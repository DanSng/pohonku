"""
forest_catalog.py — Aturan mode petualangan hutan.

Sengaja dipisah dari catalog.py (tidak diedit langsung) — sama seperti
mining_data.py, supaya tidak menyentuh data pohon/hewan/toko yang sudah
ada dan battle-tested. File ini HANYA mengonsumsi data dari catalog.py
dan mining_data.py, tidak mendefinisikan hewan/material baru.
"""

FOREST_W, FOREST_H = 14, 14
FOREST_SPAWN = (7, 7)          # titik masuk karakter ke hutan
FOREST_NODE_COUNT = 14

STAMINA_COST_MOVE     = 1
STAMINA_COST_INTERACT = 3

# Peluang tiap tipe titik sumber daya muncul (harus total <= 1.0)
NODE_TYPE_WEIGHTS = {"tree": 0.40, "herb": 0.35, "animal": 0.25}

# Bobot kemunculan hewan liar berdasarkan tier — makin tinggi tier, makin
# jarang ditemui di hutan (konsisten dengan filosofi rarity yang sudah ada)
ANIMAL_TIER_WEIGHTS = {
    "common": 50, "uncommon": 25, "rare": 15,
    "epic": 7, "legendary": 2, "mythic": 0.9, "divine": 0.1,
}

# Material "umum" (1 per zona tambang) yang bisa didapat dari forage biasa
# di hutan — BUKAN dari sesi mining hewan peliharaan (itu tetap terpisah,
# lihat mining_data.py). Forage di sini cuma level 'umum', supaya sesi
# mining hewan peliharaan tetap jadi cara utama dapat material langka.
FORAGE_MATERIAL_KEYS = [
    "akar_rapuh", "getah_biasa", "bulu_awan",
    "taring_rimba", "kerang_laut", "serpih_spiritual",
]

# Kayu (User.wood) hasil menebang — rentang acak per keberhasilan
CHOP_WOOD_MIN, CHOP_WOOD_MAX = 3, 8

# DNS hasil melawan hewan liar (bukan menjinakkan) — kecil, disengaja,
# ini bukan pengganti sistem mining hewan peliharaan yang sudah ada
FIGHT_DNS_BY_TIER = {
    "common": (5, 10), "uncommon": (8, 15), "rare": (15, 25),
    "epic": (25, 40), "legendary": (40, 70), "mythic": (70, 120), "divine": (120, 200),
}

SKILL_XP = {"chop": 15, "forage": 15, "fight": 20, "tame_success": 35, "tame_fail": 10}


def base_success_chance(action, skill_level):
    """Peluang sukses dasar berdasarkan level skill terkait. Level 1 = baru mulai."""
    table = {
        "chop":   (60, 2, 95),   # (base%, per-level%, cap%)
        "forage": (60, 2, 95),
        "fight":  (55, 2, 90),
        "tame":   (25, 3, 75),   # menjinakkan sengaja lebih sulit
    }
    base, per_level, cap = table[action]
    return min(cap, base + (skill_level - 1) * per_level) / 100.0


def pick_wild_animal(rng):
    """Pilih 1 animal_key dari ANIMAL_CATALOG, dibobotkan oleh tier."""
    from catalog import ANIMAL_CATALOG
    pool = [(key, ANIMAL_TIER_WEIGHTS.get(info["tier"], 1))
            for key, info in ANIMAL_CATALOG.items()]
    total = sum(w for _, w in pool)
    r = rng.uniform(0, total)
    upto = 0
    for key, w in pool:
        upto += w
        if r <= upto:
            return key
    return pool[-1][0]


def generate_forest_nodes(user_id):
    """
    Layout titik sumber daya — DETERMINISTIK per (user, tanggal hari ini).
    Sama sepanjang hari untuk pemain yang sama, beda tiap hari & tiap
    pemain. Tidak disimpan ke DB (dihitung ulang tiap request) — cukup
    murah karena cuma 14 titik, dan otomatis "reset" tiap hari tanpa
    perlu job terjadwal.
    """
    import random
    from datetime import date as date_cls
    rng = random.Random(f"{user_id}-{date_cls.today().isoformat()}")

    nodes = []
    used = {FOREST_SPAWN}
    attempts = 0
    while len(nodes) < FOREST_NODE_COUNT and attempts < 300:
        attempts += 1
        x, y = rng.randint(0, FOREST_W - 1), rng.randint(0, FOREST_H - 1)
        if (x, y) in used:
            continue
        used.add((x, y))

        roll = rng.random()
        if roll < NODE_TYPE_WEIGHTS["tree"]:
            ntype = "tree"
        elif roll < NODE_TYPE_WEIGHTS["tree"] + NODE_TYPE_WEIGHTS["herb"]:
            ntype = "herb"
        else:
            ntype = "animal"

        node = {"id": f"{x}_{y}", "x": x, "y": y, "type": ntype}
        if ntype == "animal":
            node["animal_key"] = pick_wild_animal(rng)
        nodes.append(node)
    return nodes
