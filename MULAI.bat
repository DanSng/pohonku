@echo off
title PohonKu v3 - Server
color 0A
echo.
echo  ================================================
echo    PohonKu v3 - Blockchain DNS Token Game
echo  ================================================
echo.

:: Cek Python
python --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python tidak ditemukan!
  echo Download di python.org - centang "Add to PATH"
  pause & exit
)

:: Install library jika belum ada
pip show flask >nul 2>&1
if errorlevel 1 (
  echo Menginstall library...
  pip install -r requirements.txt -q
)

:: Install pycryptodome untuk enkripsi backup
pip show pycryptodome >nul 2>&1
if errorlevel 1 (
  pip install pycryptodome -q
  echo [+] pycryptodome terinstall
)

:: Buat .env jika belum ada
if not exist .env (
  echo SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%pohonku_v3_production > .env
  echo DATABASE_URL=sqlite:///pohonku_v3.db >> .env
  echo FLASK_ENV=production >> .env
  echo ADMIN_PASSWORD=admin123 >> .env
  echo PORT=5000 >> .env
  echo GMAIL_USER= >> .env
  echo GMAIL_PASS= >> .env
  echo DB_BACKUP_PASSWORD=gantiDenganPasswordKuat >> .env
  echo ADMIN_EMAIL=daniel.blessed@gmail.com >> .env
  echo.
  echo [!] File .env dibuat. Buka dan isi GMAIL_USER, GMAIL_PASS, DB_BACKUP_PASSWORD
  echo     sebelum server dijalankan ke publik!
  echo.
)

:: Buat folder backup
if not exist backups mkdir backups
if not exist backups\encrypted mkdir backups\encrypted
if not exist static\uploads\proofs mkdir static\uploads\proofs

echo.
echo  ================================================
echo    Admin: admin@pohonku.game / admin123
echo    URL:   http://localhost:5000
echo    Admin: http://localhost:5000/admin
echo    Keamanan: http://localhost:5000/admin/security
echo    Toko DNS: http://localhost:5000/shop/dns
echo    Backup otomatis: jam 16:00 WIB setiap hari
echo  ================================================
echo.
echo  *** Jangan tutup jendela ini! ***
echo  *** Buka CLOUDFLARE.bat di jendela TERPISAH untuk tunnel ***
echo.

python app.py
pause
