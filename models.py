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
    role            = db.Column(db.String(16), default='user')  # user|admin
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
    is_banned       = db.Column(db.Boolean, default=False)
    onboarding_done = db.Column(db.Boolean, default=False)
    verified       = db.Column(db.Boolean, default=True)   # auto verified, tidak perlu approval admin

    wallet      = db.relationship('Wallet', backref='user', uselist=False, cascade='all,delete')
    trees       = db.relationship('UserTree', backref='owner', lazy='dynamic', cascade='all,delete')
    animals     = db.relationship('UserAnimal', backref='owner', lazy='dynamic', cascade='all,delete')
    quests      = db.relationship('Quest', backref='user', lazy='dynamic', cascade='all,delete')
    inventory   = db.relationship('InventoryItem', backref='owner', lazy='dynamic', cascade='all,delete')

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
    balance     = db.Column(db.Float, default=0.0)
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
    # ── Keamanan wallet ──────────────────────────


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
    sender_wallet   = db.Column(db.String(20))
    receiver_wallet = db.Column(db.String(20))
    amount          = db.Column(db.Float, nullable=False)
    tx_type         = db.Column(db.String(32))  # harvest/quest/trade/transfer/burn/airdrop
    note            = db.Column(db.String(256), default='')
    timestamp       = db.Column(db.DateTime, default=datetime.utcnow)

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
    # ── Keamanan wallet ──────────────────────────


# ─── GUILD ────────────────────────────────────────────────────
class Guild(db.Model):
    __tablename__ = 'guilds'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    leader_id   = db.Column(db.Integer, nullable=False)
    total_xp    = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    # ── Keamanan wallet ──────────────────────────

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
    rarity      = db.Column(db.String(20), default='common')
    animals         = db.relationship('UserAnimal', backref='tree', lazy='dynamic')

    @property
    def animal_xp_bonus(self):
        return sum(a.xp_contribution for a in self.animals.filter_by(is_active=True))

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

    @property
    def catalog(self):
        from catalog import ANIMAL_CATALOG
        return ANIMAL_CATALOG.get(self.animal_key, {})
    @property
    def display_name(self): return self.nickname or self.catalog.get('name', self.animal_key)

    def feed(self, food, from_tree=False):
        bonus = 1.25 if from_tree else 1.0
        self.hunger    = min(100, self.hunger + int(15*bonus))
        self.happiness = min(100, self.happiness + 5)
        self.bond      = min(100, self.bond + int(10*bonus))
        self.last_fed  = datetime.utcnow()
        base = self.catalog.get('xp', 0)
        self.xp_contribution = int(base * (0.5 + self.bond/200))

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
    # ── Keamanan wallet ──────────────────────────

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
    # ── Keamanan wallet ──────────────────────────


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
    dns_reward   = db.Column(db.Float, default=500.0)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    referrer     = db.relationship('User', foreign_keys=[referrer_id], backref='referrals_given')
    referred     = db.relationship('User', foreign_keys=[referred_id], backref='referral_received', uselist=False)
    # Step-based reward tracking
    step1_given  = db.Column(db.Boolean, default=False)   # daftar      +200
    step2_given  = db.Column(db.Boolean, default=False)   # tanam pohon +200
    step3_given  = db.Column(db.Boolean, default=False)   # panen ke-3  +300
    harvest_count= db.Column(db.Integer, default=0)       # jumlah panen referred
    dns_reward   = db.Column(db.Float,   default=0.0)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

class StreakLog(db.Model):
    """Log streak login harian"""
    __tablename__ = 'streak_logs'
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    log_date = db.Column(db.Date, default=date.today, nullable=False)
    dns_bonus= db.Column(db.Float, default=0.0)
