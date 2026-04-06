# 🎯 Tanlov/Registratsiya Telegram Bot (Aiogram 3)

Ushbu loyiha Telegram orqali **tanlov (event) e’lonlari**, **foydalanuvchini ro‘yxatdan o‘tkazish**, hamda **admin panel** yordamida tanlovlarni boshqarish uchun yozilgan bot.

> Eslatma: repodagi `README.txt` eski/nomuvofiq bo‘lishi mumkin. Ushbu `README.md` — loyihaning hozirgi kodiga mos hujjat.

---

## ✨ Asosiy imkoniyatlar

### Foydalanuvchi (User)
- Kanallarga **majburiy obuna tekshiruvi** (`PRIVATE_CHANNEL`, `CHANNEL_USERNAME`)
- **Ro‘yxatdan o‘tish (FSM)**: F.I.Sh → maktab → sinf → telefon (+998 format)
- **Profil**: foydalanuvchi ma’lumotlarini ko‘rish
- **Sozlamalar**: ism/maktab/sinf/tel o‘zgartirish
- **Tanlovlar**:
  - Yangi tanlovlar ro‘yxati (pagination)
  - Tanlov tafsiloti (rasm bo‘lsa rasm bilan)
  - Tanlovga ro‘yxatdan o‘tish
  - “Mening tanlovlarim” tarixi
- **Bog‘lanish (feedback)**: adminlarga xabar yuborish (admin javob qaytarishi mumkin)

### Administrator (Admin)
- `/admin` orqali admin panel
- **Bot info**: uptime, CPU/RAM, user statistikasi, token holati
- **Users**: ro‘yxat (pagination), user detail, **bloklash/blokdan chiqarish**
- **Broadcast**: barcha userlarga xabar yuborish
- **Tanlovlar (CRUD)**:
  - Qo‘shish (rasm ixtiyoriy)
  - Tahrirlash (sarlavha/tasnif/status/rasm)
  - O‘chirish
  - **Excel eksport**: tanlovga yozilganlar ro‘yxatini `.xlsx` ko‘rinishida olish

---

## 🧰 Texnologiyalar
- Python 3.10+
- Aiogram 3.x
- Async SQLAlchemy 2.x
- PostgreSQL (`asyncpg`)
- Pandas + OpenPyXL (Excel eksport)

---

## 📁 Loyihaning asosiy papkalari
- `app.py` — botni ishga tushirish (polling)
- `loader.py` — `bot` va `dp` (Dispatcher)
- `handlers/users/` — foydalanuvchi handlerlari
- `handlers/admins/` — admin handlerlari
- `database/` — SQLAlchemy modellari va DB engine/session
- `database/orm_query.py` — DB query/CRUD funksiyalar
- `middlewares/db.py` — har update uchun DB session middleware
- `keyboards/` — inline/reply klaviaturalar
- `states/` — FSM state’lar

---

## ⚙️ Sozlash (Environment)

Loyiha `environs` orqali `.env` dan o‘qiydi. Minimal kerak bo‘ladigan o‘zgaruvchilar:

- `BOT_TOKEN` — Telegram bot token
- `DB_URL` — PostgreSQL async URL  
  Misol: `postgresql+asyncpg://user:password@localhost:5432/db`
- `ADMINS` — admin telegram ID lar ro‘yxati (vergul bilan)  
  Misol: `ADMINS=123456789,987654321`
- `PRIVATE_CHANNEL` — majburiy obuna qilinadigan kanal ID lar (vergul bilan)  
  Misol: `PRIVATE_CHANNEL=-1001234567890,-1009876543210`
- `CHANNEL_USERNAME` — yuqoridagi kanallarning username’lari (vergul bilan)  
  Misol: `CHANNEL_USERNAME=@my_channel_1,@my_channel_2`

> `database/config.py` da qo‘shimcha keylar ham bor (`OPENWEATHER_*`, `LOCATIONIQ_*`), lekin ushbu repo’dagi registratsiya/tanlov logikasida ular ishlatilmasligi mumkin.

---

## 🚀 Ishga tushirish

1) Virtual muhit (ixtiyoriy, tavsiya qilinadi)

```bash
python -m venv venv
source venv/bin/activate
```

2) Kutubxonalarni o‘rnatish

```bash
pip install -r requirements.txt
```

3) `.env` faylini to‘ldiring (yuqoridagi bo‘limga qarang)

4) Botni ishga tushirish

```bash
python app.py
```

`app.py` ishga tushganda `database/engine.py` orqali jadval(lar) `create_all` bilan yaratiladi.

---

## 🧪 Foydali buyruqlar
- `/start` — user flow
- `/admin` — admin panel (faqat `ADMINS` dagilar uchun)

---

## 🔐 Xavfsizlik eslatmalari
- `.env` ni repoga qo‘shmang.
- `BOT_TOKEN` va `DB_URL` kabi maxfiy ma’lumotlarni oshkor qilmang.

---

## 👤 Muallif
Sayfulloh Mamatqulov

