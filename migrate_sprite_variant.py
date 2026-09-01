"""
migrate_sprite_variant.py — Jalankan SEKALI SAJA setelah update models.py ini.

Menambah kolom `sprite_variant` ke tabel `characters` yang sudah ada di
database kamu, TANPA menghapus data pemain manapun (db.create_all() tidak
bisa nambah kolom ke tabel yang sudah ada, makanya perlu skrip terpisah ini).

Cara pakai:
    cd C:\\pohonku
    python migrate_sprite_variant.py

Aman dijalankan berkali-kali — kalau kolomnya sudah ada, akan bilang
'sudah ada, dilewati' dan tidak melakukan apa-apa.
"""
from app import app
from models import db
from sqlalchemy import text, inspect

with app.app_context():
    inspector = inspect(db.engine)
    cols = [c["name"] for c in inspector.get_columns("characters")]
    if "sprite_variant" in cols:
        print("Kolom 'sprite_variant' sudah ada — dilewati, tidak ada perubahan.")
    else:
        db.session.execute(text(
            "ALTER TABLE characters ADD COLUMN sprite_variant VARCHAR(16) DEFAULT 'female'"
        ))
        db.session.commit()
        print("✓ Kolom 'sprite_variant' berhasil ditambahkan ke tabel characters.")

    # Sekalian set default pack yang benar untuk karakter yang SUDAH ada
    # (dibuat sebelum sprite asli ini terpasang, jadi masih 'placeholder')
    result = db.session.execute(text(
        "UPDATE characters SET asset_pack = 'chibi_v1' WHERE asset_pack = 'placeholder' OR asset_pack IS NULL"
    ))
    db.session.commit()
    print(f"✓ {result.rowcount} karakter lama diupdate ke pack sprite asli 'chibi_v1'.")
