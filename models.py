from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ─── USER ────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id              = db.Column(db.Integer, primary_key=True)
    email           = db.Column(db.String(120), unique=True, nullable=False)
    username        = db.Column(db.String(64), unique=True, nullable=False)
    password_hash   = db.Column(db.String(256))
    role            = db.Column(db.String(16), default='user', index=True)  # user|admin
    level           = db.Column(db.Integer, default=1)
    xp              = db.Column(db.Integer, default=0)
    o2_total        = db.Column(db.Float, default=0.0)   # O2 kumulatif
    wood            = db.Column(db.Integer, default=0)    # kayu untuk sarang
    selfie_path     = db.Column(db.String(256), default='')
    lat             = db.Column(db.Float, nullable=True)
    lng             = db.Column(db.Float, nullable=True)
    location_name   = db.Column(db.String(256), default='')
    title           = db.Column(db.String(64), default='Petualang Baru')
    streak_days     = db.Column(db.Integer, default=0)
    last_active     = db.Column(db.Date, default=date.today)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    last_login      = db.Column(db.DateTime, default=datetime.utcnow)
    guild_id        = db.Column(db.Integer, db.ForeignKey('guilds.id'), nullable=True)
    is_banned       = db.Column(db.Boolean, default=False, index=True)
    onboarding_done = db.Column(db.Boolean, default=False)
    verified        = db.Column(db.Boolean, default=True)   # auto verified, tidak perlu approval admin

    __table_args__ = (
        # Kombinasi (role, is_banned) inilah yang paling sering dipakai bareng
        # di query (leaderboard, admin dashboard, seed quest harian, dll).
        db.Index('ix_users_role_banned', 'role', 'is_banned'),
    )


    wallet      = db.relationship('Wallet', backref='user', uselist=False, cascade='all,delete')
    trees       = db.relationship('UserTree', backref='owner', lazy='dynamic', cascade='all,delete')
    animals     = db.relationship('UserAnimal', backref='owner', lazy='dynamic', cascade='all,delete')
    quests      = db.relationship('Quest', backref='user', lazy='dynamic', cascade='all,delete')
    inventory   = db.relationship('InventoryItem', backref='owner', lazy='dynamic', cascade='all,delete')
    character   = db.relationship('Character', backref='user', uselist=False, cascade='all,delete')

    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)
    @property
    def is_admin(self): return self.role == 'admin'
    @property
    def active_tree(self): return self.trees.filter_by(is_active=True).first()
    @property
    def dns_balance(self): return self.wallet.balance if self.wallet else 0.0

    def add_xp(self, n):
        self.xp += n
        needed = self.level * 1000
        while self.xp >= needed:
            self.xp -= needed; self.level += 1; needed = self.level * 1000
        # Update title
        titles = [(5,"Petualang Baru"),(15,"Penjaga Bibit"),(30,"Petani Hutan"),
                  (50,"Pelestari Alam"),(75,"Penjaga Rimba"),(98,"Guardian Arboria"),(99,"Dewa Pohon")]
        for lvl, t in reversed(titles):
            if self.level >= lvl: self.title = t; break

# ─── WALLET ──────────────────────────────────────────────────
class Wallet(db.Model):
    __tablename__ = 'wallets'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    address     = db.Column(db.String(16), unique=True, nullable=False)  # PK-XXXXXXXX
    balance     = db.Column(db.Float, default=0.0, index=True)
    total_earned= db.Column(db.Float, default=0.0)
    total_spent = db.Column(db.Float, default=0.0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    pin_hash         = db.Column(db.String(256), nullable=True)
    pin_set          = db.Column(db.Boolean, default=False)
    pin_wrong        = db.Column(db.Integer, default=0)
    pin_locked_until = db.Column(db.DateTime, nullable=True)

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(str(pin))
        self.pin_set  = True; self.pin_wrong = 0; self.pin_locked_until = None

    def check_pin(self, pin) -> bool:
        if not self.pin_set: return False
        return check_password_hash(self.pin_hash, str(pin))

    def is_pin_locked(self) -> bool:
        return bool(self.pin_locked_until and self.pin_locked_until > datetime.utcnow())

    def add_dns(self, amount: float, note: str = "", tx_type: str = "harvest"):
        if amount <= 0: return
        self.balance += amount
        self.total_earned += amount
        _record_tx("SYSTEM", self.address, amount, tx_type, note)

    def spend_dns(self, amount: float, note: str = "", tx_type: str = "purchase") -> bool:
        if amount > self.balance: return False
        self.balance -= amount
        self.total_spent += amount
        burn = round(amount * 0.01, 4)
        _record_tx(self.address, "BURN", burn, "burn", f"1% burn dari {tx_type}")
        _record_tx(self.address, "SYSTEM", amount - burn, tx_type, note)
        return True

    def transfer_to(self, target_wallet, amount: float) -> bool:
        fee = 1.0
        total = amount + fee
        if total > self.balance: return False
        self.balance -= total
        self.total_spent += total
        target_wallet.balance += amount
        target_wallet.total_earned += amount
        _record_tx(self.address, target_wallet.address, amount, "transfer", "transfer antar player")
        _record_tx(self.address, "BURN", fee, "burn", "fee transfer 1 DNS")
        return True

def _record_tx(sender, receiver, amount, tx_type, note):
    """Buat DNSTransaction baru dengan hash blockchain."""
    from blockchain import compute_block_hash, genesis_hash
    last = DNSTransaction.query.order_by(DNSTransaction.block_number.desc()).first()
    block_num = (last.block_number + 1) if last else 1
    prev_hash = last.block_hash if last else genesis_hash()
    ts = datetime.utcnow()
    bh = compute_block_hash(block_num, prev_hash, sender or "SYSTEM",
                            receiver or "SYSTEM", amount, tx_type, ts.isoformat())
    tx = DNSTransaction(
        block_number=block_num, prev_hash=prev_hash, block_hash=bh,
        sender_wallet=sender, receiver_wallet=receiver,
        amount=amount, tx_type=tx_type, note=note, timestamp=ts
    )
    db.session.add(tx)

# ─── DNS BLOCKCHAIN TRANSACTION ──────────────────────────────
class DNSTransaction(db.Model):
    __tablename__ = 'dns_transactions'
    id              = db.Column(db.Integer, primary_key=True)
    block_number    = db.Column(db.Integer, nullable=False, unique=True)
    prev_hash       = db.Column(db.String(64))
    block_hash      = db.Column(db.String(64), nullable=False)
    sender_wallet   = db.Column(db.String(20), index=True)
    receiver_wallet = db.Column(db.String(20), index=True)
    amount          = db.Column(db.Float, nullable=False)
    tx_type         = db.Column(db.String(32))  # harvest/quest/trade/transfer/burn/airdrop
    note            = db.Column(db.String(256), default='')
    timestamp       = db.Column(db.DateTime, default=datetime.utcnow, index=True)

# ─── DNS SUPPLY (singleton) ───────────────────────────────────
class DNSSupply(db.Model):
    __tablename__ = 'dns_supply'
    id          = db.Column(db.Integer, primary_key=True)
    total       = db.Column(db.Float, default=1_000_000_000.0)
    circulating = db.Column(db.Float, default=0.0)
    burned      = db.Column(db.Float, default=0.0)
    locked      = db.Column(db.Float, default=1_000_000_000.0)  # belum didistribusi
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow)

# ─── DISTRIBUTION WALLETS (admin-only) ───────────────────────
class DistributionWallet(db.Model):
    """Dompet distribusi DNS — hanya bisa dilihat admin"""
    __tablename__ = 'distribution_wallets'
    id          = db.Column(db.Integer, primary_key=True)
    wallet_key  = db.Column(db.String(64), unique=True)  # gameplay_reward, ecosystem, dll
    name        = db.Column(db.String(128))
    description = db.Column(db.String(256))
    percent     = db.Column(db.Float)
    initial_amount = db.Column(db.Float)
    balance     = db.Column(db.Float)
    disbursed   = db.Column(db.Float, default=0.0)  # sudah didistribusikan ke player
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

# ─── GUILD ────────────────────────────────────────────────────
class Guild(db.Model):
    __tablename__ = 'guilds'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    leader_id   = db.Column(db.Integer, nullable=False)
    total_xp    = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    members     = db.relationship('User', backref='guild', lazy='dynamic')

# ─── TREE ─────────────────────────────────────────────────────
class UserTree(db.Model):
    __tablename__ = 'user_trees'
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tree_id         = db.Column(db.String(64), nullable=False)
    tree_name       = db.Column(db.String(128), default='Pohonku')
    xp              = db.Column(db.Integer, default=0)
    stage           = db.Column(db.Integer, default=1)
    health          = db.Column(db.Integer, default=100)
    water_today     = db.Column(db.Integer, default=0)
    pupuk_today     = db.Column(db.Integer, default=0)
    last_watered    = db.Column(db.Date, nullable=True)
    last_harvested  = db.Column(db.Date, nullable=True)
    is_active       = db.Column(db.Boolean, default=False)
    location_name   = db.Column(db.String(256), default='')
    lat             = db.Column(db.Float, nullable=True)
    lng             = db.Column(db.Float, nullable=True)
    selfie_path     = db.Column(db.String(256), default='')
    planted_at      = db.Column(db.DateTime, default=datetime.utcnow)
    total_o2        = db.Column(db.Float, default=0.0)
    rarity          = db.Column(db.String(20), default='common')
    weather_checked_date = db.Column(db.Date, nullable=True)
    weather_condition    = db.Column(db.String(20), nullable=True)  # rain/heat/normal — buat ditampilkan di UI
    
    # PERBAIKAN CASCADE MENCEGAH DATA TABRAKAN (ORPHAN DATA)
    animals         = db.relationship('UserAnimal', backref='tree', lazy='dynamic', cascade='save-update, merge')

    @property
    def animal_xp_bonus(self):
        return sum(a.xp_contribution for a in self.animals.filter_by(is_active=True))

    # ─── PERTUMBUHAN OTOMATIS (baru) ───────────────────────────
    def sync_growth(self):
        """
        Pertumbuhan pohon otomatis berbasis WAKTU sejak ditanam (planted_at):
        dalam 30 hari, pohon pasti mencapai stage maksimal (dewasa penuh),
        walaupun tidak pernah disiram/dipupuk sama sekali.

        Siram/pupuk/panen (yang menambah `xp` pohon) tetap dihitung dan bisa
        MEMPERCEPAT pertumbuhan kalau progres XP sudah melampaui progres waktu —
        jadi tombol siram & pupuk tetap punya efek nyata, bukan cuma dekorasi.

        Fungsi ini aman dipanggil berkali-kali (idempotent) dan sengaja dipanggil
        di setiap halaman/route yang menampilkan atau menyentuh pohon (dashboard,
        my-trees, gallery, siram, pupuk, panen) — sehingga pohon LAMA yang sudah
        ditanam >30 hari sebelum fitur ini ada pun otomatis ter-upgrade jadi
        dewasa begitu pertama kali dibuka lagi, tanpa perlu migrasi/skrip manual.

        Tidak menambah kolom database baru — hanya memakai `stage`, `xp`, dan
        `planted_at` yang sudah ada di tabel user_trees.
        """
        from catalog import get_tree, get_xp_progress

        td = get_tree(self.tree_id)
        if not td:
            return self.stage or 1

        max_stage = td.get("max_stage", 4) or 4
        xp_table  = td.get("xp_per_stage", []) or []
        planted   = self.planted_at or datetime.utcnow()

        elapsed_days = (datetime.utcnow() - planted).total_seconds() / 86400.0
        elapsed_days = max(0.0, elapsed_days)

        # 1) Stage berbasis waktu — otomatis penuh (max_stage) dalam 30 hari
        if max_stage > 1:
            interval = 30.0 / (max_stage - 1)
            time_stage = 1 + int(elapsed_days // interval)
        else:
            time_stage = max_stage
        time_stage = max(1, min(max_stage, time_stage))

        # 2) Stage berbasis XP (dari siram/pupuk/panen) — dipakai kalau lebih cepat
        xp_stage = get_xp_progress(self.xp, self.tree_id).get("stage", 1)

        # 3) Pakai yang tertinggi, dan stage tidak pernah mundur
        final_stage = max(time_stage, xp_stage, self.stage or 1)
        final_stage = min(final_stage, max_stage)

        if final_stage != self.stage:
            self.stage = final_stage

        # Samakan XP minimum supaya progress bar & estimasi panen di UI
        # (yang dihitung dari cat.get_xp_progress(ut.xp, ...)) konsisten
        # dengan stage hasil pertumbuhan otomatis berbasis waktu.
        if xp_table and final_stage > xp_stage:
            min_xp_needed = sum(xp_table[:final_stage - 1])
            if self.xp < min_xp_needed:
                self.xp = min_xp_needed

        return self.stage

    # ─── CUACA NYATA (baru) ─────────────────────────────────────
    def sync_weather(self):
        """
        Cek cuaca ASLI di lokasi pohon (lat/lng sungguhan dari GPS saat
        ditanam) — MAKSIMAL 1x per hari per pohon (ditandai lewat
        weather_checked_date), supaya tidak memanggil API cuaca berkali-kali
        tiap kali dashboard/route dibuka (jaga performa & tidak menambah
        latensi di luar hari pertama cek).

        Efek gameplay:
          - Cuaca hujan di lokasi pohon  -> +8 kesehatan (dianggap tersiram alami)
          - Gelombang panas & pohon belum disiram hari itu -> -5 kesehatan

        Kalau API cuaca gagal/timeout/lat-lng kosong, fungsi ini diam-diam
        tidak melakukan apa-apa — fitur ini bonus, tidak boleh sampai
        mengganggu gameplay inti (siram/pupuk/panen tetap jalan normal).

        Return: "rain" | "heat" | "normal" | None (None = belum/gagal cek)
        """
        today = date.today()
        if self.weather_checked_date == today:
            return self.weather_condition

        from weather import get_current_weather
        w = get_current_weather(self.lat, self.lng)
        if not w:
            return None

        self.weather_checked_date = today
        self.weather_condition = w["condition"]

        if w["condition"] == "rain":
            self.health = min(100, self.health + 8)
        elif w["condition"] == "heat" and (self.water_today or 0) == 0:
            self.health = max(0, self.health - 5)

        return self.weather_condition


# ─── TREE LOCATION ────────────────────────────────────────────
class TreeLocation(db.Model):
    __tablename__ = 'tree_locations'
    id              = db.Column(db.Integer, primary_key=True)
    tree_id         = db.Column(db.Integer, db.ForeignKey('user_trees.id'), unique=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'))
    lat             = db.Column(db.Float, nullable=False)
    lng             = db.Column(db.Float, nullable=False)
    location_name   = db.Column(db.String(256), default='')
    selfie_path     = db.Column(db.String(256), default='')
    planted_at      = db.Column(db.DateTime, default=datetime.utcnow)
    tree            = db.relationship('UserTree', backref='location_data', foreign_keys=[tree_id])
    user            = db.relationship('User', backref='tree_locations', foreign_keys=[user_id])

    @staticmethod
    def check_distance(lat: float, lng: float, exclude_user_id: int = None, min_meters: float = 10):
        import math
        locations = TreeLocation.query
        if exclude_user_id:
            locations = locations.filter(TreeLocation.user_id != exclude_user_id)
        locations = locations.all()
        if not locations: return True, float('inf'), None
        nearest_dist, nearest = float('inf'), None
        for loc in locations:
            R = 6371000
            phi1, phi2 = math.radians(lat), math.radians(loc.lat)
            dphi = math.radians(loc.lat - lat)
            dlam = math.radians(loc.lng - lng)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
            dist = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            if dist < nearest_dist: nearest_dist, nearest = dist, loc
        return nearest_dist >= min_meters, nearest_dist, nearest

# ─── ANIMAL ───────────────────────────────────────────────────
NEST_TYPES = {
    'kecil': {'wood':8, 'bonus':10, 'label':'Sarang Kecil'},
    'sedang':{'wood':15,'bonus':20, 'label':'Sarang Sedang'},
    'besar': {'wood':22,'bonus':35, 'label':'Sarang Besar'},
    'kastil':{'wood':40,'bonus':60, 'label':'Kastil Mini'},
}

class UserAnimal(db.Model):
    __tablename__ = 'user_animals'
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tree_id         = db.Column(db.Integer, db.ForeignKey('user_trees.id'), nullable=True)
    animal_key      = db.Column(db.String(64), nullable=False)
    nickname        = db.Column(db.String(64), default='')
    size            = db.Column(db.String(32), default='bayi')
    hunger          = db.Column(db.Integer, default=60)
    happiness       = db.Column(db.Integer, default=60)
    bond            = db.Column(db.Integer, default=10)
    xp_contribution = db.Column(db.Integer, default=0)
    nest_type       = db.Column(db.String(32), default='')
    is_active       = db.Column(db.Boolean, default=True)
    adopted_at      = db.Column(db.DateTime, default=datetime.utcnow)
    last_fed        = db.Column(db.DateTime, nullable=True)
    last_mined      = db.Column(db.DateTime, nullable=True)
    mining_session_start = db.Column(db.DateTime, nullable=True)
    mining_mode          = db.Column(db.String(10), nullable=True)  # "aman" atau "dalam" — dikunci sejak sesi dimulai

    @property
    def catalog(self):
        from catalog import ANIMAL_CATALOG
        return ANIMAL_CATALOG.get(self.animal_key, {})

    @property
    def display_name(self): 
        return self.nickname or self.catalog.get('name', self.animal_key)

    def feed(self, food_key, from_tree=False):
        """Fungsi makan yang sudah diperbaiki agar tidak tabrakan dan memiliki validasi."""
        # 1. Mencegah eksploitasi Spam (Cooldown 1 Jam)
        if self.last_fed:
            time_diff = (datetime.utcnow() - self.last_fed).total_seconds()
            if time_diff < 3600: # 3600 detik = 1 jam
                return False, "Hewan masih kenyang, tunggu beberapa saat lagi!"

        # 2. Validasi Kecocokan Makanan dari Catalog
        cat = self.catalog
        valid_foods = cat.get('foods_tree', []) if from_tree else cat.get('foods_shop', [])
        
        # Cek apakah makanan ada di daftar kesukaan hewan (jika daftarnya ada)
        if len(valid_foods) > 0 and food_key not in valid_foods:
            return False, f"{self.display_name} tidak memakan makanan jenis ini!"

        # 3. Kalkulasi Bonus berdasarkan kualitas makanan
        bonus = 1.25 if from_tree else 1.0
        add_hunger = 15
        add_happy = 5
        add_bond = 10
        
        # Mengambil efek makanan dari SHOP_ITEMS jika dari toko
        if not from_tree:
            from catalog import SHOP_ITEMS
            food_data = SHOP_ITEMS.get(food_key, {})
            rarity = food_data.get('rarity', 'common')
            
            # Dinamis sesuai rarity makanan dari toko
            if rarity == 'uncommon': add_hunger, add_happy = 20, 10
            elif rarity == 'rare': add_hunger, add_happy = 40, 15
            elif rarity == 'epic': add_hunger, add_happy = 60, 25
            elif rarity in ['legendary', 'mythic', 'divine']: 
                add_hunger, add_happy, add_bond = 100, 100, 50

        # 4. Update Status Hewan
        self.hunger    = min(100, self.hunger + int(add_hunger * bonus))
        self.happiness = min(100, self.happiness + int(add_happy * bonus))
        self.bond      = min(100, self.bond + int(add_bond * bonus))
        self.last_fed  = datetime.utcnow()
        
        # 5. Evolusi Otomatis Ukuran (Size) Berdasarkan Bond
        sizes = cat.get('sizes', ['bayi'])
        if self.bond >= 80 and len(sizes) >= 4: self.size = sizes[3]
        elif self.bond >= 50 and len(sizes) >= 3: self.size = sizes[2]
        elif self.bond >= 20 and len(sizes) >= 2: self.size = sizes[1]
        
        # 6. Hitung ulang XP Contribution
        base = cat.get('xp', 0)
        self.xp_contribution = int(base * (0.5 + self.bond/200))
        
        return True, f"Berhasil memberi makan {self.display_name}!"


# ─── MARKET ───────────────────────────────────────────────────
class MarketListing(db.Model):
    __tablename__ = 'market_listings'
    id          = db.Column(db.Integer, primary_key=True)
    seller_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_type   = db.Column(db.String(32), nullable=False)
    item_key    = db.Column(db.String(64), nullable=False)
    item_name   = db.Column(db.String(128), nullable=False)
    item_rarity = db.Column(db.String(32), default='common')
    price_dns   = db.Column(db.Float, nullable=False)
    fee_dns     = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text, default='')
    animal_id   = db.Column(db.Integer, db.ForeignKey('user_animals.id'), nullable=True)
    xp_contrib  = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    expires_at  = db.Column(db.DateTime, nullable=True)
    sold_at     = db.Column(db.DateTime, nullable=True)
    buyer_id    = db.Column(db.Integer, nullable=True)
    seller      = db.relationship('User', foreign_keys=[seller_id], backref='listings')
    @staticmethod
    def calc_fee(price): return max(1.0, round(price * 0.10, 2))

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id          = db.Column(db.Integer, primary_key=True)
    seller_id   = db.Column(db.Integer)
    buyer_id    = db.Column(db.Integer)
    listing_id  = db.Column(db.Integer, db.ForeignKey('market_listings.id'))
    item_type   = db.Column(db.String(32))
    item_key    = db.Column(db.String(64))
    price_dns   = db.Column(db.Float)
    fee_dns     = db.Column(db.Float)
    net_dns     = db.Column(db.Float)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

# ─── QUEST ────────────────────────────────────────────────────
class Quest(db.Model):
    __tablename__ = 'quests'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quest_key   = db.Column(db.String(64))
    name        = db.Column(db.String(128))
    description = db.Column(db.String(256))
    target      = db.Column(db.Integer, default=1)
    progress    = db.Column(db.Integer, default=0)
    reward_dns  = db.Column(db.Float, default=20.0)
    reward_xp   = db.Column(db.Integer, default=50)
    is_done     = db.Column(db.Boolean, default=False)
    date        = db.Column(db.Date, default=date.today)

    __table_args__ = (
        # Kombinasi (user_id, date) inilah yang selalu dipakai bareng —
        # cek quest harian user & seeding quest baru per hari.
        db.Index('ix_quests_user_date', 'user_id', 'date'),
    )

    @property
    def percent(self): return min(100, int(self.progress/max(1,self.target)*100))


class DNSOrder(db.Model):
    """Order pembelian DNS dengan transfer manual."""
    __tablename__ = 'dns_orders'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_code    = db.Column(db.String(20), unique=True, nullable=False)
    package_key   = db.Column(db.String(20), nullable=False)
    package_name  = db.Column(db.String(50), nullable=False)
    dns_amount    = db.Column(db.Integer, nullable=False)
    price_base    = db.Column(db.Integer, nullable=False)
    price_unique  = db.Column(db.Integer, nullable=False)
    unique_code   = db.Column(db.Integer, nullable=False)
    proof_path    = db.Column(db.String(200), nullable=True)
    status        = db.Column(db.String(20), default='pending')
    admin_note    = db.Column(db.String(200), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at   = db.Column(db.DateTime, nullable=True)
    user          = db.relationship('User', backref='dns_orders')

class InventoryItem(db.Model):
    __tablename__ = 'inventory'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_key    = db.Column(db.String(64), nullable=False)
    item_type   = db.Column(db.String(32), default='tool')
    quantity    = db.Column(db.Integer, default=1)
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)

class Referral(db.Model):
    """Sistem referral — ajak teman daftar dapat bonus DNS"""
    __tablename__ = 'referrals'
    id           = db.Column(db.Integer, primary_key=True)
    referrer_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    referred_id  = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    reward_given = db.Column(db.Boolean, default=False)
    referrer     = db.relationship('User', foreign_keys=[referrer_id], backref='referrals_given')
    referred     = db.relationship('User', foreign_keys=[referred_id], backref='referral_received', uselist=False)
    # Step-based reward tracking
    step1_given  = db.Column(db.Boolean, default=False)   # daftar      +200
    step2_given  = db.Column(db.Boolean, default=False)   # tanam pohon +200
    step3_given  = db.Column(db.Boolean, default=False)   # panen ke-3  +300
    harvest_count= db.Column(db.Integer, default=0)       # jumlah panen referred
    dns_reward   = db.Column(db.Float,   default=0.0)      # akumulasi bonus DNS yang sudah diberikan lewat step1-3
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

class StreakLog(db.Model):
    """Log streak login harian"""
    __tablename__ = 'streak_logs'
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    log_date = db.Column(db.Date, default=date.today, nullable=False)
    dns_bonus= db.Column(db.Float, default=0.0)

# ═══════════════════════════════════════════════════════════════════
# CHARACTER SYSTEM — fondasi avatar, skill & tas petualangan
#
# Prinsip desain: SEMUA definisi visual (sprite sheet, ukuran frame,
# animasi jalan) TIDAK disimpan di database, tapi di ASSET_PACKS
# (lihat character_catalog.py). Baris DB cuma nyimpen "pakai pack yang
# mana" (asset_pack, default 'placeholder'). Jadi kalau nanti beli/pakai
# aset pixel-art baru: cukup tambah 1 entry di character_catalog.py +
# taruh file gambar di static/ — TIDAK PERLU migrasi database maupun
# ubah kode karakter yang sudah jalan.
# ═══════════════════════════════════════════════════════════════════

class Character(db.Model):
    """Avatar per-user — posisi di dunia, penampilan, dan progres dasar."""
    __tablename__ = 'characters'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    # Lokasi di dunia game (BUKAN GPS asli — ini peta virtual terpisah)
    map_key     = db.Column(db.String(32), default='home')   # 'home' | 'forest' (masa depan) | dst
    pos_x       = db.Column(db.Integer, default=5)            # posisi grid/tile, bukan pixel
    pos_y       = db.Column(db.Integer, default=5)
    direction   = db.Column(db.String(8), default='down')     # down|up|left|right

    # Penampilan — key ke ASSET_PACKS[asset_pack]['layers'][...]
    # Placeholder sekarang cuma pakai warna, tapi struktur sudah siap
    # untuk sprite sheet berlapis (badan, rambut, baju, topi, dst).
    asset_pack  = db.Column(db.String(32), default='chibi_v1')
    sprite_variant = db.Column(db.String(16), default='female')   # 'female' | 'male' — dari ASSET_PACKS[pack]['variants']
    skin_key    = db.Column(db.String(32), default='default')
    hair_key    = db.Column(db.String(32), default='default')
    outfit_key  = db.Column(db.String(32), default='default')
    hat_key     = db.Column(db.String(32), nullable=True)     # None = tidak pakai topi

    # Stat dasar petualangan (dipakai mode hutan — fase berikutnya)
    stamina     = db.Column(db.Integer, default=100)
    stamina_max = db.Column(db.Integer, default=100)

    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow)

    skills      = db.relationship('CharacterSkill', backref='character', lazy='dynamic', cascade='all,delete')
    equipment   = db.relationship('CharacterEquipment', backref='character', lazy='dynamic', cascade='all,delete')

    def get_skill(self, skill_key):
        return self.skills.filter_by(skill_key=skill_key).first()

    def add_skill_xp(self, skill_key, amount):
        """Tambah XP skill tertentu, auto level-up. Return (skill, leveled_up)."""
        from character_catalog import SKILL_CATALOG
        sk = self.get_skill(skill_key)
        if not sk:
            sk = CharacterSkill(character_id=self.id, skill_key=skill_key, level=1, xp=0)
            db.session.add(sk)
            db.session.flush()

        info = SKILL_CATALOG.get(skill_key, {})
        max_level = info.get('max_level', 20)
        leveled_up = False
        sk.xp += amount
        while sk.level < max_level and sk.xp >= sk.level * 100:
            sk.xp -= sk.level * 100
            sk.level += 1
            leveled_up = True
        return sk, leveled_up


class CharacterSkill(db.Model):
    """Progres tiap skill petualangan (menebang, meramu, bertarung, dst)."""
    __tablename__ = 'character_skills'
    id           = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    skill_key    = db.Column(db.String(32), nullable=False)   # lihat character_catalog.SKILL_CATALOG
    level        = db.Column(db.Integer, default=1)
    xp           = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('character_id', 'skill_key', name='uq_char_skill'),
    )


class CharacterEquipment(db.Model):
    """
    Slot yang sedang dipakai karakter (tas petualangan tetap memakai
    tabel InventoryItem yang sudah ada — tabel ini cuma menandai item
    mana dari tas yang lagi 'dipakai' di slot tertentu, tanpa menduplikasi
    data item itu sendiri).
    """
    __tablename__ = 'character_equipment'
    id           = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    slot         = db.Column(db.String(16), nullable=False)   # weapon|tool|head|body|bag
    item_key     = db.Column(db.String(64), nullable=False)   # cocok dengan InventoryItem.item_key

    __table_args__ = (
        db.UniqueConstraint('character_id', 'slot', name='uq_char_slot'),
    )

class HomeDecor(db.Model):
    """Dekorasi yang ditaruh pemain di halaman rumah virtual (map_key='home')."""
    __tablename__ = 'home_decor'
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_key = db.Column(db.String(32), nullable=False)   # lihat character_catalog.DECOR_CATALOG
    pos_x    = db.Column(db.Integer, nullable=False)
    pos_y    = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'pos_x', 'pos_y', name='uq_decor_pos'),
    )

class ForestState(db.Model):
    """
    Progres harian mode petualangan hutan — titik sumber daya mana yang
    sudah 'dipanen' hari ini, dan kapan terakhir di-reset. Stamina
    sendiri tetap dari Character.stamina (di-reset ke max di sini saat
    hari berganti), jadi tidak duplikasi data.
    """
    __tablename__ = 'forest_state'
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    date           = db.Column(db.Date, default=date.today)
    consumed_nodes = db.Column(db.Text, default='')   # CSV node id, mis. "3_5,7_2,10_11"
