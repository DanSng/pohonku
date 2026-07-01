@echo off
title PohonKu v3 - Cloudflare Tunnel
color 0B
echo.
echo  Mengecek server lokal...
curl -s http://localhost:5000 >nul 2>&1
if errorlevel 1 (
  echo [!] Server belum jalan! Buka MULAI.bat dulu.
  pause & exit
)
echo  Membuka tunnel...
echo  Tunggu URL muncul di bawah, lalu bagikan ke pemain!
echo.
cloudflared tunnel --url http://localhost:5000
pause
