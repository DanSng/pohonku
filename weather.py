"""
PohonKu — Integrasi Cuaca Nyata
================================
Pakai Open-Meteo (https://open-meteo.com) — API cuaca gratis, TANPA perlu
API key, jadi tidak nambah dependensi/config baru. Dipanggil berdasarkan
lat/lng ASLI pohon (yang sudah disimpan dari GPS saat menanam).

Desain sengaja "gagal diam-diam" (return None) kalau API cuaca down/timeout/
error apapun — fitur cuaca ini BONUS, tidak boleh sampai bikin dashboard,
siram, pupuk, atau panen ikut error/lambat gara-gara API pihak ketiga
bermasalah.
"""
import json
import urllib.request
import urllib.error

_TIMEOUT = 4  # detik — dibatasi ketat supaya tidak bikin request pemain menggantung

# Kode cuaca WMO (dipakai Open-Meteo) yang tergolong hujan/badai.
# Referensi: https://open-meteo.com/en/docs
_RAIN_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}

_HEAT_THRESHOLD_C = 34.0  # suhu dianggap "gelombang panas" buat pohon


def get_current_weather(lat, lng):
    """
    Ambil cuaca TERKINI di satu titik koordinat.

    Return dict: {"condition": "rain"|"heat"|"normal", "temp_c": float, "raw_code": int}
    Return None kalau lat/lng kosong ATAU API gagal dengan alasan apapun.
    """
    if lat is None or lng is None:
        return None
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={float(lat):.4f}&longitude={float(lng):.4f}&current_weather=true"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "PohonKu/1.0"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        cw = data.get("current_weather") or {}
        code = cw.get("weathercode")
        temp = cw.get("temperature")
        if code is None or temp is None:
            return None

        if code in _RAIN_CODES:
            condition = "rain"
        elif temp >= _HEAT_THRESHOLD_C:
            condition = "heat"
        else:
            condition = "normal"

        return {"condition": condition, "temp_c": temp, "raw_code": code}
    except Exception:
        # API down / timeout / format berubah / dll — gagal diam-diam.
        return None


# Info tampilan untuk UI (dipakai dashboard.html)
WEATHER_DISPLAY = {
    "rain":   {"emoji": "🌧️", "label": "Hujan di lokasi pohonmu", "color": "#60a8e0",
               "desc": "Pohonmu dapat siraman alami hari ini! +8 kesehatan"},
    "heat":   {"emoji": "🔥", "label": "Gelombang panas", "color": "#e05030",
               "desc": "Cuaca sangat panas di lokasi pohonmu — siram supaya kesehatan tidak turun"},
    "normal": {"emoji": "⛅", "label": "Cuaca normal", "color": "#c8a860",
               "desc": "Cuaca di lokasi pohonmu normal hari ini"},
}
