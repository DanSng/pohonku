import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY          = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH  = 16 * 1024 * 1024
    DNS_TOTAL_SUPPLY    = 1_000_000_000
    DNS_AIRDROP_TIER1   = 1000   # pemain 1-100
    DNS_AIRDROP_TIER2   = 500    # pemain 101-1000
    DNS_AIRDROP_TIER3   = 100    # pemain 1001+
    DNS_BURN_RATE       = 0.01   # 1% setiap transaksi P2P
    TREE_MIN_DISTANCE   = 10     # meter
    PREFERRED_URL_SCHEME = 'https'
    PROXY_FIX           = True
    # Session security
    SESSION_COOKIE_SECURE   = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 jam

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pohonku_v3_dev.db'
    PREFERRED_URL_SCHEME = 'http'
    PROXY_FIX = False

class ProductionConfig(Config):
    DEBUG = False
    _db = os.environ.get('DATABASE_URL', 'sqlite:///pohonku_v3.db')
    if _db.startswith('postgres://'): _db = _db.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
