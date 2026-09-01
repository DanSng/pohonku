"""
character_catalog.py — Definisi skill, equipment, dan ASSET PACK karakter.

═══════════════════════════════════════════════════════════════════════
GANTI ASSET DI SINI SAJA
═══════════════════════════════════════════════════════════════════════
Kalau kamu beli/dapat sprite sheet pixel-art baru nanti, TIDAK perlu:
  - ubah models.py
  - ubah routes/character.py
  - migrasi database

Cukup:
  1. Taruh file sprite di static/images/characters/<nama_pack>/
  2. Tambah 1 entry baru di ASSET_PACKS di bawah ini
  3. (opsional) set DEFAULT_ASSET_PACK ke nama pack baru, atau biarkan
     pemain pilih sendiri lewat menu ganti tampilan nanti

Format sprite sheet yang didukung engine (world.html):
  - Grid sederhana, tiap baris = 1 arah (down, left, right, up — urutan
    umum RPG Maker/Stardew-style), tiap kolom = 1 frame animasi jalan.
  - frame_w / frame_h dalam pixel, cols = jumlah frame per baris.
═══════════════════════════════════════════════════════════════════════
"""

DEFAULT_ASSET_PACK = "chibi_v1"

def _chibi_frames(gender):
    base = f"images/characters/chibi_v1/{gender}"
    return {
        "idle":      [f"{base}/idle_{i}.png" for i in range(7)],
        "walk_left": [f"{base}/walk_left_{i}.png" for i in range(7)],
        "walk_up":   [f"{base}/walk_up_{i}.png" for i in range(7)],
        "attack":    [f"{base}/attack_{i}.png" for i in range(5)],
        "shield":    [f"{base}/shield_{i}.png" for i in range(5)],
        "portrait":  f"{base}/portrait.png",
    }

ASSET_PACKS = {
    # ── Pack aktif sekarang — hasil potongan sprite sheet asli (chibi,
    # 2 varian gender). type='image_set': kumpulan file PNG per pose/aksi,
    # BUKAN satu spritesheet grid seragam (makanya row_map tidak dipakai
    # di sini, tapi daftar file eksplisit per kategori).
    "chibi_v1": {
        "name": "Chibi Sprite v1",
        "type": "image_set",
        "variants": {
            "female": _chibi_frames("female"),
            "male": _chibi_frames("male"),
        },
    },

    # ── Placeholder CSS — tetap disimpan sebagai fallback kalau file
    # sprite belum ter-upload di server (misal baru clone project).
    "placeholder": {
        "name": "Placeholder (CSS)",
        "type": "css",
        "frame_w": 32,
        "frame_h": 32,
    },

    # ── Contoh entry untuk pack masa depan — TINGGAL DIISI nanti kalau
    #    beli/pakai sprite sheet lain lagi. Hapus komentar & sesuaikan.
    # "pack_v2": {
    #     "name": "Nama Pack Baru",
    #     "type": "image_set",
    #     "variants": {
    #         "female": {"idle": [...], "walk_left": [...], "walk_up": [...],
    #                    "attack": [...], "shield": [...], "portrait": "..."},
    #         "male": {...},
    #     },
    # },
}

# ── Palet warna placeholder (dipakai engine CSS sebelum ada sprite asli) ─
PLACEHOLDER_COLORS = {
    "skin":   {"default": "#e8b088", "gelap": "#a86840", "terang": "#f5d0a8"},
    "hair":   {"default": "#3a2410", "pirang": "#c8a050", "merah": "#a03818"},
    "outfit": {"default": "#3d8c10", "biru": "#2a6ab0", "merah": "#b02818", "ungu": "#7040b0"},
    "hat":    {"topi_petani": "#c04030", "topi_penjelajah": "#8a6018"},
}

# ═══════════════════════════════════════════════════════════════════════
# SKILL PETUALANGAN — fondasi untuk mode hutan (fase berikutnya)
# ═══════════════════════════════════════════════════════════════════════
SKILL_CATALOG = {
    "menebang": {
        "name": "Menebang",
        "icon": "🪓",
        "desc": "Efisiensi mengambil kayu & bahan dari pohon liar di hutan",
        "max_level": 20,
    },
    "meramu": {
        "name": "Meramu",
        "icon": "🌿",
        "desc": "Kemampuan mengumpulkan herbal, buah, dan bahan ramuan",
        "max_level": 20,
    },
    "bertarung": {
        "name": "Bertarung",
        "icon": "⚔️",
        "desc": "Kekuatan menghadapi hama/monster hutan",
        "max_level": 20,
    },
    "menjinakkan": {
        "name": "Menjinakkan",
        "icon": "🐾",
        "desc": "Peluang berhasil menjinakkan hewan liar jadi peliharaan",
        "max_level": 20,
    },
}

# ═══════════════════════════════════════════════════════════════════════
# EQUIPMENT — item dari tas (InventoryItem) yang bisa di-"pakai" karakter
# item_type di InventoryItem untuk equipment adventure: 'equipment'
# ═══════════════════════════════════════════════════════════════════════
EQUIPMENT_CATALOG = {
    "kapak_kayu": {
        "name": "Kapak Kayu", "slot": "weapon", "icon": "🪓",
        "rarity": "common", "bonus_skill": "menebang", "bonus_value": 5,
    },
    "keranjang_ramu": {
        "name": "Keranjang Ramu", "slot": "tool", "icon": "🧺",
        "rarity": "common", "bonus_skill": "meramu", "bonus_value": 5,
    },
    "topi_penjelajah": {
        "name": "Topi Penjelajah", "slot": "head", "icon": "🎩",
        "rarity": "uncommon", "bonus_skill": None, "bonus_value": 0,
    },
}

EQUIPMENT_SLOTS = ["weapon", "tool", "head", "body", "bag"]

# ═══════════════════════════════════════════════════════════════════════
# DEKORASI RUMAH & LAHAN — sekarang barang SUNGGUHAN dari toko
# (catalog.SHOP_ITEMS, type='deco'), dibeli pakai DNS lewat toko yang
# sudah ada, baru bisa ditaruh di halaman kalau sudah dimiliki
# (InventoryItem item_type='deco', quantity>0). Icon & kategori di sini
# HANYA untuk kebutuhan render peta rumah — data harga/rarity aslinya
# tetap satu sumber kebenaran di catalog.SHOP_ITEMS, tidak diduplikasi.
# ═══════════════════════════════════════════════════════════════════════
DECOR_CATALOG = {
    # Lahan
    "pagar_kayu":     {"name": "Pagar Kayu",            "icon": "🪵", "category": "lahan"},
    "bangku_taman":   {"name": "Bangku Taman",          "icon": "🪑", "category": "lahan"},
    "sumur_tua":      {"name": "Sumur Tua",             "icon": "🪣", "category": "lahan"},
    "pot_bunga":      {"name": "Pot Bunga",             "icon": "🪴", "category": "lahan"},
    "batu_hias":      {"name": "Batu Hias",             "icon": "🪨", "category": "lahan"},
    "kolam_mini":     {"name": "Kolam Mini",            "icon": "💧", "category": "lahan"},
    "ayunan_kayu":    {"name": "Ayunan Kayu",           "icon": "🪢", "category": "lahan"},
    "gerbang_bambu":  {"name": "Gerbang Bambu",         "icon": "⛩️", "category": "lahan"},
    "lentera_kunang": {"name": "Lentera Kunang",        "icon": "🏮", "category": "lahan"},
    "menara_sarang":  {"name": "Menara Sarang",         "icon": "🗼", "category": "lahan"},
    "patung_garuda":  {"name": "Patung Garuda",         "icon": "🦅", "category": "lahan"},
    "altar_naga":     {"name": "Altar Naga Kuno",       "icon": "🐉", "category": "lahan"},
    # Rumah
    "keset_selamat":  {"name": "Keset Selamat Datang",  "icon": "🚪", "category": "rumah"},
    "karangan_bunga": {"name": "Karangan Bunga Pintu",  "icon": "💐", "category": "rumah"},
    "kotak_bunga":    {"name": "Kotak Bunga Jendela",   "icon": "🌷", "category": "rumah"},
    "lampion_gerbang":{"name": "Lampion Gerbang",       "icon": "🎐", "category": "rumah"},
}
