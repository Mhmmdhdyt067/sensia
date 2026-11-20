# Panduan Pelabelan Sentimen — SenSia

Dokumen ini mengikat. Semua baris dataset harus dilabeli dengan aturan yang sama, karena label yang tidak konsisten adalah penyebab paling umum akurasi rendah pada proyek seperti ini.

## Pertanyaan tunggal

Untuk setiap komentar, tanyakan satu hal:

> **"Pembaca ini sedang menyatakan harapan harga naik, kekhawatiran harga turun, atau tidak menyatakan apa-apa?"**

Jangan menilai emosinya terhadap saham tertentu; nilai arah sentimennya terhadap harga.

## Tiga kelas

### `negatif`
Keluhan, kekhawatiran, panik, ajakan jual/cut loss, kritik terhadap emiten/kebijakan/bandar, pesimisme, sindiran terhadap praktik pasar.

- "ihsg anjlok lagi, portofolio makin merah aja"
- "kapok main saham gorengan, duit habis buat ARB"
- "bandar lagi pada cabut nih, hati-hati yang nyangkut"
- "mantap nih ARB terus, terima kasih pak" ← sarkasme, maknanya negatif

### `positif`
Optimisme, ajakan beli/akumulasi, pujian, ekspektasi rebound, kabar baik tentang emiten.

- "BBCA udah murah banget ini, waktunya akumulasi"
- "finally hijau semua, cuan hari ini"
- "rebound dulu ah, panik jual malah nyesel"
- "fundamental bank masih bagus, saya tambah terus"

### `netral`
Informasi tanpa opini, pertanyaan murni, laporan angka, candaan yang tidak mengarah ke mana-mana.

- "IHSG hari ini ditutup di 6.812, turun 1,2%"
- "ada yang tahu jadwal rilis laporan keuangan BBRI kapan?"
- "GOTO ARB lagi, ada yang bisa jelasin kenapa?" ← pertanyaan murni, bukan keluhan
- "saham itu kayak kopi, pahit dulu baru nikmat" ← perumpamaan tanpa arah

## Kasus ambigu

| Kasus | Aturan | Contoh |
|---|---|---|
| Sarkasme | Ikuti makna yang dimaksud, bukan kata literal | "mantap nih ARB terus" → `negatif` |
| Pertanyaan berharap | `netral`, kecuali ada klaim atau ajakan | "bisa naik nggak ya?" → `netral` |
| Kutipan berita tanpa komentar penulis | `netral` | "IHSG turun 1,2% menurut CNBC" → `netral` |
| Campuran positif dan negatif | Ambil yang dominan; jika benar-benar seimbang → `netral` | "awalnya boncos, tapi sekarang cuan" → `positif` |
| Emoji kuat (🚀 vs 💀) | Jadi sinyal saat memberi label, walau nanti dibersihkan di preprocessing | "gak kuat liat ini 💀" → `negatif` |
| Hanya tagar/mention | Tidak masuk dataset (dibuang saat screening) | "#IHSG #saham" → dibuang |
| Tidak bisa dipastikan | `netral` — jangan menebak | singkatan yang tidak dikenal → `netral` |

## Prosedur

1. **Label awal boleh dibantu AI/aturan kata kunci**, tetapi **setiap baris diverifikasi manusia**. Tidak ada baris yang masuk dataset tanpa dibaca.
2. **Teks tidak boleh diedit.** Perbaiki labelnya saja. Teks mentah adalah data; cleaning dikerjakan kode di notebook.
3. Kerjakan per blok 100 baris, bukan sekaligus 900. Kelelahan membuat label asal-asalan di blok terakhir.
4. Setelah selesai, tunggu **≥24 jam**, lalu periksa ulang **10% baris acak** (`df.sample(90, random_state=42)`) tanpa melihat label sebelumnya.
5. Jika konsistensi di bawah **90%**, jangan lanjut melatih model: perbaiki panduan ini dulu, lalu label ulang bagian yang bermasalah.
6. Setelah selesai, catat di laporan: siapa yang melabeli, berapa baris, dan hasil pengecekan ulang. Ini bukti metodologi, bukan formalitas.

## Distribusi target

| Kelas | Target | Toleransi |
|---|---|---|
| `negatif` | 300 | 280–320 |
| `netral` | 300 | 280–320 |
| `positif` | 300 | 280–320 |

Jika setelah 1200 baris mentah salah satu kelas tetap jauh di bawah 280, tambah kata kunci yang mengarah ke kelas itu, jangan memaksakan label.
