"""
mining_data.py — Konfigurasi Tambang Ekosistem PohonKu
=========================================================
Sengaja dipisah dari catalog.py (bukan diedit langsung) supaya aman —
tidak menyentuh data pohon/hewan/toko yang sudah ada.

Prinsip: tiap hewan dipetakan ke SATU zona tambang sesuai habitat/karakter
aslinya (lihat ANIMAL_CATALOG di catalog.py). Tier hewan (common..divine)
menentukan TINGKAT bahan mistis yang bisa didapat di zona itu — bukan cuma
angka lebih besar, tapi item yang benar-benar beda & lebih prestisius.
"""

# ─── ZONA TAMBANG ──────────────────────────────────────────────────────
# materials: 3 tingkat per zona — umum (dari hewan common/uncommon),
# langka (dari rare/epic), sangat_langka (dari legendary/mythic/divine).
MINING_ZONES = {
    "akar": {
        "label": "Tambang Akar",
        "emoji": "🌱",
        "desc": "Hewan darat/penggali mencari mineral dekat akar pohon",
        "animals": ["tupai_emas", "rusa_sambar"],
        "materials": {
            "umum":          {"key": "akar_rapuh", "name": "Akar Rapuh", "emoji": "🥔"},
            "langka":        {"key": "akar_emas",  "name": "Akar Emas",  "emoji": "💛"},
            "sangat_langka": {"key": "akar_purba", "name": "Akar Purba", "emoji": "🌟"},
        },
    },
    "kanopi": {
        "label": "Tambang Kanopi",
        "emoji": "🌳",
        "desc": "Primata pemanjat forage getah/resin di tajuk pohon tinggi",
        "animals": ["kera_ekor_panjang", "orangutan"],
        "materials": {
            "umum":          {"key": "getah_biasa", "name": "Getah Biasa", "emoji": "🟤"},
            "langka":        {"key": "getah_suci",  "name": "Getah Suci",  "emoji": "🟢"},
            "sangat_langka": {"key": "getah_abadi", "name": "Getah Abadi", "emoji": "✨"},
        },
    },
    "langit": {
        "label": "Tambang Langit",
        "emoji": "☁️",
        "desc": "Unggas & makhluk terbang kumpulkan kristal dari ketinggian",
        "animals": ["burung_pipit", "elang_brontok", "cendrawasih", "rajawali_jawa",
                    "fenghuang", "pegasus", "griffin"],
        "materials": {
            "umum":          {"key": "bulu_awan",  "name": "Bulu Awan",  "emoji": "☁️"},
            "langka":        {"key": "bulu_cahaya","name": "Bulu Cahaya","emoji": "💫"},
            "sangat_langka": {"key": "bulu_fajar", "name": "Bulu Fajar", "emoji": "🌅"},
        },
    },
    "rimba": {
        "label": "Tambang Rimba Dalam",
        "emoji": "🐅",
        "desc": "Predator berburu bijih & batu di zona rimba berbahaya",
        "animals": ["harimau_sumatra", "komodo"],
        "materials": {
            "umum":          {"key": "taring_rimba",  "name": "Taring Rimba",   "emoji": "🦷"},
            "langka":        {"key": "taring_purba",  "name": "Taring Purba",   "emoji": "🦴"},
            "sangat_langka": {"key": "taring_legenda","name": "Taring Legenda", "emoji": "⚔️"},
        },
    },
    "laut": {
        "label": "Tambang Laut Dalam",
        "emoji": "🌊",
        "desc": "Naga & ular air menyelam mencari mutiara & harta laut",
        "animals": ["long_wang", "hydra", "leviathan", "jormungandr"],
        "materials": {
            "umum":          {"key": "kerang_laut",  "name": "Kerang Laut",  "emoji": "🐚"},
            "langka":        {"key": "mutiara_abadi","name": "Mutiara Abadi","emoji": "🔮"},
            "sangat_langka": {"key": "mutiara_naga", "name": "Mutiara Naga", "emoji": "🐉"},
        },
    },
    "mistis": {
        "label": "Tambang Mistis",
        "emoji": "✨",
        "desc": "Makhluk spiritual — cuma bisa ditambang malam hari (WIB)",
        "animals": ["qilin", "fenrir"],
        "materials": {
            "umum":          {"key": "serpih_spiritual","name": "Serpih Spiritual","emoji": "🔹"},
            "langka":        {"key": "inti_spiritual",  "name": "Inti Spiritual",  "emoji": "💠"},
            "sangat_langka": {"key": "jiwa_murni",       "name": "Jiwa Murni",      "emoji": "🌟"},
        },
    },
}

# Bangun otomatis: animal_key -> zone_key
ANIMAL_TO_ZONE = {}
for _zk, _z in MINING_ZONES.items():
    for _ak in _z["animals"]:
        ANIMAL_TO_ZONE[_ak] = _zk

# Bangun otomatis: material_key -> info lengkap (dipakai halaman Inventori)
ALL_MATERIALS = {}
for _zk, _z in MINING_ZONES.items():
    for _lvl, _mat in _z["materials"].items():
        ALL_MATERIALS[_mat["key"]] = {
            "key": _mat["key"], "name": _mat["name"], "emoji": _mat["emoji"],
            "zone_key": _zk, "zone_label": _z["label"], "zone_emoji": _z["emoji"],
            "level": _lvl,
        }

# Tier hewan (dari ANIMAL_CATALOG) -> tingkat bahan mistis
TIER_TO_LEVEL = {
    "common": "umum", "uncommon": "umum",
    "rare": "langka", "epic": "langka",
    "legendary": "sangat_langka", "mythic": "sangat_langka", "divine": "sangat_langka",
}

# Rentang DNS per tier hewan (min, max) — hasil pasti tiap sesi mining
DNS_RANGE = {
    "common":    (10, 20),
    "uncommon":  (20, 40),
    "rare":      (40, 80),
    "epic":      (80, 150),
    "legendary": (150, 300),
    "mythic":    (300, 600),
    "divine":    (600, 1200),
}

# Rarity bibit yang bisa didapat sebagai bonus, per tingkat bahan
LEVEL_TO_SEED_RARITIES = {
    "umum":          ["common"],
    "langka":        ["uncommon", "rare"],
    "sangat_langka": ["epic", "legendary", "mythic"],
}

# ─── Parameter ekonomi mining ───────────────────────────────────────────
BASE_MATERIAL_CHANCE = 0.30   # peluang dasar dapat bahan mistis (sebelum modifier)
SEED_BONUS_CHANCE     = 0.06   # peluang dasar dapat bonus bibit
LEGENDARY_CHANCE      = 0.001  # 0.1% — cuma untuk hewan legendary ke atas

# Sesi mining berjalan REAL berjam-jam — minimal 1 jam sebelum bisa diklaim,
# peluang naik terus sampai maksimal di jam ke-24, lalu mentok. 1 hewan
# cuma bisa 1 sesi per hari (reset tengah malam WIB), bukan cooldown jam
# tetap — supaya selaras dengan siklus reset harian yang sudah ada di game
# (quest harian, dll).
MIN_SESSION_HOURS   = 1
MAX_SESSION_HOURS   = 24
MIN_SESSION_SECONDS = MIN_SESSION_HOURS * 3600
TIME_RAMP_SECONDS   = MAX_SESSION_HOURS * 3600
MAX_TIME_MULTIPLIER = 3.0

# Pilihan "gali lebih dalam" saat klaim — gamble tambahan DI ATAS peluang
# yang sudah terkumpul dari waktu. Kalau gagal, bahan mistis sesi ini
# hilang total (DNS & bonus bibit tetap aman, cuma bahan yang dipertaruhkan).
DEEP_DIG_SUCCESS_BASE = 0.5   # 50%-70% tergantung kondisi hewan
DEEP_DIG_BONUS_MULT   = 1.5   # multiplier tambahan kalau berhasil


def time_multiplier(elapsed_seconds):
    """Multiplier peluang berdasarkan berapa lama sesi mining sudah berjalan.
    Naik linear dari 1.0x sampai MAX_TIME_MULTIPLIER dalam TIME_RAMP_SECONDS
    (24 jam), lalu mentok (plateau) — tidak ada gunanya menahan lebih lama."""
    frac = min(1.0, max(0.0, elapsed_seconds) / TIME_RAMP_SECONDS)
    return 1.0 + frac * (MAX_TIME_MULTIPLIER - 1.0)


# ─── RESEP CRAFTING ──────────────────────────────────────────────────────
# Merakit item amulet/deco (dari SHOP_ITEMS di catalog.py) pakai bahan
# mistis hasil mining + sebagian DNS — jalur alternatif selain beli
# langsung pakai DNS penuh. Item hasil craft masuk InventoryItem persis
# seperti kalau dibeli dari toko (item_key & item_type sama), jadi otomatis
# kompatibel dengan sistem yang sudah menangani amulet/deco pembelian.
CRAFTING_RECIPES = {
    "lentera_kunang": {   # deco rare — normal beli 600 DNS
        "materials": {"bulu_awan": 3, "getah_biasa": 2},
        "dns_cost": 200,
    },
    "perisai_rimbara": {  # amulet rare — normal beli 900 DNS
        "materials": {"taring_rimba": 4},
        "dns_cost": 250,
    },
    "kristal_waktu": {    # amulet epic — normal beli 1800 DNS
        "materials": {"akar_emas": 2, "getah_suci": 2},
        "dns_cost": 600,
    },
    "menara_sarang": {    # deco epic — normal beli 2800 DNS
        "materials": {"bulu_cahaya": 2, "getah_suci": 3},
        "dns_cost": 900,
    },
    "patung_garuda": {    # deco legendary — normal beli 15000 DNS
        "materials": {"bulu_fajar": 3, "taring_purba": 2},
        "dns_cost": 4000,
    },
    "batu_nasib": {       # amulet legendary — normal beli 5000 DNS
        "materials": {"akar_purba": 2, "mutiara_abadi": 2, "inti_spiritual": 1},
        "dns_cost": 1500,
    },
    "altar_naga": {       # deco mythic — normal beli 50000 DNS
        "materials": {"mutiara_naga": 3, "jiwa_murni": 1},
        "dns_cost": 15000,
    },
    "mahkota_ilahi": {    # amulet divine — normal beli 200000 DNS
        # Butuh 1 dari SETIAP bahan "sangat langka" di 6 zona — tujuan
        # jangka panjang yang menyatukan semua zona tambang.
        "materials": {
            "akar_purba": 1, "getah_abadi": 1, "bulu_fajar": 1,
            "taring_legenda": 1, "mutiara_naga": 1, "jiwa_murni": 1,
        },
        "dns_cost": 60000,
    },
}


def get_zone_for_animal(animal_key):
    """Return dict zona (bukan cuma key) untuk animal_key, atau None kalau
    hewan ini belum dipetakan ke zona manapun."""
    zk = ANIMAL_TO_ZONE.get(animal_key)
    if not zk:
        return None
    z = dict(MINING_ZONES[zk])
    z["key"] = zk
    return z
