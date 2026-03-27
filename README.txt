# 🌦 Location-Based Weather Telegram Bot

## 📌 Description

This Telegram bot shows **current weather information** based on the **user’s location**.
The user sends their location, and the bot returns weather details with **AI-based advice**.

---

## ⚙️ How It Works

1. User sends location
2. Bot detects address (reverse geocoding)
3. Weather data is fetched from API
4. AI analyzes conditions and gives advice
5. Result is sent to the user
6. Data is cached in Redis for faster responses

---

## ✨ Features

* 📍 Location-based weather
* 🌡 Temperature & conditions
* 🤖 AI weather analysis
* 🔄 Refresh weather button
* 📦 Redis caching (30 minutes)
* 🧠 Daily AI request limit
* ⚡ Fully async architecture

---

## 🛠 Technologies

* Python 3.10+
* Aiogram 3.x
* Async SQLAlchemy
* Redis
* Aiohttp
* FSM (Finite State Machine)

---

## 🌐 APIs Used

* OpenWeather API – weather data
  [https://openweathermap.org/](https://openweathermap.org/)
* LocationIQ API – reverse geocoding
  [https://locationiq.com/](https://locationiq.com/)

---

## 👨‍💻 Author

Sayfulloh Mamatqulov
Backend & Telegram Bot Developer

---

## 🚀 Future Plans

* Weather forecast
* Multi-language support
* Weather alerts
