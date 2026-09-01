import os, random
from datetime import datetime, date
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from config import config
from models import db, User, Wallet, Quest, DNSSupply, DistributionWallet
from blockchain import wallet_address, genesis_hash
import catalog as cat

def create_app(env='production'):
    app = Flask(__name__)
    app.config.from_object(config[env])

    if app.config.get('PROXY_FIX'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    Migrate(app, db)

    lm = LoginManager(app)
    lm.login_view = 'auth.login'
    lm.login_message = ''

    @lm.user_loader
    def load_user(uid): return User.query.get(int(uid))

    @app.context_processor
    def inject_globals():
        # --- PERBAIKAN RANKING ---
        # Fungsi ini di-inject secara global, dipanggil hanya saat halaman butuh ranking
        def get_leaderboards():
            # 1. Ranking XP (Tanpa N+1, ambil 10 teratas)
            top_xp = User.query.filter_by(role='user', is_banned=False)\
                         .order_by(User.level.desc(), User.xp.desc())\
                         .limit(10).all()
                         
            # 2. Ranking DNS (JOIN langsung dengan Wallet agar memori tidak crash)
            top_dns = db.session.query(User).join(Wallet)\
                          .filter(User.role == 'user', User.is_banned == False)\
                          .order_by(Wallet.balance.desc())\
                          .limit(10).all()
                          
            # 3. Ranking O2 Kumulatif
            top_o2 = User.query.filter_by(role='user', is_banned=False)\
                         .order_by(User.o2_total.desc())\
                         .limit(10).all()
            
            return {"top_xp": top_xp, "top_dns": top_dns, "top_o2": top_o2}

        return dict(cat=cat, NEST_TYPES=__import__('models').NEST_TYPES,
                    now=datetime.utcnow(), today=date.today(),
                    get_leaderboards=get_leaderboards)

    # Register blueprints
    from routes.auth   import auth_bp
    from routes.main   import main_bp
    from routes.tree   import tree_bp
    from routes.animal import animal_bp
    from routes.market import market_bp
    from routes.wallet import wallet_bp
    from routes.api    import api_bp
    from routes.admin  import admin_bp
    
    # Blueprint opsional — tidak crash jika file tidak ada
    try:
        from routes.leaderboard import lb_bp
        app.register_blueprint(lb_bp)
    except Exception as e:
        print(f'[skip] leaderboard_bp: {e}')
    try:
        from routes.rimba_run import rimba_bp
        app.register_blueprint(rimba_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] rimba_bp: {e}')
        
    try:
        from routes.story import story_bp
        app.register_blueprint(story_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] story_bp: {e}')
        
    try:
        from routes.benih_blast import blast_bp
        app.register_blueprint(blast_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] blast_bp: {e}')

    try:
        from routes.merge_benih import merge_bp
        app.register_blueprint(merge_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] merge_bp: {e}')

    try:
        from routes.lari_hutan import lari_bp
        app.register_blueprint(lari_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] lari_bp: {e}')
        
    try:
        from routes.streak import streak_bp
        app.register_blueprint(streak_bp, url_prefix='')
    except Exception as e:
        print(f"[skip] streak_bp: {e}")
        
    try:
        from routes.wallet_pin import pin_bp
        app.register_blueprint(pin_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] pin_bp: {e}')
        
    try:
        from routes.dns_shop import shop_bp
        app.register_blueprint(shop_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] shop_bp: {e}')
        
    try:
        from routes.proximity import prox_bp
        app.register_blueprint(prox_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] prox_bp: {e}')
        
    try:
        from routes.pubmap import pubmap_bp
        app.register_blueprint(pubmap_bp, url_prefix='')
    except Exception as e:
        print(f"[skip] pubmap_bp: {e}")

    try:
        from routes.mining import mining_bp
        app.register_blueprint(mining_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] mining_bp: {e}')

    try:
        from routes.character import character_bp
        app.register_blueprint(character_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] character_bp: {e}')

    try:
        from routes.forest import forest_bp
        app.register_blueprint(forest_bp, url_prefix='')
    except Exception as e:
        print(f'[skip] forest_bp: {e}')

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tree_bp,   url_prefix='/tree')
    app.register_blueprint(animal_bp, url_prefix='/animal')
    app.register_blueprint(market_bp, url_prefix='/market')
    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    app.register_blueprint(api_bp,    url_prefix='/api')
    app.register_blueprint(admin_bp,  url_prefix='/admin')

    @app.template_filter('format_num')
    def format_num(value):
        try: return f"{int(value):,}".replace(',','.')
        except: return str(value)

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    @app.route('/sw.js')
    def service_worker():
        from flask import send_from_directory
        return send_from_directory('static', 'sw.js',
            mimetype='application/javascript')

    with app.app_context():
        db.create_all()
        _init_system()

    # Alarm backup jam 16:00 WIB — daemon thread, tidak ganggu server
    try:
        from routes.backup_alarm import start_backup_alarm
        start_backup_alarm()
    except Exception as e:
        print(f'[skip] backup_alarm: {e}')

    return app

def _init_system():
    """Inisialisasi sistem: admin, DNS supply, distribution wallets, quest."""
    # Admin
    if not User.query.filter_by(role='admin').first():
        admin_pw = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin = User(email='admin@pohonku.game', username='admin',
                     role='admin', level=99)
        admin.set_password(admin_pw)
        db.session.add(admin)
        db.session.flush()
        w = Wallet(user_id=admin.id,
                   address=wallet_address(admin.id, 'admin'),
                   balance=0.0)
        db.session.add(w)
        print(f"[PohonKu] Admin dibuat — login: admin@pohonku.game / {admin_pw}")

    # DNS Supply
    if not DNSSupply.query.first():
        db.session.add(DNSSupply())
        print("[PohonKu] DNS Supply diinisialisasi: 1,000,000,000 DNS")

    # Distribution Wallets
    if not DistributionWallet.query.first():
        for key, d in cat.DNS_DISTRIBUTION.items():
            dw = DistributionWallet(
                wallet_key=key, name=d['name'],
                description=d['desc'], percent=d['percent'],
                initial_amount=d['amount'], balance=d['amount'],
            )
            db.session.add(dw)
        print("[PohonKu] Distribution Wallets dibuat (6 wallet)")

    # Quest harian
    _seed_daily_quests()
    db.session.commit()

def _seed_daily_quests():
    today = date.today()
    QUESTS = [
        {"key":"water_3",    "name":"Penjaga Air",   "desc":"Siram pohon 3x hari ini",  "target":3,"dns":200,"xp":80},
        {"key":"harvest_1",  "name":"Petani Sejati",  "desc":"Panen pohon 1x hari ini",  "target":1,"dns":100,"xp":40},
        {"key":"feed_animal","name":"Pecinta Hewan",  "desc":"Beri makan hewan 2x",      "target":2,"dns":120,"xp":50},
        {"key":"guild_visit","name":"Jiwa Sosial",    "desc":"Kunjungi pohon guild",      "target":3,"dns":150,"xp":60},
    ]
    for u in User.query.filter_by(role='user', is_banned=False).all():
        if Quest.query.filter_by(user_id=u.id, date=today).count() == 0:
            for q in QUESTS:
                db.session.add(Quest(user_id=u.id, quest_key=q['key'],
                    name=q['name'], description=q['desc'],
                    target=q['target'], reward_dns=q['dns'], reward_xp=q['xp'], date=today))

env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=(env == 'development'))
