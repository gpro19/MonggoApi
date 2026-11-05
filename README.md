📘 README.md

Berikut adalah file README.md yang lengkap dan siap pakai untuk proyek Anda:

```markdown
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

```

.
├── main.py              # File utama aplikasi FastAPI
├── requirements.txt     # Daftar dependencies Python
├── Dockerfile           # Konfigurasi Docker image
├── Procfile             # (Opsional) Untuk platform non-Docker
├── README.md            # Dokumentasi proyek
└── .env                 # (Lokal) Environment variables - JANGAN di-commit!

```

---

## 📦 Prasyarat

Sebelum memulai, pastikan Anda sudah memiliki:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **MongoDB Atlas Account** ([Daftar gratis](https://www.mongodb.com/cloud/atlas))
- **Git** ([Download](https://git-scm.com/))
- **Docker** ([Download](https://www.docker.com/)) - untuk deployment
- **Akun Koyeb** ([Daftar gratis](https://www.koyeb.com/)) - untuk hosting

---

## 💻 Instalasi Lokal

### 1. Clone Repositori

```bash
git clone https://github.com/username/your-repo.git
cd your-repo
```

2. Buat Virtual Environment (Opsional tapi Direkomendasikan)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. Setup Environment Variables

Buat file .env di root proyek:

```env
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MY_SECRET_TOKEN=YourSecretTokenHere
```

⚠️ Jangan pernah commit file .env ke Git! Pastikan sudah masuk .gitignore.

Buat file .gitignore:

```gitignore
# Environment
.env
.env.*

# Python
__pycache__/
*.pyc
venv/
.venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

⚙️ Konfigurasi Environment Variables

Variable Deskripsi Contoh
MONGO_URI Connection string MongoDB Atlas mongodb+srv://user:pass@cluster.mongodb.net/
MY_SECRET_TOKEN Token rahasia untuk autentikasi API MySecretToken12345

Cara Mendapatkan MongoDB URI

1. Login ke MongoDB Atlas
2. Pilih cluster Anda → Connect
3. Pilih Drivers → Python
4. Copy connection string mongodb+srv://...
5. Ganti <password> dengan password user MongoDB Anda

💡 Tips: Buat user database khusus di MongoDB Atlas (Database Access) dengan role Read and Write to any database.

---

▶️ Menjalankan Aplikasi

Mode Development (dengan auto-reload)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Mode Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Aplikasi akan berjalan di: http://localhost:8000

---

📚 Dokumentasi API

Setelah aplikasi berjalan, buka dokumentasi interaktif otomatis:

· Swagger UI: http://localhost:8000/docs
· ReDoc: http://localhost:8000/redoc

Ringkasan Endpoint

Semua endpoint memerlukan header x-api-token:

Method Endpoint Deskripsi
POST /{db}/{collection}/insert Insert satu dokumen
POST /{db}/{collection}/insert-many Insert banyak dokumen
GET /{db}/{collection}/find Cari dokumen dengan filter
GET /{db}/{collection}/{id} Cari dokumen berdasarkan ID
POST /{db}/{collection}/upsert Update atau insert (upsert)
PUT /{db}/{collection}/update Update dokumen
DELETE /{db}/{collection}/delete Hapus satu dokumen
DELETE /{db}/{collection}/delete-many Hapus banyak dokumen
GET / Health check

---

🧪 Contoh Penggunaan

Ganti https://your-app.koyeb.app dengan URL aplikasi Anda (atau http://localhost:8000 untuk lokal).

1. Health Check

```bash
curl https://your-app.koyeb.app/
```

2. Insert Data

```bash
curl -X POST https://your-app.koyeb.app/mydb/users/insert \
  -H "Content-Type: application/json" \
  -H "x-api-token: MySecretToken12345" \
  -d '{
    "document": {
      "name": "Galeh",
      "email": "galeh@example.com",
      "age": 25
    }
  }'
```

3. Insert Many Data

```bash
curl -X POST https://your-app.koyeb.app/mydb/users/insert-many \
  -H "Content-Type: application/json" \
  -H "x-api-token: MySecretToken12345" \
  -d '{
    "documents": [
      {"name": "Alice", "age": 22},
      {"name": "Bob", "age": 28}
    ]
  }'
```

4. Find Data

```bash
# Tanpa filter
curl -X GET "https://your-app.koyeb.app/mydb/users/find?limit=10" \
  -H "x-api-token: MySecretToken12345"

# Dengan filter (URL encoded)
curl -X GET "https://your-app.koyeb.app/mydb/users/find?filter=%7B%22age%22%3A%7B%22%24gt%22%3A20%7D%7D" \
  -H "x-api-token: MySecretToken12345"
```

5. Find By ID

```bash
curl -X GET https://your-app.koyeb.app/mydb/users/6543210fedcba9876543210 \
  -H "x-api-token: MySecretToken12345"
```

6. Update (Upsert)

```bash
curl -X POST https://your-app.koyeb.app/mydb/users/upsert \
  -H "Content-Type: application/json" \
  -H "x-api-token: MySecretToken12345" \
  -d '{
    "filter": {"email": "galeh@example.com"},
    "data": {"age": 26}
  }'
```

7. Update (Existing Only)

```bash
curl -X PUT https://your-app.koyeb.app/mydb/users/update \
  -H "Content-Type: application/json" \
  -H "x-api-token: MySecretToken12345" \
  -d '{
    "filter": {"email": "galeh@example.com"},
    "data": {"age": 27}
  }'
```

8. Delete Satu Dokumen

```bash
curl -X DELETE https://your-app.koyeb.app/mydb/users/delete \
  -H "Content-Type: application/json" \
  -H "x-api-token: MySecretToken12345" \
  -d '{
    "filter": {"email": "galeh@example.com"}
  }'
```

9. Delete Banyak Dokumen

```bash
curl -X DELETE https://your-app.koyeb.app/mydb/users/delete-many \
  -H "Content-Type: application/json" \
  -H "x-api-token: MySecretToken12345" \
  -d '{
    "filter": {"age": {"$lt": 18}}
  }'
```

---

🐳 Deployment ke Koyeb dengan Docker

1. Siapkan Dockerfile

File Dockerfile sudah disertakan di repositori:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Push ke GitHub

```bash
git add .
git commit -m "Ready for Koyeb deployment"
git push origin main
```

3. Deploy di Koyeb

1. Login ke Koyeb Dashboard
2. Klik Create Service → GitHub
3. Pilih repositori proyek ini
4. Konfigurasi:
   · Builder: Dockerfile
   · Port: 8000
   · Instance: Nano (free tier) atau lebih tinggi
5. Tambahkan Environment Variables:
   · MONGO_URI = connection string MongoDB Anda
   · MY_SECRET_TOKEN = token rahasia pilihan Anda
6. Klik Deploy 🚀

4. Testing Deployment

```bash
curl https://your-app-name.koyeb.app/
```

5. Testing Lokal dengan Docker

```bash
# Build image
docker build -t fastapi-mongo-crud .

# Run container
docker run -p 8000:8000 \
  -e MONGO_URI="mongodb+srv://..." \
  -e MY_SECRET_TOKEN="MySecretToken12345" \
  fastapi-mongo-crud
```

---

🔐 Keamanan

⚠️ Penting

1. JANGAN hardcode kredensial di kode (main.py). Selalu gunakan environment variables.
2. JANGAN commit file .env ke repositori publik.
3. Ganti MY_SECRET_TOKEN dengan string acak yang kuat (misal: hasil dari openssl rand -hex 32).
4. Gunakan password MongoDB yang kuat dan jangan gunakan password yang sama dengan username.
5. Batasi IP Whitelist di MongoDB Atlas (Network Access) sesuai kebutuhan.
6. Aktifkan HTTPS di production (Koyeb sudah otomatis menyediakan HTTPS).

Generate Token yang Aman

```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

Contoh Implementasi Aman di Kode

```python
import os

MONGO_URI = os.getenv("MONGO_URI")
MY_SECRET_TOKEN = os.getenv("MY_SECRET_TOKEN")

if not MONGO_URI or not MY_SECRET_TOKEN:
    raise ValueError("Environment variables MONGO_URI dan MY_SECRET_TOKEN wajib diisi!")
```

---

🐛 Troubleshooting

Masalah Solusi
ServerSelectionTimeoutError Periksa koneksi internet & IP whitelist MongoDB Atlas
401 Unauthorized Pastikan header x-api-token sesuai dengan MY_SECRET_TOKEN
400 Filter format invalid Filter harus JSON valid dan di-URL-encode
Build Docker gagal Pastikan requirements.txt tidak ada typo & versi kompatibel
Aplikasi timeout di Koyeb Periksa apakah port sudah 0.0.0.0:8000 di CMD Dockerfile

---

📄 Lisensi

Proyek ini dilisensikan di bawah MIT License — bebas digunakan untuk keperluan pribadi maupun komersial.

---

👤 Author

Galeh — @username

---

🙏 Kontribusi

Pull request sangat dipersilakan! Untuk perubahan besar, silakan buka issue terlebih dahulu untuk mendiskusikan apa yang ingin diubah.

---

⭐ Dukungan

Jika proyek ini bermanfaat, jangan lupa berikan bintang ⭐ di repositori GitHub!

```

---

## 💡 Tips Tambahan

Setelah membuat file `README.md`, ada beberapa hal yang sebaiknya Anda lakukan:

### 1. Tambahkan File `.gitignore` (Penting!)

```gitignore
# Environment & Secrets
.env
.env.*
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

2. Ganti Placeholder

Di README di atas, ganti placeholder berikut dengan data asli Anda:

· https://github.com/username/your-repo.git → URL repo Anda
· your-app.koyeb.app → URL Koyeb Anda
· @username → username GitHub Anda

3. Tambahkan Badge (Opsional)

Di bagian atas README, Anda bisa menambahkan badge agar terlihat profesional:

```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen.svg)
![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

4. Screenshot Swagger UI (Opsional)

Tambahkan screenshot dokumentasi Swagger UI untuk membuat README lebih menarik:

```markdown
## 📸 Preview

![Swagger UI](docs/swagger-preview.png)
```

---

README ini sudah mencakup semua aspek penting: instalasi, konfigurasi, penggunaan API, deployment Docker ke Koyeb, hingga catatan keamanan. Anda tinggal menyesuaikan placeholder dan langsung push ke GitHub! 🚀
