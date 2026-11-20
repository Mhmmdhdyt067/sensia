# SenSia — Rancangan Project

**Analisis Sentimen Masyarakat mengenai Turunnya Harga Saham menggunakan Algoritma Bi-LSTM**

Mata kuliah Kecerdasan Buatan · Tugas project deep learning
Tanggal: 20 November 2026 · Status: menunggu persetujuan

## 0. Keputusan yang sudah dikunci

| Hal | Keputusan | Sumber |
|---|---|---|
| Web app | Flask + 1 template HTML | Anda |
| Volume data | 900 komentar (target 300/kelas) | Anda |
| Pipeline | Pendekatan A (ringkas, tanpa Sastrawi/FastText) | Anda |
| Akuisisi | Playwright sebagai jalur utama; akun tersedia, search pernah jalan normal | Anda |
| Jendela data | Tidak terikat peristiwa; kata kunci berorientasi penurunan; rentang tanggal aktual dilaporkan | Saya |
| Tenggat | 7–10 hari | Anda |
| Cakupan pekerjaan | Kode, data, model, web app. Laporan & slide ditulis Anda | Anda |

---

## 1. Intent dan alasan

Tugas ini meminta satu pipeline deep learning end-to-end yang bisa dipertanggungjawabkan di depan kelas: dari mengumpulkan data nyata, memberi label, melatih model, sampai dipakai. Yang dinilai bukan hanya akurasi, tapi kemampuan menjelaskan mengapa setiap langkah ada.

SenSia dibuat untuk memperlihatkan tiga hal: (1) data sentimen saham Indonesia benar-benar bisa dikumpulkan tanpa API berbayar, (2) Bi-LSTM cukup untuk masalah ini dan hasilnya terukur, (3) model bisa dipakai orang lain lewat satu halaman web.

Prinsip yang dipegang: **sederhana, dapat dijalankan ulang, dan setiap angka di laporan bisa ditelusuri ke satu cell notebook.**

## 2. Goals

- Dataset 900 komentar berbahasa Indonesia berlabel (target 300 per kelas) dari X dan Threads.
- Notebook tunggal yang menjalankan seluruh pipeline dari CSV mentah sampai model tersimpan.
- Model Bi-LSTM 3 kelas dengan evaluasi jujur: accuracy, precision/recall/F1 per kelas, confusion matrix.
- Web app Flask berisi landing page dan form prediksi teks.
- Repo GitHub yang bisa di-`clone` orang lain lalu langsung menghasilkan notebook dan web app yang sama.

## 3. Non-goals

- **Bukan prediksi harga saham.** Yang diprediksi hanya sentimen teks. Ini perlu dinyatakan di laporan agar tidak salah kaprah.
- Tidak ada scraping lewat API resmi X/Threads, tidak ada crawling skala besar.
- Tidak ada autentikasi, database, atau user account di web app.
- Tidak ada deployment publik yang wajib. Jalan lokal sudah cukup untuk demo; deploy opsional.
- Tidak memakai model SOTA (IndoBERT, LLM fine-tuning). Algoritma yang diminta adalah Bi-LSTM dan itu yang dipakai.
- Tidak ada dashboard analitik, riwayat prediksi, atau fitur admin.

**Anti-goal:** project yang terlihat mengesankan tapi tidak bisa dijelaskan pemiliknya. Kalau satu komponen tidak bisa dijelaskan dalam dua kalimat, komponen itu dibuang.

## 4. Constraints

| Constraint | Nilai | Konsekuensi desain |
|---|---|---|
| Compute | CPU saja (laptop) | Model kecil: embedding 128, Bi-LSTM 64. 900 sampel selesai dalam hitungan menit. |
| Bahasa | Indonesia, banyak slang bursa | Butuh kamus normalisasi ±40 entri buraskam, bukan stemmer agresif |
| Data | Manual + Playwright, tanpa API | Teks harus diverifikasi; screenshot bukan sumber teks eksak |
| Repo | GitHub, kolaborasi | Notebook rawan conflict → aturan commit & nbstripout |
| Ukuran model | ±5–6 MB | Aman di-commit; Flask langsung jalan setelah clone |
| Algoritma | Bi-LSTM | Arsitektur tidak boleh diganti tanpa alasan metodologis |

## 5. Pendekatan yang dipertimbangkan

**A. Pipeline ringkas** (dipilih) — cleaning + kamus slang → Tokenizer → pad 100 → Embedding trainable 128 → Bi-LSTM 64 → Dense 3. Sepuluh cell, dependency hanya TensorFlow/pandas/sklearn/matplotlib. Realistis 70–85% test accuracy pada 900 data.

**B. + Sastrawi, class weighting, k-fold** — akurasi mungkin +3–5% (tidak dijamin pada data kecil), tapi menambah 6 cell dan satu jebakan: Sastrawi memotong istilah bursa ("gorengan" → "goreng"), sehingga tetap perlu kamus pengecualian. Lebih banyak yang harus dipertanggungjawabkan tanpa hasil proporsional.

**C. + FastText/Indo word2vec pretrained** — akurasi terbaik, tapi unduhan ~1 GB, file model di luar repo, dan paling sulit dijelaskan. Untuk tugas dengan batas waktu presentasi, biaya penjelasannya tidak sepadan.

**Pilihan: A.** Alasan: target nilai ada di kejelasan pipeline dan kualitas data, bukan di angka akurasi tertinggi.

## 6. Struktur repo

```
Sensia/
├── README.md                     # cara menjalankan, hasil model, screenshot
├── .gitignore
├── requirements.txt              # dari pip freeze
├── notebook/
│   └── sensia_bilstm.ipynb       # FILE UTAMA
├── data/
│   ├── screenshots/              # input gambar (tidak di-commit)
│   ├── raw/sensia_raw.csv        # hasil scraping, belum berlabel
│   └── labeled/sensia_labeled.xlsx   # dataset final (di-commit)
├── model/
│   ├── sensia_bilstm.keras
│   ├── tokenizer.json
│   └── label_map.json
├── webapp/
│   ├── app.py
│   ├── templates/index.html
│   └── static/style.css
└── docs/
    ├── labeling-guide.md
    └── superpowers/specs/2026-11-20-sensia-design.md
```

`data/screenshots/` di-gitignore (gambar besar). Bukti dataset yang di-commit adalah CSV/XLSX-nya.

## 7. Alur data

```
screenshot + Playwright
        ↓  transkripsi + verifikasi
data/raw/sensia_raw.csv        (text, platform, kata_kunci, tanggal)
        ↓  pre-label AI + verifikasi manusia
data/labeled/sensia_labeled.xlsx   (+ label)
        ↓  dibaca notebook
cleaning → split → tokenize → train Bi-LSTM
        ↓  save
model/*.keras + tokenizer.json + label_map.json
        ↓  load
webapp/app.py  →  localhost:5000
```

Satu aturan yang mengikat: **`text` di Excel selalu teks mentah apa adanya.** Semua cleaning terjadi di notebook, tidak pernah di spreadsheet. Dengan begitu preprocessing bisa diubah, diuji, dan dijelaskan sebagai bagian dari kode — bukan sebagai perubahan data yang tidak terlihat jejaknya.

## 8. Skema dataset (`data/labeled/sensia_labeled.xlsx`)

Satu baris = satu komentar.

| Kolom | Tipe | Contoh | Aturan |
|---|---|---|---|
| `text` | string | `ihsg anjlok lagi, gorengan pada ARB 😭` | Teks mentah persis dari sumber. Emoji dipertahankan. |
| `platform` | enum | `x` / `threads` | Huruf kecil. |
| `kata_kunci` | string | `ihsg anjlok` | Query yang memunculkan komentar. Satu nilai, bukan daftar. |
| `tanggal` | date | `2026-11-14` | Format `YYYY-MM-DD`. Jika hanya tampil relatif ("2h"), catat tanggal ambil dan tandai di kolom catatan internal. |
| `label` | enum | `negatif` / `netral` / `positif` | Huruf kecil, tanpa spasi. |

Aturan tambahan:

- **Deduplikasi sebelum split**, berdasarkan teks yang sudah di-lowercase dan dibuang non-alfanya. Repost/quote dengan teks identik dihitung satu.
- Tidak menyimpan username, handle, atau foto profil. Hanya teks. Ini bagian dari etika data dan disebut di laporan.
- Komentar yang bukan bahasa Indonesia, iklan/judi online, atau <5 kata dibuang saat screening.

## 9. Aturan pelabelan (`docs/labeling-guide.md`)

Tiga kelas, diuji dengan pertanyaan tunggal: **"pembaca ini sedang menyatakan harapan naik, kekhawatiran turun, atau tidak menyatakan apa-apa?"**

**Positif** — optimisme, ajakan beli/akumulasi, pujian terhadap emiten/kebijakan/bandar, ekspektasi rebound.
`"BBCA udah murah banget ini, waktunya akumulasi"`

**Negatif** — keluhan, panik, ajakan jual/cut loss, kritik, pesimisme, sindiran terhadap "gorengan"/bandar.
`"kapok main saham gorengan, duit habis buat ARB"`

**Netral** — informasi tanpa opini, pertanyaan murni, laporan harga, candaan tanpa arah.
`"IHSG hari ini ditutup di 6.812, turun 1,2%"`

Kasus ambigu dan penyelesaiannya:

| Kasus | Aturan |
|---|---|
| Sarkasme (`"mantap nih ARB terus"`) | Ikuti makna yang dimaksud, bukan kata literal → negatif |
| Pertanyaan berharap (`"bisa naik nggak ya?"`) | Netral, kecuali ada klaim atau ajakan |
| Kutipan berita tanpa komentar penulis | Netral |
| Campuran positif & negatif | Ambil yang dominan; jika benar-benar seimbang → netral |
| Emoji kuat (`🚀` vs `💀`) | Dipakai sebagai sinyal saat memberi label, tapi tetap dibersihkan di preprocessing |
| Hanya tagar/mention | Dibuang (tidak lolos screening) |

Jaminan kualitas yang bisa ditulis di laporan: 10% sampel acak dicek ulang setelah jeda ≥24 jam, target konsistensi ≥90%. Label awal boleh dibantu AI, tetapi **semua baris diverifikasi manusia** — ini yang membuat dataset bisa dipertanggungjawabkan.

## 10. Isi notebook (12 cell)

| # | Jenis | Isi | Output yang terlihat |
|---|---|---|---|
| 1 | markdown | Judul, identitas, ringkasan pipeline | — |
| 2 | code | Import, `set_seed(42)`, cek versi TF | versi library |
| 3 | code | Load XLSX, `head()`, `value_counts()` label | 900 baris, 3 kelas |
| 4 | code | EDA ringkas: distribusi label, platform, panjang teks | 3 grafik |
| 5 | code | `clean_text()`: lowercase, hapus URL/mention/hashtag/angka berlebih, rapikan spasi | contoh 5 sebelum–sesudah |
| 6 | code | `SLANG` dict ±40 entri + apply | contoh normalisasi |
| 7 | code | Split stratified 80/10/10 (`random_state=42`) | jumlah tiap split |
| 8 | code | `Tokenizer(num_words=10000, oov_token="<OOV>")`, `fit_on_texts` **hanya pada train**, `pad_sequences(maxlen=100)` | contoh teks → urutan angka |
| 9 | code | Build + compile model, `model.summary()` | tabel parameter |
| 10 | code | `model.fit()` dengan `EarlyStopping(patience=3, restore_best_weights=True)` | kurva accuracy & loss |
| 11 | code | `classification_report`, confusion matrix, 10 contoh salah prediksi | metrik per kelas |
| 12 | code | Simpan model, tokenizer, label map + `predict(text)` demo | file di `model/` |

Arsitektur (cell 9):

```python
model = Sequential([
    Embedding(VOCAB_SIZE, 128, input_length=MAX_LEN),
    Bidirectional(LSTM(64, dropout=0.2, recurrent_dropout=0.0)),
    Dropout(0.3),
    Dense(64, activation="relu"),
    Dense(3, activation="softmax"),
])
model.compile(loss="sparse_categorical_crossentropy",
              optimizer="adam", metrics=["accuracy"])
```

`EarlyStopping` adalah satu baris tambahan di luar pendekatan A murni. Alasan dimasukkan: pada dataset kecil model mudah overfit, dan tanpa itu kurva validasi biasanya berbalik naik setelah epoch 5–7 — angka yang buruk di laporan. Ini keputusan saya, bukan permintaan Anda.

Label map dipatok manual, **bukan** mengandalkan urutan alfabet yang kebetulan:

```json
{"0": "negatif", "1": "netral", "2": "positif"}
```

Urutan ini harus sama antara notebook dan `app.py`. Salah urutan = prediksi terbalik tanpa error, jadi ini ditulis eksplisit di dua tempat dan dicek dengan satu test prediksi kalimat yang jelas.

## 11. Baseline dan ambang kelulusan

| Model | Test accuracy (perkiraan) |
|---|---|
| Majority class | ±33% |
| Aturan kata kunci sederhana | 45–55% |
| Bi-LSTM (target) | **≥75%, macro F1 ≥0.70** |

Jika hasil di bawah target, urutan pemeriksaan yang disepakati:

1. **Konsistensi label** — biasanya ini penyebabnya pada dataset buatan sendiri.
2. Distribusi kelas — jika tidak ±300/300/300, pakai `class_weight="balanced"` (3 baris).
3. Jumlah data per kelas di training set.
4. Baru setelah itu menyentuh arsitektur/hyperparameter.

Bukan sebaliknya. Menaikkan kapasitas model di atas data berlabel berisik hanya menghasilkan overfit yang lebih rapi.

## 12. Web app (Flask)

Satu halaman, empat bagian:

1. **Hero** — nama SenSia, judul project, satu paragraf penjelasan, tombol "Coba sekarang" yang scroll ke form.
2. **Tentang** — tiga kartu: Dataset (900 komentar X & Threads), Model (Bi-LSTM 3 kelas), Performa (accuracy & macro F1 dari hasil latihan — diisi angka nyata, bukan karangan).
3. **Coba** — textarea + tombol "Analisis Sentimen" → badge positif/negatif/netral + confidence bar + skor ketiga kelas.
4. **Footer** — mata kuliah, tahun, tautan GitHub.

Teknis:

- `GET /` → `render_template`.
- `POST /predict` → JSON `{label, confidence, scores}`, dipanggil `fetch()` dari JS. Tanpa reload halaman.
- Model dan tokenizer dimuat **sekali** saat startup (module level), bukan per request.
- Validasi input di server (trust boundary): tolak kosong, <3 karakter, >500 karakter. Pesan error ditampilkan di form.
- Tidak ada database. Tidak ada riwayat. Tidak ada file upload.
- Jika file model tidak ada saat startup, app berhenti dengan pesan: "Jalankan notebook dulu untuk menghasilkan model/".
- Desain visual (warna, tipografi, layout) diserahkan ke designer; isi teknis dan copy diperiksa setelahnya.

Batas yang diakui: prediksi hanya sebaik data latihnya. Kalimat di luar gaya bahasa saham Twitter kemungkinan salah, dan UI tidak perlu menyembunyikan itu.

## 13. Rencana akuisisi data

**Kata kunci** (12): `ihsg anjlok`, `saham turun`, `ihsg hari ini`, `saham gorengan`, `ARB saham`, `cut loss`, `bandar saham`, `cuan saham`, `saham naik`, `BBCA`, `GOTO`, `harga saham`.

**Screening** (dibuang): bukan bahasa Indonesia, iklan/promo/judi online, <5 kata, hanya emoji/tagar, duplikat.

**Jendela waktu.** Tidak mengejar peristiwa pasar tertentu. Kata kunci dipilih yang berorientasi penurunan supaya isi data tetap relevan dengan judul, dan `tanggal` tiap baris dicatat. Rentang tanggal yang benar-benar tercakup dilaporkan sebagai fakta ("data dikumpulkan pada X, mencakup Y–Z"), bukan diklaim sebagai periode krisis tertentu. Konsekuensi yang harus diterima: kalau rentangnya pendek, laporan tidak boleh menyimpulkan tren antar waktu.

**Playwright (jalur akurat)** — buka X search `/search?q=<kata kunci>&f=live`, buka Threads search, scroll N kali, ambil teks dari DOM (`article[data-testid="tweet"]` untuk X). Teks yang didapat adalah teks asli, tanpa kesalahan OCR. Hasil langsung ke `data/raw/sensia_raw.csv`.

**Screenshot (jalur cadangan)** — untuk postingan yang tidak lagi bisa diakses atau saat sesi Playwright diblokir. Nama file: `<platform>_<kata_kunci>_<nomor>.png`. Ditranskripsi lalu **diverifikasi satu per satu**; baris yang tidak bisa dipastikan dibuang, bukan ditebak.

Catatan jujur: transkripsi gambar tidak bisa dijamin 100% identik dengan aslinya. Karena itu Playwright adalah jalur utama untuk volume, screenshot adalah bukti dan cadangan. Ini perlu disebut di laporan sebagai keterbatasan metodologi, bukan disembunyikan.

Etika: hanya teks publik, tanpa identitas, tanpa foto, tidak menembus login orang lain, laju permintaan wajar.

## 14. Kolaborasi GitHub

- `git init` → `main` selalu dalam keadaan bisa dijalankan.
- Fitur di branch `feat/<topik>`, merge lewat PR, minimal 1 review, squash merge.
- Commit kecil dan sering; jangan menumpuk 900 baris perubahan notebook dalam satu commit.
- Aturan praktis notebook: **satu orang mengedit notebook pada satu waktu.** JSON notebook tidak bisa di-merge otomatis dengan baik.
- Opsional satu perintah: `nbstripout` agar output cell tidak masuk commit (mengurangi conflict dan ukuran diff). Jika dipakai, output harus tetap ada di laporan/screenshot.
- `.gitignore`: `data/screenshots/`, `.ipynb_checkpoints/`, `__pycache__/`, `*.venv/`, `.env`.
- Model di-commit (±5–6 MB) supaya `git clone` → `python webapp/app.py` langsung jalan. Jika suatu saat >50 MB, pindah ke GitHub Release.

## 15. Environment

- Python 3.11 atau 3.12, virtualenv lokal. Project ini Python murni, tidak butuh lerd/container.
- `requirements.txt` dihasilkan dari `pip freeze` di akhir supaya versi yang benar-benar dipakai yang tercatat.
- Inti: `tensorflow`, `pandas`, `scikit-learn`, `matplotlib`, `openpyxl` (baca/tulis XLSX), `flask`.
- VSCode: pilih interpreter venv, pasang ekstensi Jupyter, pilih kernel venv yang sama. Ini sumber error paling umum ("module not found") dan masuk README.
- `README.md` memuat: cara setup, cara generate model, cara jalankan web app, hasil metrik terakhir, dan screenshot halaman.

## 16. Milestone

| # | Hasil | Perkiraan |
|---|---|---|
| M1 | Repo + struktur + notebook kerangka + kamus slang | 1–2 hari |
| M2 | 900 komentar terkumpul & berlabel di XLSX | 3–5 hari |
| M3 | Preprocessing + training + evaluasi mencapai ambang | 1 hari |
| M4 | Model tersimpan + web app jalan lokal | 1 hari |
| M5 | README, laporan, latihan demo | 0,5 hari |

Total 7–10 hari kerja, dan **tenggatnya memang 7–10 hari**. Konsekuensinya: M1 dan M2 berjalan paralel mulai hari pertama (kerangka notebook, fungsi cleaning, dan kamus slang tidak butuh data), dan M3 tidak boleh menunggu M2 mencapai 900 — latih dengan data yang sudah ada di hari ke-5, sisanya masuk di hari ke-6.

| Hari | Yang dikerjakan |
|---|---|
| 1–2 | Repo, kerangka notebook, kamus slang **sambil** mengumpulkan data lewat Playwright |
| 3–5 | Pelabelan (jalur kritis) |
| 6 | Training + evaluasi; putaran perbaikan label jika perlu |
| 7 | Web app + model tersimpan |
| 8–9 | Buffer: perbaikan label, polishing, README |
| 10 | Anda menulis laporan dari artefak yang sudah ada |

## 17. Risiko

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Data tidak sampai 900 / tidak seimbang | Training timpang | Class weights; atau turunkan target ke 300 dan sesuaikan narasi laporan |
| Akurasi < 75% | Sulit dipertanggungjawabkan | Periksa label dulu (bagian 11), bukan arsitektur |
| Teks train/test tumpang tindih (repost) | Akurasi palsu tinggi | Dedupe sebelum split, split berdasarkan hash teks |
| X/Threads memblokir otomatis | Data macet | Screenshot manual jadi cadangan; laju wajar; jangan pakai akun utama |
| Notebook conflict di git | Pekerjaan hilang | Satu editor pada satu waktu, commit kecil, `nbstripout` opsional |
| Model terlalu besar untuk git | Clone gagal | Release asset |
| Demo web app gagal saat presentasi | Nilai turun | Model di-commit, jalankan lokal, siapkan screenshot cadangan |
| Label tidak konsisten | Akurasi rendah & tidak bisa dibela | Guideline + verifikasi ulang 10% setelah 24 jam |
| Tenggat 7–10 hari | Tidak ada ruang untuk rework besar | Data & label dikunci sebelum hari 6; tidak ada fitur baru setelah hari 7 |

## 18. Yang diserahkan ke builder

- Nama branch dan jadwal kerja konkret.
- Penamaan file screenshot dan siapa yang mengisi kolom mana (jika berkelompok).
- Visual web app: warna, tipografi, layout detail.
- Opsional: deploy ke Render/Fly.io, atau tetap lokal.
- Opsional: menambah `class_weight` bila distribusi akhir tidak seimbang.
- **Laporan dan slide ditulis oleh pemilik project.** Yang disediakan untuk itu: angka metrik nyata, confusion matrix, grafik training, dan tabel pemetaan artefak→bab di bagian 19.

## 19. Rencana laporan (agar artefak dan tulisan sejalan)

| Bab laporan | Diambil dari |
|---|---|
| Latar belakang & tujuan | Bagian 1–3 dokumen ini |
| Metodologi akuisisi & pelabelan | Bagian 8–9, 13 |
| Preprocessing | Cell 5–6 notebook, kamus slang |
| Arsitektur & training | Cell 9–10, tabel parameter |
| Hasil & evaluasi | Cell 11, confusion matrix, perbandingan baseline |
| Implementasi web app | Bagian 12 |
| Keterbatasan | Bagian 13 (fidelitas teks), bagian 11 (data kecil), 3 (bukan prediksi harga) |
| Kesimpulan | Pencapaian ambang + apa yang akan diperbaiki |
