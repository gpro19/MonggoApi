# Gunakan image Python resmi yang ringan
FROM python:3.11-slim

# Tentukan working directory di dalam container
WORKDIR /app

# Salin requirements.txt terlebih dahulu agar caching lebih efisien
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi
COPY . .

# Ekspos port yang akan digunakan (Koyeb akan mendeteksi ini, tapi praktik yang baik untuk mendokumentasikannya)
EXPOSE 8000

# Perintah untuk menjalankan aplikasi
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
