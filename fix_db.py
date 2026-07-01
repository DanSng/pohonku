"""
fix_db.py — Migrasi database PohonKu v3
Aman dijalankan berkali-kali (idempotent).
Jalankan: python fix_db.py
"""
import sqlite3, os, glob, shutil

print("=" * 55)
print("  PohonKu v3 — Migrasi Database")
print("=" * 55)

# Cari file database
db_files = glob.glob("*.db") + glob.glob("instance/*.db") + glob.glob("**/*.db", recursive=True)
db_files = list(set(db_files))

if not db_files:
    print("\n[!] File .db tidak ditemukan.")
    print("    Letakkan file database ke folder ini, lalu jalankan lagi.")
    input("\nTekan Enter untuk keluar...")
    exit()

if len(db_files) == 1:
    db_path = db_files[0]
    print(f"\nDatabase: {db_path}")
else:
    print("\nBeberapa database ditemukan:")
    for i,f in enumerate(db_files):
        size = os.path.getsize(f) // 1024
        print(f"  [{i+1}] {f}  ({size} KB)")
    pilih = input("\nPilih nomor [1]: ").strip()
    idx = int(pilih)-1 if pilih.isdigit() else 0
    db_path = db_files[max(0,min(idx,len(db_files)-1))]

# Backup otomatis
backup = db_path + ".backup"
if not os.path.exists(backup):
    shutil.copy2(db_path, backup)
    print(f"✓ Backup: {backup}")

# Rename jika perlu
target = "pohonku_v3.db"
if os.path.basename(db_path) != target and not os.path.exists(target):
    shutil.copy2(db_path, target)
    print(f"✓ Disalin sebagai: {target}")
    db_path = target

conn = sqlite3.connect(db_path)
cur  = conn.cursor()
fixes = 0
tables = [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"\nTabel: {tables}")

def add_col(table, col, coltype, default=None):
    global fixes
    try:
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()]
        if not cols: return
        if col not in cols:
            dflt = f" DEFAULT {default}" if default is not None else ""
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}{dflt}")
            print(f"  ✓ {table}.{col}")
            fixes += 1
    except Exception as e:
        print(f"  ! {table}.{col}: {e}")

print("\n[users]")
if "users" in tables:
    add_col("users","verified","BOOLEAN","1")
    add_col("users","coins","INTEGER","0")
    add_col("users","streak_days","INTEGER","0")
    add_col("users","o2_total","REAL","0")
    add_col("users","wood","INTEGER","0")
    add_col("users","guild_id","INTEGER",None)
    add_col("users","onboarding_done","BOOLEAN","1")
    add_col("users","title","TEXT","'Petualang Baru'")
    add_col("users","is_banned","BOOLEAN","0")
    add_col("users","city","VARCHAR(100)","'Indonesia'")
    add_col("users","last_active","DATETIME",None)
    cur.execute("UPDATE users SET verified=1 WHERE verified IS NULL OR verified=0")
    cur.execute("UPDATE users SET onboarding_done=1 WHERE onboarding_done IS NULL")
    n = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"  → {n} user ditemukan, semua diverifikasi")

print("\n[wallets]")
if "wallets" in tables:
    add_col("wallets","pin_hash","VARCHAR(256)",None)
    add_col("wallets","pin_set","BOOLEAN","0")
    add_col("wallets","pin_wrong","INTEGER","0")
    add_col("wallets","pin_locked_until","DATETIME",None)
    n = cur.execute("SELECT COUNT(*) FROM wallets").fetchone()[0]
    print(f"  → {n} wallet ditemukan")


print("\n[wallets — buat yang kurang]")
cur.execute("""
    INSERT INTO wallets (user_id, address, balance, total_earned, total_spent)
    SELECT u.id,
           'PK-' || printf('%04d', u.id) || '-' || UPPER(SUBSTR(HEX(RANDOMBLOB(4)),1,8)),
           0, 0, 0
    FROM users u
    LEFT JOIN wallets w ON w.user_id = u.id
    WHERE w.id IS NULL AND u.role = 'user'
""")
n_created = cur.rowcount
if n_created > 0:
    print(f"  ✓ {n_created} wallet baru dibuat untuk user yang belum punya")
else:
    print("  ✓ Semua user sudah punya wallet")
print("\n[user_trees]")
if "user_trees" in tables:
    add_col("user_trees","selfie_path","TEXT","''")
    add_col("user_trees","location_name","TEXT","''")
    add_col("user_trees","lat","REAL",None)
    add_col("user_trees","lng","REAL",None)
    add_col("user_trees","total_o2","REAL","0")
    add_col("user_trees","stage","INTEGER","1")
    add_col("user_trees","rarity","VARCHAR(20)","'common'")
    add_col("user_trees","xp","REAL","0")
    add_col("user_trees","health","INTEGER","100")
    add_col("user_trees","pupuk_today","INTEGER","0")
    n = cur.execute("SELECT COUNT(*) FROM user_trees").fetchone()[0]
    print(f"  → {n} pohon ditemukan")

print("\n[referrals]")
if "referrals" in tables:
    add_col("referrals","dns_reward","REAL","0")
    add_col("referrals","created_at","DATETIME",None)
    add_col("referrals","step1_given","BOOLEAN","0")
    add_col("referrals","step2_given","BOOLEAN","0")
    add_col("referrals","step3_given","BOOLEAN","0")
    add_col("referrals","harvest_count","INTEGER","0")
    # Mark referral lama sebagai selesai semua
    cur.execute("UPDATE referrals SET step1_given=1,step2_given=1,step3_given=1,reward_given=1 WHERE reward_given=1 AND step1_given=0")
    add_col("referrals","created_at","DATETIME",None)

print("\n[distribution_wallets]")
if "distribution_wallets" in tables:
    add_col("distribution_wallets","disbursed","REAL","0")

print("\n[dns_supply]")
if "dns_supply" in tables:
    add_col("dns_supply","locked","REAL","1000000000")
    add_col("dns_supply","burned","REAL","0")

# Buat tabel baru yang belum ada
print("\n[dns_orders — tabel baru]")
cur.execute("""
    CREATE TABLE IF NOT EXISTS dns_orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        order_code VARCHAR(20) UNIQUE NOT NULL,
        package_key VARCHAR(20) NOT NULL,
        package_name VARCHAR(50) NOT NULL,
        dns_amount INTEGER NOT NULL,
        price_base INTEGER NOT NULL,
        price_unique INTEGER NOT NULL,
        unique_code INTEGER NOT NULL,
        proof_path VARCHAR(200),
        status VARCHAR(20) DEFAULT 'pending',
        admin_note VARCHAR(200),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        verified_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
print("  ✓ dns_orders")

print("\n[streak_logs — tabel baru]")
cur.execute("""
    CREATE TABLE IF NOT EXISTS streak_logs (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        streak_day INTEGER NOT NULL,
        dns_bonus REAL DEFAULT 0,
        logged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
print("  ✓ streak_logs")

conn.commit()
conn.close()

print(f"\n{'='*55}")
print(f"  Selesai! {fixes} perubahan diterapkan.")
if fixes == 0:
    print("  Database sudah up-to-date.")
print(f"\n  Sekarang jalankan MULAI.bat")
print(f"{'='*55}")
input("\nTekan Enter untuk keluar...")
