"""
routes/mining.py — Tambang Ekosistem PohonKu
=================================================
Hewan peliharaan dikirim ke zona tambang sesuai jenisnya (lihat
mining_data.py). Tier hewan menentukan tingkat bahan mistis yang bisa
didapat. Kondisi hewan (hunger/happiness) dan cuaca nyata di lokasi pohon
tempatnya ditugaskan ikut mempengaruhi peluang.

Sesi mining berjalan REAL berjam-jam (1-24 jam) — waktu mulai disimpan di
SERVER (bukan browser, anti-curang). Makin lama ditahan, makin besar
peluang dapat bahan mistis, sampai maksimal di jam ke-24. Klaim paling
cepat setelah 1 jam. 1 hewan cuma bisa 1 sesi per hari — reset tengah
malam WIB (bukan cooldown jam tetap), selaras dengan siklus reset harian
lain di game (quest harian, dst).

Saat klaim, ada pilihan risiko: "Ambil Sekarang" (aman, pakai peluang yang
sudah terkumpul) atau "Gali Lebih Dalam" (gamble ×1.5 tambahan — kalau
gagal, bahan mistis sesi ini hilang total, tapi DNS & bonus bibit aman).

Alur:
  1. GET  /mining              -> halaman utama (daftar hewan)
  2. GET  /mining/list          -> daftar hewan + status sesi (AJAX)
  3. GET  /mining/detail/<id>   -> halaman detail 1 hewan (dari tombol di halaman Hewan)
  4. POST /mining/start/<id>    -> mulai sesi (catat waktu mulai di server)
  5. POST /mining/finish/<id>   -> klaim, body: {"choice": "aman"|"dalam"}
  6. GET  /mining/inventory     -> semua bahan mistis & penemuan legendaris yang terkumpul
"""
from flask import Blueprint, render_template, request, jsonify, redirect
from flask_login import login_required, current_user
from models import db, UserAnimal, UserTree, InventoryItem, DNSSupply, DistributionWallet, _record_tx
from datetime import datetime, timedelta
import random, uuid as _uuid
import catalog as cat
from mining_data import (
    MINING_ZONES, TIER_TO_LEVEL, DNS_RANGE, LEVEL_TO_SEED_RARITIES, ALL_MATERIALS,
    BASE_MATERIAL_CHANCE, SEED_BONUS_CHANCE, LEGENDARY_CHANCE,
    MIN_SESSION_HOURS, MAX_SESSION_HOURS, MIN_SESSION_SECONDS,
    DEEP_DIG_SUCCESS_BASE, DEEP_DIG_BONUS_MULT, CRAFTING_RECIPES,
    get_zone_for_animal, time_multiplier,
)

mining_bp = Blueprint("mining", __name__)


def _is_night_wib():
    """Malam = 19:00-04:59 WIB (UTC+7). Tambang Mistis cuma buka malam hari."""
    wib_hour = ((datetime.utcnow() + timedelta(hours=7)).hour)
    return wib_hour >= 19 or wib_hour < 5


def _today_wib():
    """Tanggal hari ini menurut WIB — dipakai untuk reset harian mining."""
    return (datetime.utcnow() + timedelta(hours=7)).date()


def _last_mined_wib_date(a):
    """Tanggal (WIB) terakhir hewan ini selesai mining, atau None kalau belum pernah."""
    if not a.last_mined:
        return None
    return (a.last_mined + timedelta(hours=7)).date()


def _add_material(uid, material_key, qty=1):
    rec = InventoryItem.query.filter_by(
        user_id=uid, item_key=material_key, item_type="material"
    ).first()
    if rec:
        rec.quantity = (rec.quantity or 0) + qty
    else:
        db.session.add(InventoryItem(
            user_id=uid, item_key=material_key, item_type="material", quantity=qty
        ))


def _grant_random_seed(uid, level):
    """Kasih 1 bibit acak sesuai rarity yang cocok dengan tingkat bahan."""
    rarities = LEVEL_TO_SEED_RARITIES.get(level, ["common"])
    candidates = [k for k, v in cat.SHOP_ITEMS.items()
                  if v.get("type") == "seed" and v.get("rarity") in rarities]
    if not candidates:
        return None
    key = random.choice(candidates)
    db.session.add(InventoryItem(user_id=uid, item_key=key, item_type="seed"))
    item = cat.SHOP_ITEMS[key]
    return {"key": key, "name": item.get("name"), "rarity": item.get("rarity")}


def _grant_legendary_find(uid, zone, animal):
    """Penemuan langka spesial — cuma untuk hewan legendary ke atas, 0.1% peluang."""
    find_id = _uuid.uuid4().hex[:8]
    name = f"Penemuan {zone['label']} #{find_id}"
    db.session.add(InventoryItem(
        user_id=uid, item_key=f"legendary_find_{find_id}",
        item_type="legendary_find", quantity=1
    ))
    bonus_dns = round(random.uniform(500, 2000), 2)
    return {"name": name, "bonus_dns": bonus_dns, "from_animal": animal.display_name}


def _give_dns_mining(user, amount):
    """Beri DNS dari gameplay_reward pool — pola sama seperti tree.py/proximity.py."""
    if amount <= 0 or not user.wallet:
        return 0
    gp = DistributionWallet.query.filter_by(wallet_key="gameplay_reward").first()
    if not gp or gp.balance < amount:
        return 0
    gp.balance   -= amount
    gp.disbursed  = (gp.disbursed or 0) + amount
    user.wallet.balance      += amount
    user.wallet.total_earned += amount
    s = DNSSupply.query.first()
    if s:
        s.circulating = (s.circulating or 0) + amount
        s.locked      = max(0, (s.locked or 0) - amount)
    _record_tx("GAMEPLAY_POOL", user.wallet.address, amount, "mining", "Hasil tambang hewan")
    return amount


@mining_bp.route("/mining")
@login_required
def index():
    return render_template("mining.html")


@mining_bp.route("/mining/detail/<int:animal_id>")
@login_required
def detail(animal_id):
    """Halaman detail mining untuk SATU hewan spesifik — dibuka dari tombol
    'Tambang' di sebelah nama hewan pada halaman Hewan."""
    a = UserAnimal.query.filter_by(id=animal_id, user_id=current_user.id).first()
    if not a:
        return redirect("/animal")

    zone = get_zone_for_animal(a.animal_key)
    animal_data = cat.ANIMAL_CATALOG.get(a.animal_key, {})
    animal_tier = animal_data.get("tier", "common")
    level       = TIER_TO_LEVEL.get(animal_tier, "umum")
    ts = cat.get_rarity_style(animal_tier)
    ti = cat.get_tier_info(animal_tier)

    dns_lo, dns_hi = DNS_RANGE.get(animal_tier, (10, 20))
    condition_factor = max(0.2, min(1.0, ((a.hunger or 0) + (a.happiness or 0)) / 200.0))
    base_chance_pct     = round(min(0.95, BASE_MATERIAL_CHANCE * condition_factor) * 100, 1)
    max_chance_pct      = round(min(0.95, BASE_MATERIAL_CHANCE * condition_factor * 3) * 100, 1)
    deep_max_chance_pct = round(min(0.95, BASE_MATERIAL_CHANCE * condition_factor * 3 * DEEP_DIG_BONUS_MULT) * 100, 1)

    mined_today = (_last_mined_wib_date(a) == _today_wib())
    session_elapsed = None
    if a.mining_session_start:
        session_elapsed = round((datetime.utcnow() - a.mining_session_start).total_seconds(), 1)

    return render_template("mining_detail.html",
        a=a, zone=zone, animal_tier=animal_tier, level=level, ts=ts, ti=ti,
        dns_lo=dns_lo, dns_hi=dns_hi,
        base_chance_pct=base_chance_pct, max_chance_pct=max_chance_pct,
        deep_max_chance_pct=deep_max_chance_pct,
        can_mine=bool(zone) and not mined_today and session_elapsed is None,
        session_active=session_elapsed is not None,
        session_elapsed=session_elapsed,
        session_mode=a.mining_mode,
        session_ready=(session_elapsed is not None and session_elapsed >= MIN_SESSION_SECONDS),
        mined_today=mined_today,
        is_legendary_eligible=animal_tier in ("legendary", "mythic", "divine"),
        seed_rarities=LEVEL_TO_SEED_RARITIES.get(level, []),
        is_night=_is_night_wib(),
        min_session_hours=MIN_SESSION_HOURS,
        max_session_hours=MAX_SESSION_HOURS,
        min_session_seconds=MIN_SESSION_SECONDS,
    )


@mining_bp.route("/mining/list")
@login_required
def list_animals():
    animals = current_user.animals.filter_by(is_active=True).all()
    now = datetime.utcnow()
    today_wib = _today_wib()
    rows = []
    for a in animals:
        zone = get_zone_for_animal(a.animal_key)
        ac = cat.ANIMAL_CATALOG.get(a.animal_key, {})
        session_elapsed = None
        if a.mining_session_start:
            session_elapsed = (now - a.mining_session_start).total_seconds()
        mined_today = (_last_mined_wib_date(a) == today_wib)
        rows.append({
            "id": a.id,
            "name": a.display_name,
            "animal_key": a.animal_key,
            "emoji": ac.get("emoji", "🐾"),
            "tier": ac.get("tier", "common"),
            "zone_label": zone["label"] if zone else None,
            "zone_emoji": zone["emoji"] if zone else None,
            "hunger": a.hunger,
            "happiness": a.happiness,
            "mined_today": mined_today,
            "can_mine": bool(zone) and not mined_today and session_elapsed is None,
            "session_active": session_elapsed is not None,
            "session_mode": a.mining_mode,
            "session_elapsed": round(session_elapsed, 1) if session_elapsed is not None else None,
            "session_ready": session_elapsed is not None and session_elapsed >= MIN_SESSION_SECONDS,
        })
    return jsonify({"ok": True, "animals": rows})


@mining_bp.route("/mining/start/<int:animal_id>", methods=["POST"])
@login_required
def start(animal_id):
    """Mulai sesi mining. body: {"choice": "aman"|"dalam"} — WAJIB dipilih
    dulu SEBELUM timer mulai jalan, dan dikunci di database untuk sesi ini
    (tidak bisa diubah lagi setelah dimulai). Kalau sesi sudah aktif,
    kembalikan mode yang sudah terkunci (idempotent — refresh halaman tidak
    reset progress atau ganti pilihan)."""
    data   = request.json or {}
    choice = data.get("choice", "aman")
    if choice not in ("aman", "dalam"):
        choice = "aman"

    a = UserAnimal.query.filter_by(id=animal_id, user_id=current_user.id).first()
    if not a:
        return jsonify({"ok": False, "msg": "Hewan tidak ditemukan"}), 404

    zone = get_zone_for_animal(a.animal_key)
    if not zone:
        return jsonify({"ok": False, "msg": f"{a.display_name} belum bisa ditambang"})

    if not a.mining_session_start:
        if _last_mined_wib_date(a) == _today_wib():
            return jsonify({"ok": False, "msg": f"{a.display_name} sudah menambang hari ini — coba lagi setelah reset tengah malam WIB"})
        if zone["key"] == "mistis" and not _is_night_wib():
            return jsonify({"ok": False, "msg": "Tambang Mistis cuma bisa diakses malam hari (WIB)"})
        a.mining_session_start = datetime.utcnow()
        a.mining_mode = choice
        db.session.commit()

    return jsonify({
        "ok": True,
        "zone_label": zone["label"],
        "zone_emoji": zone["emoji"],
        "animal_emoji": cat.ANIMAL_CATALOG.get(a.animal_key, {}).get("emoji", "🐾"),
        "mode": a.mining_mode,
        "session_elapsed": round((datetime.utcnow() - a.mining_session_start).total_seconds(), 1),
        "min_session_seconds": MIN_SESSION_SECONDS,
    })


@mining_bp.route("/mining/finish/<int:animal_id>", methods=["POST"])
@login_required
def finish(animal_id):
    """Klaim sesi mining yang sedang berjalan. Mode (aman/dalam) SUDAH
    dikunci sejak /mining/start dipanggil — tidak ada pilihan lagi di sini.
    - aman:  pakai peluang yang sudah terkumpul dari lama sesi (aman)
    - dalam: gamble ×1.5 tambahan — kalau gagal, bahan mistis sesi ini
             hilang total (DNS & bonus bibit tetap aman)."""
    a = UserAnimal.query.filter_by(id=animal_id, user_id=current_user.id).first()
    if not a:
        return jsonify({"ok": False, "msg": "Hewan tidak ditemukan"}), 404
    if not a.mining_session_start:
        return jsonify({"ok": False, "msg": "Tidak ada sesi mining yang sedang berjalan"})

    choice = a.mining_mode or "aman"

    zone = get_zone_for_animal(a.animal_key)
    if not zone:
        return jsonify({"ok": False, "msg": f"{a.display_name} belum bisa ditambang"})

    elapsed_seconds = (datetime.utcnow() - a.mining_session_start).total_seconds()
    if elapsed_seconds < MIN_SESSION_SECONDS:
        remain_min = int((MIN_SESSION_SECONDS - elapsed_seconds) / 60) + 1
        return jsonify({"ok": False, "msg": f"Belum genap {MIN_SESSION_HOURS} jam — tunggu {remain_min} menit lagi"})

    animal_data  = cat.ANIMAL_CATALOG.get(a.animal_key, {})
    animal_tier  = animal_data.get("tier", "common")
    level        = TIER_TO_LEVEL.get(animal_tier, "umum")

    # Kondisi hewan (hunger + happiness) -> faktor 0.2 - 1.0
    condition_factor = max(0.2, min(1.0, ((a.hunger or 0) + (a.happiness or 0)) / 200.0))

    # Modifier cuaca nyata dari pohon tempat hewan ditugaskan (kalau ada)
    zone_modifier = 1.0
    if a.tree_id:
        tree = UserTree.query.get(a.tree_id)
        weather_cond = tree.weather_condition if tree else None
        if zone["key"] == "laut" and weather_cond == "rain":
            zone_modifier = 2.0
        elif zone["key"] == "langit" and weather_cond != "rain":
            zone_modifier = 1.5

    # ── Multiplier dari lama sesi berjalan (1x di awal, 3x di jam ke-24) ──
    t_mult = time_multiplier(elapsed_seconds)

    # ── DNS — selalu didapat, tidak terpengaruh pilihan gali-dalam ───────
    lo, hi = DNS_RANGE.get(animal_tier, (10, 20))
    dns_amount = round(random.uniform(lo, hi), 2)

    # ── Pilihan "gali lebih dalam" saat klaim ─────────────────────────────
    dig_result    = None
    material_mult = t_mult
    if choice == "dalam":
        success_chance = DEEP_DIG_SUCCESS_BASE + condition_factor * 0.2  # 50%-70%
        if random.random() < success_chance:
            material_mult = t_mult * DEEP_DIG_BONUS_MULT
            dig_result = "berhasil"
        else:
            material_mult = 0  # bahan mistis sesi ini hilang total (DNS tetap aman)
            dig_result = "gagal"

    # ── Bahan mistis ─────────────────────────────────────────────────
    material_chance = min(0.95, BASE_MATERIAL_CHANCE * condition_factor * zone_modifier * material_mult)
    material_found  = None
    if material_mult > 0 and random.random() < material_chance:
        mat = zone["materials"][level]
        _add_material(current_user.id, mat["key"])
        material_found = mat

    # ── Bonus bibit rare — tidak ikut dipertaruhkan di gali-dalam ────────
    seed_found = None
    if random.random() < min(0.9, SEED_BONUS_CHANCE * condition_factor * t_mult):
        seed_found = _grant_random_seed(current_user.id, level)

    # ── Penemuan Legendaris (jackpot, cuma hewan legendary+) ──────────
    legendary_find = None
    if animal_tier in ("legendary", "mythic", "divine") and random.random() < LEGENDARY_CHANCE:
        legendary_find = _grant_legendary_find(current_user.id, zone, a)
        dns_amount += legendary_find["bonus_dns"]

    dns_given = _give_dns_mining(current_user, dns_amount)

    a.last_mined = datetime.utcnow()
    a.mining_session_start = None
    a.mining_mode = None
    db.session.commit()

    return jsonify({
        "ok": True,
        "zone_label": zone["label"],
        "zone_emoji": zone["emoji"],
        "animal_name": a.display_name,
        "session_hours": round(elapsed_seconds / 3600, 2),
        "time_multiplier": round(t_mult, 2),
        "dig_choice": choice,
        "dig_result": dig_result,
        "dns": dns_given,
        "material": material_found,
        "seed": seed_found,
        "legendary": legendary_find,
        "weather_bonus": zone_modifier > 1.0,
        "new_balance": current_user.dns_balance,
    })


@mining_bp.route("/mining/inventory")
@login_required
def inventory():
    """Semua bahan mistis & Penemuan Legendaris hasil mining, plus status
    resep crafting (bahan yang dimiliki vs dibutuhkan tiap resep)."""
    material_rows = InventoryItem.query.filter_by(
        user_id=current_user.id, item_type="material"
    ).all()
    legendary_rows = InventoryItem.query.filter_by(
        user_id=current_user.id, item_type="legendary_find"
    ).order_by(InventoryItem.acquired_at.desc()).all()

    owned = {m.item_key: (m.quantity or 0) for m in material_rows}

    materials = []
    for m in material_rows:
        info = ALL_MATERIALS.get(m.item_key)
        if info:
            row = dict(info)
            row["quantity"] = m.quantity
            materials.append(row)

    level_order = {"sangat_langka": 0, "langka": 1, "umum": 2}
    materials.sort(key=lambda x: (level_order.get(x["level"], 9), x["zone_label"]))

    # Status tiap resep crafting
    recipes = []
    for item_key, recipe in CRAFTING_RECIPES.items():
        shop_item = cat.SHOP_ITEMS.get(item_key, {})
        need_rows = []
        can_craft = True
        for mat_key, qty_needed in recipe["materials"].items():
            info = ALL_MATERIALS.get(mat_key, {})
            have = owned.get(mat_key, 0)
            if have < qty_needed:
                can_craft = False
            need_rows.append({
                "key": mat_key, "name": info.get("name", mat_key),
                "emoji": info.get("emoji", "❓"),
                "have": have, "need": qty_needed,
            })
        if current_user.dns_balance < recipe["dns_cost"]:
            can_craft = False
        recipes.append({
            "item_key": item_key,
            "name": shop_item.get("name", item_key),
            "type": shop_item.get("type", "amulet"),
            "rarity": shop_item.get("rarity", "common"),
            "desc": shop_item.get("desc", ""),
            "shop_price": shop_item.get("price", 0),
            "dns_cost": recipe["dns_cost"],
            "materials": need_rows,
            "can_craft": can_craft,
        })
    rarity_order = {"rare": 0, "epic": 1, "legendary": 2, "mythic": 3, "divine": 4}
    recipes.sort(key=lambda x: rarity_order.get(x["rarity"], 9))

    return render_template("mining_inventory.html",
        materials=materials, legendary_finds=legendary_rows, recipes=recipes)


@mining_bp.route("/mining/craft/<item_key>", methods=["POST"])
@login_required
def craft(item_key):
    """Rakit item amulet/deco dari bahan mistis + DNS. Item hasil masuk
    InventoryItem persis seperti kalau dibeli dari toko."""
    recipe = CRAFTING_RECIPES.get(item_key)
    if not recipe:
        return jsonify({"ok": False, "msg": "Resep tidak ditemukan"}), 404

    shop_item = cat.SHOP_ITEMS.get(item_key)
    if not shop_item:
        return jsonify({"ok": False, "msg": "Item tidak ditemukan di katalog"}), 404

    # Cek semua bahan cukup
    owned_rows = {}
    for mat_key in recipe["materials"]:
        rec = InventoryItem.query.filter_by(
            user_id=current_user.id, item_key=mat_key, item_type="material"
        ).first()
        owned_rows[mat_key] = rec
        have = rec.quantity if rec else 0
        if have < recipe["materials"][mat_key]:
            info = ALL_MATERIALS.get(mat_key, {})
            return jsonify({"ok": False, "msg": f"Bahan {info.get('name', mat_key)} kurang"})

    if current_user.dns_balance < recipe["dns_cost"]:
        return jsonify({"ok": False, "msg": f"DNS tidak cukup — butuh {recipe['dns_cost']} DNS"})

    # Potong bahan
    for mat_key, qty_needed in recipe["materials"].items():
        rec = owned_rows[mat_key]
        rec.quantity -= qty_needed
        if rec.quantity <= 0:
            db.session.delete(rec)

    # Potong DNS (langsung dari wallet — bukan gameplay pool, ini "biaya" bukan reward)
    current_user.wallet.balance -= recipe["dns_cost"]
    current_user.wallet.total_spent += recipe["dns_cost"]
    _record_tx(current_user.wallet.address, "BURN", recipe["dns_cost"], "burn", f"Crafting {shop_item['name']}")

    # Beri item hasil craft
    db.session.add(InventoryItem(
        user_id=current_user.id, item_key=item_key,
        item_type=shop_item.get("type", "amulet")
    ))
    db.session.commit()

    return jsonify({
        "ok": True,
        "item_name": shop_item["name"],
        "new_balance": current_user.dns_balance,
    })
