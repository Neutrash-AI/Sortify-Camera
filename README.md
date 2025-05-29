## 🎥 Sortify Camera – Dokumentasi Servis Python untuk Klasifikasi Sampah

### 🧩 Deskripsi Umum

**Sortify Camera** adalah servis Python yang berfungsi untuk:

- Mengambil gambar dari kamera (webcam laptop atau ESP32-CAM).
- Melakukan klasifikasi sampah menjadi kategori **organik** atau **recycle** menggunakan model AI.
- Mengirimkan hasil klasifikasi ke:

  - **Backend** untuk penyimpanan dan analisis data.
  - **Frontend** untuk visualisasi real-time.
  - **ESP32** untuk menggerakkan servo berdasarkan hasil klasifikasi.

### 🔀 Arsitektur Komunikasi

```
[ Kamera (Webcam/ESP32-CAM) ]
           │
           ▼
[ Servis Python (Sortify Camera) ]
           │
           ├──> [ Backend (via Redis) ]
           │
           ├──> [ Frontend (via Socket.IO) ]
           │
           └──> [ ESP32 (via Serial) ]
```

### 🌿 Mode Operasi

- **Branch `v1-webcam`**: Menggunakan **OpenCV** untuk mengambil gambar dari webcam laptop.
- **Branch `main`**: Menggunakan **ESP32-CAM** yang mengirimkan data gambar melalui **serial**, mengurangi beban komputasi pada perangkat seperti Raspberry Pi.

### 🚀 Alur Kerja

1. **Pengambilan Gambar**:

   - `v1-webcam`: Menggunakan OpenCV untuk menangkap gambar dari webcam.
   - `main`: Menerima data gambar dari ESP32-CAM melalui serial.

2. **Klasifikasi Gambar**:

   - Gambar yang diterima diproses oleh model AI untuk menentukan kategori sampah.

3. **Pengiriman Hasil**:

   - Hasil klasifikasi dikirim ke backend dan frontend melalui Socket.IO.
   - Instruksi untuk menggerakkan servo dikirim ke ESP32 melalui komunikasi serial.

### 🔧 Konfigurasi

- **Model AI**: Dapat disesuaikan sesuai kebutuhan proyek.
- **Threshold Confidence**:

  - **Recycle**: >91%
  - **Organik**: >40%

- **Port Serial**: Pastikan port serial yang digunakan sesuai dengan konfigurasi ESP32.

### 📈 Peningkatan Mendatang

- **Optimasi Performa**: Mengurangi penggunaan OpenCV dengan mengandalkan ESP32-CAM untuk pengambilan gambar.

## 🚀 Happy Coding!
