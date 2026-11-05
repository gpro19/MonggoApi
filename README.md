# 🚀 FastAPI MongoDB CRUD API

REST API lengkap untuk operasi CRUD (Create, Read, Update, Delete) pada MongoDB, dibangun dengan **FastAPI** dan **Motor** (async MongoDB driver). Proyek ini mendukung deployment ke platform cloud seperti **Koyeb** menggunakan **Docker**.

---

## 📋 Daftar Isi

- [Fitur](#-fitur)
- [Tech Stack](#-tech-stack)
- [Struktur Proyek](#-struktur-proyek)
- [Prasyarat](#-prasyarat)
- [Instalasi Lokal](#-instalasi-lokal)
- [Konfigurasi Environment Variables](#-konfigurasi-environment-variables)
- [Menjalankan Aplikasi](#-menjalankan-aplikasi)
- [Dokumentasi API](#-dokumentasi-api)
- [Contoh Penggunaan](#-contoh-penggunaan)
- [Deployment ke Koyeb dengan Docker](#-deployment-ke-koyeb-dengan-docker)
- [Keamanan](#-keamanan)
- [Lisensi](#-lisensi)

---

## ✨ Fitur

- ✅ **Full CRUD Operations** - Insert, Find, Update, Delete
- ✅ **Bulk Operations** - Insert many, Delete many
- ✅ **Upsert** - Update jika ada, insert jika tidak ada
- ✅ **Async/Await** - Performa tinggi dengan Motor driver
- ✅ **Auto Timestamp** - `created_at` dan `updated_at` otomatis
- ✅ **Multi-Database Support** - Akses banyak database dalam satu API
- ✅ **Multi-Collection Support** - Akses banyak collection secara dinamis
- ✅ **Token Authentication** - Proteksi endpoint dengan `x-api-token`
- ✅ **Health Check** - Monitoring koneksi MongoDB
- ✅ **Docker Ready** - Siap deploy ke Koyeb, Railway, Fly.io, dll.

---

## 🛠 Tech Stack

| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| Python | 3.11+ | Bahasa pemrograman |
| FastAPI | 0.104.1 | Web framework |
| Uvicorn | 0.24.0 | ASGI server |
| Motor | 3.3.1 | Async MongoDB driver |
| PyMongo | 4.5.0 | MongoDB driver |
| Docker | - | Containerization |

---

## 📁 Struktur Proyek
