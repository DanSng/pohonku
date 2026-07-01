# ═══════════════════════════════════════════════════════════
#  POHONKU v3 — KATALOG RESMI (sesuai White Paper v2.0)
#  DNS = satu-satunya mata uang
# ═══════════════════════════════════════════════════════════

TREE_TIERS = {
    "common":    {"label":"Common",    "emoji":"🌱","color":"#7dc840","border":"#97C459","unlock":1,  "dns_mult":1.0},
    "uncommon":  {"label":"Uncommon",  "emoji":"🍀","color":"#40c878","border":"#40C878","unlock":5,  "dns_mult":1.5},
    "rare":      {"label":"Rare",      "emoji":"🔵","color":"#60a8e0","border":"#85B7EB","unlock":15, "dns_mult":2.5},
    "epic":      {"label":"Epic",      "emoji":"🟣","color":"#c080ff","border":"#AFA9EC","unlock":30, "dns_mult":4.0},
    "legendary": {"label":"Legendary", "emoji":"🟠","color":"#f0b030","border":"#EF9F27","unlock":50, "dns_mult":7.0},
    "mythic":    {"label":"Mythic",    "emoji":"🔴","color":"#ff5040","border":"#FF5040","unlock":75, "dns_mult":12.0},
    "divine":    {"label":"Divine",    "emoji":"🟡","color":"#ffe080","border":"#FFE020","unlock":99, "dns_mult":20.0},
}

TREE_CATALOG = {
    # ══ COMMON ══
    "mahoni":   {"id":"mahoni","name":"Mahoni","latin":"Swietenia mahagoni","tier":"common",
                 "dns_per_jam":10,"grow_days":3,"panen_dns":100,"wood":4,"water_need":2,"pupuk_need":1,
                 "seed_price":50,"max_stage":4,"xp_per_stage":[80,200,500,1000],
                 "image":"trees/MAHONI.png","desc":"Pohon teduh populer. Tumbuh cepat dan mudah dirawat.",
                 "bonuses":["Pertumbuhan sangat cepat","Biaya tanam murah","Produksi DNS aktif"],
                 "animals":["tupai_emas","burung_pipit"]},
    "akasia":   {"id":"akasia","name":"Akasia","latin":"Acacia mangium","tier":"common",
                 "dns_per_jam":12,"grow_days":3,"panen_dns":150,"wood":5,"water_need":2,"pupuk_need":1,
                 "seed_price":60,"max_stage":4,"xp_per_stage":[80,200,500,1000],
                 "image":"trees/akasia_3.png",
                 "image_stages":["trees/akasia/bibit.png","trees/akasia/semai.png","trees/akasia/remaja.png","trees/akasia/dewasa.png"],"desc":"Pohon industri andalan. Tumbuh cepat di berbagai tanah.",
                 "bonuses":["Pertumbuhan cepat","Biaya murah","DNS aktif"],
                 "animals":["tupai_emas","burung_pipit"]},
    "trembesi": {"id":"trembesi","name":"Trembesi","latin":"Samanea saman","tier":"common",
                 "dns_per_jam":15,"grow_days":4,"panen_dns":200,"wood":6,"water_need":2,"pupuk_need":1,
                 "seed_price":80,"max_stage":4,"xp_per_stage":[100,250,600,1200],
                 "image":"trees/TREMBESI.png","desc":"Pohon peneduh raksasa. Kanopi lebar, ikon taman kota.",
                 "bonuses":["Kanopi terlebar","DNS aktif","Pengunjung bertambah"],
                 "animals":["tupai_emas","kera_ekor_panjang"]},
    # ══ UNCOMMON ══
    "rambutan": {"id":"rambutan","name":"Rambutan","latin":"Nephelium lappaceum","tier":"uncommon",
                 "dns_per_jam":18,"grow_days":5,"panen_dns":300,"wood":5,"water_need":3,"pupuk_need":1,
                 "seed_price":250,"max_stage":4,"xp_per_stage":[150,380,850,1700],
                 "image":"trees/RAMBUTAN.png","desc":"Pohon buah tropis yang disukai banyak hewan.",
                 "bonuses":["Produksi buah tinggi","DNS meningkat","Hewan lebih sering datang"],
                 "animals":["tupai_emas","kera_ekor_panjang","rusa_sambar"]},
    "mangga":   {"id":"mangga","name":"Mangga","latin":"Mangifera indica","tier":"uncommon",
                 "dns_per_jam":20,"grow_days":4,"panen_dns":300,"wood":5,"water_need":3,"pupuk_need":2,
                 "seed_price":280,"max_stage":4,"xp_per_stage":[150,380,850,1700],
                 "image":"trees/MANGGA.png","desc":"Raja buah tropis. Mengundang lebih banyak pengunjung.",
                 "bonuses":["Buah disukai hewan","DNS meningkat","Pengunjung bertambah"],
                 "animals":["kera_ekor_panjang","elang_brontok","rusa_sambar"]},
    "nangka":   {"id":"nangka","name":"Nangka","latin":"Artocarpus heterophyllus","tier":"uncommon",
                 "dns_per_jam":22,"grow_days":5,"panen_dns":350,"wood":6,"water_need":3,"pupuk_need":2,
                 "seed_price":300,"max_stage":4,"xp_per_stage":[160,400,900,1800],
                 "image":"trees/NANGKA.png","desc":"Buah terbesar. Favorit orangutan hutan.",
                 "bonuses":["Buah berlimpah","DNS meningkat","Orangutan tertarik"],
                 "animals":["kera_ekor_panjang","orangutan","rusa_sambar"]},
    # ══ RARE ══
    "sonokeling":{"id":"sonokeling","name":"Sonokeling","latin":"Dalbergia latifolia","tier":"rare",
                 "dns_per_jam":28,"grow_days":7,"panen_dns":600,"wood":16,"water_need":4,"pupuk_need":2,
                 "seed_price":1200,"max_stage":4,"xp_per_stage":[300,750,1800,3600],
                 "image":"trees/SONOKELING.png","desc":"Kayu hitam Jawa. Serat indah, bernilai tinggi.",
                 "bonuses":["Kayu bernilai tinggi","XP besar","Hewan mulai tertarik"],
                 "animals":["harimau_sumatra","cendrawasih"]},
    "ulin":     {"id":"ulin","name":"Ulin","latin":"Eusideroxylon zwageri","tier":"rare",
                 "dns_per_jam":32,"grow_days":7,"panen_dns":650,"wood":18,"water_need":4,"pupuk_need":2,
                 "seed_price":1500,"max_stage":4,"xp_per_stage":[320,800,2000,4000],
                 "image":"trees/ULIN.png","desc":"Kayu besi Kalimantan. Terkeras di Indonesia.",
                 "bonuses":["Kayu terkuat","XP besar","Predator tertarik"],
                 "animals":["harimau_sumatra","orangutan","komodo"]},
    # ══ EPIC ══
    "jati":     {"id":"jati","name":"Jati","latin":"Tectona grandis","tier":"epic",
                 "dns_per_jam":50,"grow_days":30,"panen_dns":800,"wood":25,"water_need":4,"pupuk_need":3,
                 "seed_price":3000,"max_stage":5,"xp_per_stage":[600,1500,3500,7000,15000],
                 "image":None,"desc":"Raja kayu Nusantara. Peti akar kuno mulai muncul.",
                 "bonuses":["Kayu bernilai tertinggi","DNS tinggi","Peti akar kuno muncul"],
                 "animals":["orangutan","komodo","rajawali_jawa"],"special":"ancient_chest"},
    "bangkirai":{"id":"bangkirai","name":"Bangkirai","latin":"Shorea laevifolia","tier":"epic",
                 "dns_per_jam":55,"grow_days":30,"panen_dns":850,"wood":22,"water_need":4,"pupuk_need":3,
                 "seed_price":2800,"max_stage":5,"xp_per_stage":[600,1500,3500,7000,15000],
                 "image":None,"desc":"Kayu besi Kalimantan. Tahan cuaca ekstrem ribuan tahun.",
                 "bonuses":["Kayu tahan lama","DNS tinggi","Hewan epik tertarik"],
                 "animals":["komodo","rajawali_jawa"],"special":"ancient_chest"},
    # ══ LEGENDARY ══
    "ebony":    {"id":"ebony","name":"Ebony Sulawesi","latin":"Diospyros celebica","tier":"legendary",
                 "dns_per_jam":90,"grow_days":60,"panen_dns":3000,"wood":45,"water_need":5,"pupuk_need":4,
                 "seed_price":15000,"max_stage":5,"xp_per_stage":[1500,4000,9000,18000,35000],
                 "image":None,"desc":"Kayu hitam paling eksklusif di dunia. Hanya di Sulawesi.",
                 "bonuses":["Hewan langka muncul","Harta karun akar","DNS meningkat pesat"],
                 "animals":["long_wang","fenghuang"],"special":"treasure"},
    "cendana":  {"id":"cendana","name":"Cendana","latin":"Santalum album","tier":"legendary",
                 "dns_per_jam":100,"grow_days":60,"panen_dns":4000,"wood":40,"water_need":5,"pupuk_need":5,
                 "seed_price":20000,"max_stage":5,"xp_per_stage":[2000,5000,11000,22000,40000],
                 "image":None,"desc":"Emas putih Nusa Tenggara. Wanginya menarik makhluk gaib.",
                 "bonuses":["Hewan mitologi muncul","Harta karun","DNS tertinggi tier ini"],
                 "animals":["long_wang","qilin"],"special":"treasure"},
    # ══ MYTHIC ══
    "gaharu":   {"id":"gaharu","name":"Gaharu","latin":"Aquilaria malaccensis","tier":"mythic",
                 "dns_per_jam":120,"grow_days":90,"panen_dns":15000,"wood":100,"water_need":5,"pupuk_need":5,
                 "seed_price":80000,"max_stage":5,"xp_per_stage":[5000,12000,25000,50000,100000],
                 "image":None,"desc":"Kayu surga. Harganya melebihi emas murni per kilogram.",
                 "bonuses":["Peti ajaib muncul","Efek visual peta","Hewan Mythic datang"],
                 "animals":["pegasus","griffin"],"special":"magic_chest","visual":"golden_aura"},
    "gaharu_emas":{"id":"gaharu_emas","name":"Gaharu Emas","latin":"Aquilaria aurea","tier":"mythic",
                 "dns_per_jam":130,"grow_days":90,"panen_dns":25000,"wood":120,"water_need":5,"pupuk_need":5,
                 "seed_price":150000,"max_stage":5,"xp_per_stage":[6000,15000,30000,60000,120000],
                 "image":None,"desc":"Mutasi langka Gaharu. Kayunya berwarna emas saat dibelah.",
                 "bonuses":["Kayu emas langka","Hewan Mythic datang","DNS luar biasa"],
                 "animals":["hydra","pegasus"],"special":"magic_chest","visual":"golden_pulse"},
    # ══ DIVINE ══
    "yggdrasil_nusantara":{"id":"yggdrasil_nusantara","name":"Yggdrasil Nusantara","latin":"Arbor mundi nusantara",
                 "tier":"divine","dns_per_jam":120,"grow_days":15,"panen_dns":10000,"wood":300,
                 "water_need":5,"pupuk_need":5,"seed_price":0,"max_stage":5,
                 "xp_per_stage":[50000,120000,250000,500000,1000000],
                 "image":"trees/YGGDRASIL_NUSANTARA.png",
                 "desc":"Pohon dunia Nusantara. Akarnya menembus semua dimensi.",
                 "bonuses":["Hanya via Event Global","Aura cahaya permanen","Semua hewan Divine"],
                 "animals":["fenrir","leviathan","jormungandr"],"special":"divine","event_only":True,"visual":"rainbow"},
    "pohon_surga":{"id":"pohon_surga","name":"Pohon Surga","latin":"Arbor paradisi divinus",
                 "tier":"divine","dns_per_jam":125,"grow_days":None,"panen_dns":12000,"wood":500,
                 "water_need":5,"pupuk_need":5,"seed_price":0,"max_stage":5,
                 "xp_per_stage":[80000,200000,400000,800000,2000000],
                 "image":"trees/POHON_SURGA.png",
                 "desc":"Pohon tertinggi. Hanya lewat event global terbesar.",
                 "bonuses":["Hanya via Event Global","Aura abadi","Semua hewan Divine","Relic Suci"],
                 "animals":["fenrir","leviathan","jormungandr"],"special":"divine","event_only":True,"visual":"god_aura"},
}

# ── HEWAN ──────────────────────────────────────────────────
ANIMAL_CATALOG = {
    # COMMON — hewan nyata
    "tupai_emas":      {"name":"Tupai Emas","latin":"Callosciurus notatus","tier":"common","emoji":"🐿️","xp":5,"price":200,"lore":None,"foods_tree":["buah","biji"],"foods_shop":["kacang"],"sizes":["bayi","kecil","sedang","besar"]},
    "burung_pipit":    {"name":"Burung Pipit","latin":"Lonchura leucogastroides","tier":"common","emoji":"🐦","xp":4,"price":150,"lore":None,"foods_tree":["biji","daun"],"foods_shop":["campuran_biji"],"sizes":["bayi","kecil","sedang"]},
    "kera_ekor_panjang":{"name":"Kera Ekor Panjang","latin":"Macaca fascicularis","tier":"common","emoji":"🐒","xp":7,"price":300,"lore":None,"foods_tree":["buah","biji"],"foods_shop":["pisang"],"sizes":["bayi","kecil","sedang","besar"]},
    # UNCOMMON
    "rusa_sambar":     {"name":"Rusa Sambar","latin":"Rusa unicolor","tier":"uncommon","emoji":"🦌","xp":12,"price":800,"lore":None,"foods_tree":["daun","buah"],"foods_shop":["wortel"],"sizes":["bayi","kecil","sedang","besar"]},
    "elang_brontok":   {"name":"Elang Brontok","latin":"Nisaetus cirrhatus","tier":"uncommon","emoji":"🦅","xp":15,"price":1200,"lore":None,"foods_tree":[],"foods_shop":["daging","ikan"],"sizes":["bayi","kecil","sedang","besar"]},
    # RARE
    "orangutan":       {"name":"Orangutan","latin":"Pongo pygmaeus","tier":"rare","emoji":"🦧","xp":28,"price":5000,"lore":None,"foods_tree":["buah","daun"],"foods_shop":["pisang","madu"],"sizes":["bayi","kecil","sedang","besar","dewasa"]},
    "harimau_sumatra": {"name":"Harimau Sumatra","latin":"Panthera tigris sumatrae","tier":"rare","emoji":"🐯","xp":30,"price":6000,"lore":None,"foods_tree":[],"foods_shop":["daging","ikan"],"sizes":["bayi","kecil","sedang","besar","dewasa"]},
    "cendrawasih":     {"name":"Cendrawasih","latin":"Paradisaea apoda","tier":"rare","emoji":"🦜","xp":25,"price":4000,"lore":None,"foods_tree":["buah"],"foods_shop":["madu","serangga"],"sizes":["bayi","kecil","sedang","besar","dewasa"]},
    # EPIC
    "komodo":          {"name":"Komodo","latin":"Varanus komodoensis","tier":"epic","emoji":"🦎","xp":50,"price":20000,"lore":None,"foods_tree":[],"foods_shop":["daging","daging_premium"],"sizes":["bayi","kecil","sedang","besar","dewasa"]},
    "rajawali_jawa":   {"name":"Rajawali Jawa","latin":"Nisaetus bartelsi","tier":"epic","emoji":"🦁","xp":55,"price":25000,"lore":None,"foods_tree":[],"foods_shop":["daging_premium"],"sizes":["bayi","kecil","sedang","besar","dewasa"]},
    # LEGENDARY — MITOLOGI CHINA
    "long_wang":       {"name":"Long Wang (龍王)","latin":"Naga Rex Maris","tier":"legendary","emoji":"🐲","xp":100,"price":80000,
                        "lore":"Dewa naga penguasa lautan dan cuaca dalam mitologi China. Dipuja nelayan sebelum melaut. Empat saudaranya menguasai empat lautan dunia.",
                        "foods_tree":["buah_langka"],"foods_shop":["amerta"],"sizes":["kecil","sedang","besar","dewasa"]},
    "fenghuang":       {"name":"Fenghuang (鳳凰)","latin":"Phoenix Sinicus","tier":"legendary","emoji":"🌅","xp":90,"price":70000,
                        "lore":"Raja segala burung dalam mitologi China. Hanya muncul saat pemerintahan bijaksana. Tubuhnya menggabungkan 5 unsur dan warna 5 kebajikan Konfusianisme.",
                        "foods_tree":["buah_dewa"],"foods_shop":["amerta"],"sizes":["kecil","sedang","besar","dewasa"]},
    "qilin":           {"name":"Qilin (麒麟)","latin":"Unicornus Sinicus","tier":"legendary","emoji":"✨","xp":120,"price":100000,
                        "lore":"Makhluk suci pembawa keberuntungan. Bersisik seperti naga, bertanduk satu, berjalan tanpa merusak rerumputan. Muncul saat orang bijak lahir.",
                        "foods_tree":["buah_suci"],"foods_shop":["amerta"],"sizes":["kecil","besar","dewasa"]},
    # MYTHIC — MITOLOGI YUNANI
    "pegasus":         {"name":"Pegasus","latin":"Pegasus Graecus","tier":"mythic","emoji":"🐴","xp":250,"price":500000,
                        "lore":"Kuda bersayap lahir dari darah Medusa. Dijinakkan Bellerophon. Mengangkut petir Zeus ke Olympus. Kini bintang di langit utara.",
                        "foods_tree":["amerta_pohon"],"foods_shop":["amerta_emas"],"sizes":["sedang","besar","dewasa"]},
    "griffin":         {"name":"Griffin (Γρύφων)","latin":"Gryphus Graecus","tier":"mythic","emoji":"🦁","xp":280,"price":600000,
                        "lore":"Kepala elang + badan singa. Penjaga harta emas Apollo di utara dunia. Satu griffin setara 8 singa atau 100 elang.",
                        "foods_tree":["amerta_pohon"],"foods_shop":["amerta_emas"],"sizes":["sedang","besar","dewasa"]},
    "hydra":           {"name":"Hydra (Ὕδρα)","latin":"Hydra Lernaea","tier":"mythic","emoji":"🐍","xp":300,"price":750000,
                        "lore":"Ular sembilan kepala rawa Lerna. Tiap kepala dipotong tumbuh dua. Racunnya mematikan dewa sekalipun. Dibunuh Heracles sebagai tugas ke-2.",
                        "foods_tree":["amerta_pohon"],"foods_shop":["amerta_emas"],"sizes":["besar","dewasa"]},
    # DIVINE — MITOLOGI NORSE/EROPA
    "fenrir":          {"name":"Fenrir","latin":"Fenrisulfr Norsicus","tier":"divine","emoji":"🐺","xp":500,"price":3000000,
                        "lore":"Putra Loki, terbesar dari segala serigala. Dirantai para dewa dengan tali Gleipnir. Saat Ragnarok ia bebas dan menelan Odin. Ukurannya setara gunung.",
                        "foods_tree":["amerta_ilahi"],"foods_shop":["amerta_dewa"],"sizes":["dewasa"]},
    "leviathan":       {"name":"Leviathan","latin":"Leviathan Abyssus","tier":"divine","emoji":"🌊","xp":600,"price":5000000,
                        "lore":"Makhluk laut purba dari teks Ibrani kuno. Penguasa lautan dalam. Tubuhnya melingkari seluruh bumi. Nafasnya membakar lautan.",
                        "foods_tree":["amerta_ilahi"],"foods_shop":["amerta_dewa"],"sizes":["dewasa"]},
    "jormungandr":     {"name":"Jörmungandr","latin":"Serpens Midgardensis","tier":"divine","emoji":"🌙","xp":700,"price":8000000,
                        "lore":"Putra Loki dan Angrboda. Mengitari bumi dan menggigit ekornya sendiri (Ouroboros). Musuh abadi Thor. Racunnya membunuh Thor setelah 9 langkah.",
                        "foods_tree":["amerta_ilahi"],"foods_shop":["amerta_dewa"],"sizes":["dewasa"]},
}

SHOP_ITEMS = {
    # ALAT
    "cangkul_kristal":  {"name":"Cangkul Kristal Air","type":"tool","price":450,"rarity":"rare","desc":"Panen XP +25% selama 3 hari"},
    "pupuk_dewa":       {"name":"Pupuk Dewa","type":"tool","price":1200,"rarity":"epic","desc":"Pohon skip 1 stage pertumbuhan"},
    "ember_emas":       {"name":"Ember Emas","type":"tool","price":800,"rarity":"rare","desc":"Siram 3 pohon sekaligus"},
    "drone_penyiram":   {"name":"Drone Penyiram","type":"tool","price":8000,"rarity":"legendary","desc":"Siram otomatis 3 hari"},
    # DEKO
    "lentera_kunang":   {"name":"Lentera Kunang","type":"deco","price":600,"rarity":"rare","desc":"Pengunjung +20% malam hari"},
    "menara_sarang":    {"name":"Menara Sarang","type":"deco","price":2800,"rarity":"epic","desc":"Tambah 2 slot kandang"},
    "patung_garuda":    {"name":"Patung Garuda","type":"deco","price":15000,"rarity":"legendary","desc":"Hewan Legendary lebih sering"},
    "altar_naga":       {"name":"Altar Naga Kuno","type":"deco","price":50000,"rarity":"mythic","desc":"Hewan Mythic bisa datang"},
    # JIMAT
    "kristal_waktu":    {"name":"Kristal Waktu","type":"amulet","price":1800,"rarity":"epic","desc":"Pohon tumbuh 2x lebih cepat 24 jam"},
    "batu_nasib":       {"name":"Batu Nasib Emas","type":"amulet","price":5000,"rarity":"legendary","desc":"Peluang Epic/Legendary 3x, 7 hari"},
    "perisai_rimbara":  {"name":"Perisai Rimbara","type":"amulet","price":900,"rarity":"rare","desc":"Pohon tidak layu 3 hari"},
    "mahkota_ilahi":    {"name":"Mahkota Cahaya Ilahi","type":"amulet","price":200000,"rarity":"divine","desc":"Semua hewan +50% ikatan"},
    # PAKAN
    "daging_segar":     {"name":"Daging Segar","type":"food","price":80,"rarity":"common","desc":"+25 kenyang karnivora"},
    "madu_hutan":       {"name":"Madu Hutan","type":"food","price":150,"rarity":"uncommon","desc":"+15 bahagia +10 kenyang"},
    "daging_premium":   {"name":"Daging Premium","type":"food","price":500,"rarity":"rare","desc":"+40 kenyang predator"},
    "amerta":           {"name":"Amerta","type":"food","price":5000,"rarity":"legendary","desc":"+100 semua stat, Legendary+"},
    "amerta_emas":      {"name":"Amerta Emas","type":"food","price":25000,"rarity":"mythic","desc":"+200 semua stat, Mythic+"},
    "amerta_dewa":      {"name":"Amerta Para Dewa","type":"food","price":100000,"rarity":"divine","desc":"+500 semua stat, Divine"},
    # BIBIT
    "bibit_mahoni":     {"name":"Bibit Mahoni","type":"seed","price":50,"rarity":"common","desc":"Tumbuh 3 hari · 10 DNS/jam"},
    "bibit_akasia":     {"name":"Bibit Akasia","type":"seed","price":60,"rarity":"common","desc":"Tumbuh 3 hari · 12 DNS/jam"},
    "bibit_trembesi":   {"name":"Bibit Trembesi","type":"seed","price":80,"rarity":"common","desc":"Tumbuh 4 hari · 15 DNS/jam"},
    "bibit_rambutan":   {"name":"Bibit Rambutan","type":"seed","price":250,"rarity":"uncommon","desc":"Tumbuh 5 hari · 18 DNS/jam"},
    "bibit_mangga":     {"name":"Bibit Mangga","type":"seed","price":280,"rarity":"uncommon","desc":"Tumbuh 4 hari · 20 DNS/jam"},
    "bibit_nangka":     {"name":"Bibit Nangka","type":"seed","price":300,"rarity":"uncommon","desc":"Tumbuh 5 hari · 22 DNS/jam"},
    "bibit_sonokeling": {"name":"Bibit Sonokeling","type":"seed","price":1200,"rarity":"rare","desc":"Tumbuh 7 hari · 28 DNS/jam"},
    "bibit_ulin":       {"name":"Bibit Ulin","type":"seed","price":1500,"rarity":"rare","desc":"Tumbuh 7 hari · 32 DNS/jam"},
    "bibit_jati":       {"name":"Bibit Jati","type":"seed","price":3000,"rarity":"epic","desc":"Tumbuh 30 hari · 50 DNS/jam"},
    "bibit_ebony":      {"name":"Bibit Ebony Sulawesi","type":"seed","price":15000,"rarity":"legendary","desc":"Tumbuh 60 hari · 90 DNS/jam"},
    "bibit_cendana":    {"name":"Bibit Cendana","type":"seed","price":20000,"rarity":"legendary","desc":"Tumbuh 60 hari · 100 DNS/jam"},
    "bibit_gaharu":     {"name":"Bibit Gaharu","type":"seed","price":80000,"rarity":"mythic","desc":"Tumbuh 90 hari · 120 DNS/jam"},
}

RARITY_STYLE = {
    "common":    {"badge":"#EAF3DE","text":"#27500A","border":"#97C459","label":"Common",    "star":"🌱","glow":"rgba(90,181,32,.3)","bg":"#EAF3DE","bor":"#97C459","color":"#27500A"},
    "uncommon":  {"badge":"#D8F0E8","text":"#0A5032","border":"#40C878","label":"Uncommon",  "star":"🍀","glow":"rgba(64,200,120,.3)","bg":"#D8F0E8","bor":"#40C878","color":"#0A5032"},
    "rare":      {"badge":"#E6F1FB","text":"#0C447C","border":"#85B7EB","label":"Rare",      "star":"🔵","glow":"rgba(64,144,224,.3)","bg":"#E6F1FB","bor":"#85B7EB","color":"#0C447C"},
    "epic":      {"badge":"#EEEDFE","text":"#3C3489","border":"#AFA9EC","label":"Epic",      "star":"🟣","glow":"rgba(160,128,255,.3)","bg":"#EEEDFE","bor":"#AFA9EC","color":"#3C3489"},
    "legendary": {"badge":"#FAEEDA","text":"#633806","border":"#EF9F27","label":"Legendary", "star":"🟠","glow":"rgba(240,176,48,.4)","bg":"#FAEEDA","bor":"#EF9F27","color":"#633806"},
    "mythic":    {"badge":"#FFE8E6","text":"#7A1A10","border":"#FF5040","label":"Mythic",    "star":"🔴","glow":"rgba(255,80,64,.4)","bg":"#FFE8E6","bor":"#FF5040","color":"#7A1A10"},
    "divine":    {"badge":"#FFFBE6","text":"#7A6A00","border":"#FFE020","label":"Divine",    "star":"🟡","glow":"rgba(255,220,32,.5)","bg":"#FFFBE6","bor":"#FFE020","color":"#7A6A00"},
}

# DNS Distribution Wallets (admin-only)
DNS_DISTRIBUTION = {
    "gameplay_reward":  {"name":"Gameplay Reward Pool",  "percent":40,"amount":400_000_000,"desc":"Panen harian, quest"},
    "ecosystem":        {"name":"Ecosystem & Bursa",     "percent":20,"amount":200_000_000,"desc":"Likuiditas P2P"},
    "event_guild":      {"name":"Event & Guild Reward",  "percent":15,"amount":150_000_000,"desc":"Hadiah event global"},
    "developer":        {"name":"Developer & Ops Fund",  "percent":10,"amount":100_000_000,"desc":"Dev fund, server ops"},
    "airdrop":          {"name":"Airdrop Awal",          "percent":10,"amount":100_000_000,"desc":"Bonus player awal"},
    "reserve":          {"name":"Reserve Strategis",     "percent":5, "amount":50_000_000, "desc":"Cadangan darurat"},
}

def get_tree(tid): return TREE_CATALOG.get(tid)
def get_all_trees(): return list(TREE_CATALOG.values())



def get_tree_image_by_height(tree_id: str, height_cm: float) -> str:
    """
    Return path gambar pohon berdasarkan tinggi (cm).
    Sistem folder: trees/{tree_id}/bibit.png, semai.png, remaja.png, dewasa.png
    
    Logika tinggi → fase:
      0  - 10 cm  → bibit
      11 - 30 cm  → semai
      31 - 70 cm  → remaja
      71+ cm      → dewasa
    
    Priority:
      1. Cek folder trees/{tree_id}/{fase}.png
      2. Cek image_stages dari katalog
      3. Fallback None (template tampilkan SVG generatif)
    """
    import os
    
    # Tentukan fase berdasarkan tinggi
    if height_cm <= 10:
        fase = "bibit"
    elif height_cm <= 30:
        fase = "semai"
    elif height_cm <= 70:
        fase = "remaja"
    else:
        fase = "dewasa"
    
    # 1. Cek folder per pohon: images/trees/{tree_id}/{fase}.png atau .svg
    for ext in [".png", ".svg", ".jpg", ".webp"]:
        folder_path = f"images/trees/{tree_id}/{fase}{ext}"
        if os.path.exists(f"static/{folder_path}"):
            return folder_path
    
    # 2. Fallback ke image_stages dari katalog
    tree = TREE_CATALOG.get(tree_id)
    if not tree:
        return None
    
    stages = tree.get("image_stages")
    if stages:
        fase_idx = {"bibit": 0, "semai": 1, "remaja": 2, "dewasa": 3}
        idx = min(fase_idx.get(fase, 0), len(stages) - 1)
        img = stages[idx]
        # Normalkan path ke format images/...
        img_norm = img if img.startswith("images/") else f"images/{img}"
        if os.path.exists(f"static/{img_norm}"):
            return img_norm
    
    # 3. Cek image default
    default = tree.get("image")
    if default:
        default_norm = default if default.startswith("images/") else f"images/{default}"
        if os.path.exists(f"static/{default_norm}"):
            return default_norm
    
    return None  # Tidak ada gambar → template tampilkan SVG


def get_height_cm_from_stage(stage: int) -> float:
    """
    Konversi stage pohon ke estimasi tinggi dalam cm.
    Stage 1=5cm, 2=30cm, 3=70cm, 4=200cm, 5=700cm, dst.
    """
    stage_heights = {1: 5, 2: 30, 3: 70, 4: 200, 5: 700,
                     6: 1200, 7: 1800, 8: 2500, 9: 3500, 10: 5000}
    return float(stage_heights.get(stage, 5))

def get_tree_image(tree_id: str, stage: int = 1) -> str:
    """
    Return path gambar pohon sesuai stage.
    Jika ada image_stages, pakai gambar per stage.
    Jika tidak, pakai gambar default (image).
    Stage dimulai dari 1.
    """
    tree = TREE_CATALOG.get(tree_id)
    if not tree:
        return "trees/MAHONI.png"
    
    stages = tree.get("image_stages")
    if stages:
        idx = max(0, min(stage - 1, len(stages) - 1))
        return stages[idx]
    
    return tree.get("image", "trees/MAHONI.png")

def get_trees_by_tier(tier): return [t for t in TREE_CATALOG.values() if t["tier"]==tier]
def get_animal(aid): return ANIMAL_CATALOG.get(aid)
def get_rarity_style(r): return RARITY_STYLE.get(r, RARITY_STYLE["common"])
def get_tier_info(t): return TREE_TIERS.get(t, TREE_TIERS["common"])

def get_xp_progress(tree_xp, tree_id):
    tree = get_tree(tree_id)
    if not tree: return {"current":0,"needed":100,"percent":0,"stage":1,"maxed":False,"next_stage":2}
    stage, cum = 1, 0
    for i, need in enumerate(tree["xp_per_stage"], 1):
        cum += need
        if tree_xp >= cum: stage = i+1
        else: break
    stage = min(stage, tree["max_stage"])
    if stage >= tree["max_stage"]:
        return {"current":tree_xp,"needed":tree_xp,"percent":100,"stage":stage,"maxed":True,"next_stage":stage}
    cum2 = sum(tree["xp_per_stage"][:stage-1])
    cur = tree_xp - cum2
    need = tree["xp_per_stage"][stage-1]
    return {"current":cur,"needed":need,"percent":min(100,int(cur/need*100)),"stage":stage,"next_stage":stage+1,"maxed":False}
