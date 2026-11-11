# Modifikasi Game Brick Breaker (Tkinter OOP)
**Tugas Topic 9: Implementasi OOP di GUI Programming**

---

### 👤 Identitas Mahasiswa
* **Nama**: Ilham Saputra
* **NIM**: 20240140118
* **Kelas**: D
* **Mata Kuliah**: Pemrograman Multiplatform
* **Repository GitHub**: [ModifyGameBrickBreaker_118](https://github.com/Mahl11/ModifyGameBrickBreaker_118)

---

## 📸 Tangkapan Layar Tampilan Modifikasi

Berikut adalah tampilan antarmuka game *Brick Breaker* yang telah dimodifikasi dengan gaya visual *Modern Dark Arcade*:

![Tampilan Modifikasi Game Brick Breaker](screenshots/tampilan_modifikasi.png)

---

## 🔄 Rangkuman Perubahan & Modifikasi

Game ini dikembangkan dan dimodifikasi dari referensi awal [Hackster.io - Make Your Own BrickBreaker Using Python](https://www.hackster.io/trivediswap25/make-your-own-brickbreaker-using-python-28c674). Berikut adalah perbandingan fitur bawaan (default) vs modifikasi:

| Fitur / Komponen | Versi Bawaan (Default Referensi) | Versi Modifikasi (Proyek Ini) |
| :--- | :--- | :--- |
| **Tema & Visual** | Latar biru pastel (`#aaaaff`), paddle kuning, bola putih polos. | Tema *Dark Arcade* (`#1a1a2e`), paddle neon cyan (`#00d2d3`), bola emas menyala (`#feca57`), palet bata neon kontras. |
| **HUD & Tipografi** | Font `Forte` kaku, hanya teks biasa `Lives: 3`. | Font modern `Segoe UI Bold`, header HUD rapi dengan pemisah garis, skor, level, dan nyawa simbol hati (`❤️ ❤️ ❤️`). |
| **Sistem Penilaian (Score)** | Tidak ada skor (hanya menang/kalah). | Sistem skor dinamis: +10 tiap pantulan bata, +25 saat bata hancur, +100 bonus tamat level, serta pelacak *High Score*. |
| **Kontrol Pemain** | Hanya tombol panah `<Left>` dan `<Right>`. | Kontrol ganda: Tombol panah (`<-` / `->`) dan tombol `A` / `D` (ramah keyboard gaming). |
| **Fitur Pause & Restart** | Tidak ada fitur pause maupun restart instan. | Fitur Jeda permainan (`[P] Pause/Resume`) dan Mulai Ulang instan (`[R] Quick Restart`). |
| **Progresi Multi-Level** | Hanya 1 level statis (3 baris bata). | Multi-level (Level 1 & Level 2): Level 2 menyajikan 4 baris bata rapat dengan bata emerald (3x ketahanan) dan kecepatan bola meningkat. |

---

## 🎮 Penjelasan Detail Modifikasi

### 1. Desain Visual Modern (Dark Arcade Mode)
- Latar belakang canvas diubah menjadi warna gelap elegan (`#1a1a2e`) untuk mengurangi ketegangan mata dan memberikan nuansa arcade retro modern.
- Paddle pemain diberi aksen warna Neon Cyan (`#00d2d3`) dengan garis tepi biru elektrik (`#54a0ff`).
- Bola permainan diberi warna Glowing Gold (`#feca57`) dengan outline oranye arcade (`#ff9f43`).
- Bata menggunakan gradasi warna neon kontras: Coral Red (`#ff6b6b`, 1-hit), Sky Cyan (`#48dbfb`, 2-hit), dan Emerald Green (`#1dd1a1`, 3-hit).

### 2. Sistem Skor & High Score
- Setiap kali bola mengenai bata sasaran, pemain memperoleh +10 poin.
- Ketika bata berhasil dihancurkan hingga pecah, pemain memperoleh bonus +25 poin.
- Menyelesaikan seluruh level memberikan bonus ekstra +100 poin.
- Skor tertinggi (*High Score*) secara otomatis tercatat dan diperbarui selama sesi bermain.

### 3. Indikator Nyawa Simbol Hati (Heart HUD)
- Menggantikan teks monoton `Lives: 3` dengan visualisasi simbol hati (`❤️ ❤️ ❤️`).
- Simbol hati berkurang satu per satu saat bola menyentuh dasar layar.
- Saat nyawa habis, sistem menampilkan indikator patah hati (`💔 GAME OVER`).

### 4. Fleksibilitas Kontrol Ganda & Tombol Aksi
- **Gerak Kiri**: Tekan tombol panah `<-` atau tombol `A`.
- **Gerak Kanan**: Tekan tombol panah `->` atau tombol `D`.
- **Mulai / Lempar Bola**: Tekan tombol `Spasi` (`Spacebar`).
- **Jeda (Pause / Resume)**: Tekan tombol `P` sewaktu-waktu untuk menghentikan loop pergerakan tanpa mereset game.
- **Mulai Ulang (Quick Restart)**: Tekan tombol `R` kapan saja untuk langsung mengulang game ke Level 1 dengan kondisi bersih.

### 5. Progresi Level 2 (Tantangan Bertahap)
- **Level 1**: 3 baris bata standar (kecepatan bola normal).
- **Level 2**: 4 baris bata lebih rapat dengan variasi bata emerald (membutuhkan 3 pantulan bola untuk hancur) serta peningkatan kecepatan bola sebesar 20%.

---

## 🏛️ Implementasi Konsep OOP (Object-Oriented Programming)

Struktur kode dibangun dengan mematuhi prinsip-prinsip pemrograman berorientasi objek Python:

1. **Inheritance (Pewarisan)**:
   - `GameObject`: Kelas induk (super class) abstrak yang menyediakan atribut umum canvas dan method manipulasi dasar (`get_position()`, `move()`, `delete()`).
   - `Ball(GameObject)`: Mewarisi `GameObject`, menambahkan atribut arah kecepatan (`direction`), deteksi tabrakan dinding/paddle, serta method `collide()`.
   - `Paddle(GameObject)`: Mewarisi `GameObject`, menambahkan method `move()` horizontal dengan batasan lebar layar.
   - `Brick(GameObject)`: Mewarisi `GameObject`, mengelola atribut ketahanan bata (`hits`) dan method `hit()` untuk kalkulasi degradasi warna dan poin skor.
2. **Encapsulation (Pembungkusan)**:
   - Logika status permainan (status nyawa, skor, level, pause, loop waktu `after()`) dienkapsulasi dengan rapi di dalam class `Game(tk.Frame)`.
3. **Polymorphism**:
   - Pemanggilan method polimorfik antar objek game melalui antarmuka `GameObject` dalam proses `find_overlapping()` dan `collide()`.

---

## 🚀 Cara Menjalankan Game

1. Pastikan Python 3 sudah terpasang di sistem operasi Anda.
2. Buka terminal pada folder proyek ini:
   ```bash
   cd ModifyGameBrickBreaker_118
   ```
3. Jalankan skrip utama:
   ```bash
   python main.py
   ```
4. Tekan tombol **Space** untuk mulai bermain!
