# Rekomendasi Pakaian Personal Berdasarkan Riwayat Kecocokan dan Preferensi Musiman
**alias: pandorarian**
## Project Overview
Sistem rekomendasi ini dikembangkan untuk memberikan saran pakaian kepada pengguna berdasarkan histori kecocokan pakaian sebelumnya (`fit`) dan mempertimbangkan musim saat rekomendasi diberikan. Dengan memanfaatkan Content-Based Filtering yang menggabungkan TF-IDF untuk fitur kategorikal dan normalisasi untuk fitur numerikal, sistem ini bertujuan untuk memberikan rekomendasi yang relevan dan kontekstual.

## Literature Review

### Content-Based Filtering
Content-Based Filtering (CBF) adalah metode sistem rekomendasi yang memanfaatkan informasi dan karakteristik dari item yang telah disukai pengguna untuk merekomendasikan item baru yang serupa. Pendekatan ini membangun **profil pengguna berdasarkan fitur item yang telah diberi rating tinggi atau dinyatakan cocok**. CBF sangat berguna dalam skenario di mana **interaksi antar pengguna terbatas atau tidak tersedia**, seperti pada pengguna baru atau platform dengan data rating yang tidak saling terkoneksi antar user.

**Referensi:**
- Lops, P., De Gemmis, M., & Semeraro, G. (2011). *Content-based Recommender Systems: State of the Art and Trends*. In *Recommender Systems Handbook* (pp. 73–105). Springer.

### TF-IDF untuk Representasi Fitur Kategorikal
TF-IDF (Term Frequency-Inverse Document Frequency) adalah teknik pembobotan dalam text mining yang digunakan untuk menilai seberapa penting suatu kata dalam dokumen relatif terhadap kumpulan dokumen. Dalam konteks sistem rekomendasi, TF-IDF dapat digunakan untuk mengubah **fitur kategorikal seperti jenis pakaian, musim, dan tipe tubuh menjadi vektor numerik yang bisa dibandingkan antar item**.

**Referensi:**
- Ramos, J. (2003). *Using TF-IDF to Determine Word Relevance in Document Queries*. In *Proceedings of the First Instructional Conference on Machine Learning*.

### Cosine Similarity untuk Pengukuran Kecocokan
Cosine similarity adalah metrik jarak yang digunakan untuk mengukur kesamaan antara dua vektor dengan menghitung cosinus dari sudut di antara mereka. Ini sangat cocok untuk TF-IDF karena skala absolut tidak penting — hanya arah vektor yang relevan. Dalam sistem ini, cosine similarity digunakan untuk menghitung **kesamaan antara vektor profil pengguna dan vektor tiap item**.

**Referensi:**
- Huang, A. (2008). *Similarity Measures for Text Document Clustering*. In *Proceedings of the Sixth New Zealand Computer Science Research Student Conference* (NZCSRSC), Christchurch.

### Normalisasi Data dengan StandardScaler

Dalam sistem rekomendasi berbasis konten, fitur numerikal seperti berat badan, tinggi badan, usia, ukuran pakaian, dan ukuran band dapat memiliki skala nilai yang berbeda-beda. Jika digunakan tanpa normalisasi, fitur dengan skala lebih besar dapat mendominasi perhitungan similarity dan menyebabkan bias.

Oleh karena itu, fitur numerik dinormalisasi menggunakan **StandardScaler** dari scikit-learn, yang melakukan transformasi data ke distribusi standar dengan:
- **Mean = 0**
- **Standard deviation = 1**

Dengan melakukan normalisasi ini, setiap fitur numerik memberikan kontribusi yang seimbang dalam perhitungan jarak antar vektor (cosine similarity), sehingga hasil rekomendasi menjadi lebih akurat dan adil.

**Referensi:**
- Han, J., Pei, J., & Kamber, M. (2011). *Data Mining: Concepts and Techniques* (3rd ed.). Morgan Kaufmann.
- Pedregosa, F. et al. (2011). *Scikit-learn: Machine Learning in Python*, Journal of Machine Learning Research, 12, pp. 2825–2830.

## Business Understanding

### Problem Statement
Pengguna sering kesulitan menemukan pakaian yang pas dan sesuai dengan kondisi atau musim tertentu, terutama saat menyewa pakaian secara online. Masalah utama adalah memastikan rekomendasi sesuai preferensi dan karakteristik fisik pengguna, serta relevan dengan waktu pemakaian.

### Goals
1. Memberikan rekomendasi pakaian berdasarkan histori kecocokan pakaian sebelumnya (yang diberi label "fit").
2. Memberikan rekomendasi pakaian yang tidak hanya cocok secara fisik tetapi juga relevan dengan musim saat digunakan.

### Solution Statements
- Sistem menggunakan teknik Content-Based Filtering.
- Fitur kategorikal seperti kategori pakaian, acara, musim, body type, dan ukuran cup diubah menjadi representasi TF-IDF.
- Fitur numerikal seperti tinggi, berat, usia, dan ukuran band dinormalisasi dengan StandardScaler.
- Vektor fitur digabung, lalu similarity dihitung menggunakan cosine similarity terhadap profil pengguna.

## Data Understanding

Dataset yang digunakan berasal dari [Rent the Runway](https://www.kaggle.com/datasets/rmisra/clothing-fit-dataset-for-size-recommendation), yang berisi data ulasan pelanggan terhadap produk pakaian yang mereka sewa. Dataset ini mencakup:

- **Jumlah pengguna:** 105.508
- **Jumlah produk:** 5.850
- **Jumlah transaksi:** 192.544
- **Jumlah missing values: 64759**
- **Jumlah baris data duplikat: 229**

### 📁 Deskripsi Fitur

| Fitur            | Deskripsi                                                                 |
|------------------|---------------------------------------------------------------------------|
| `item_id`        | ID unik untuk setiap produk                                               |
| `user_id`        | ID unik untuk setiap pengguna                                             |
| `review_date`    | Tanggal saat ulasan ditulis                                               |
| `review_text`    | Ulasan lengkap yang diberikan oleh pengguna (tidak digunakan dalam model) |
| `review_summary` | Ringkasan dari ulasan pengguna (tidak digunakan dalam model)              |
| `category`       | Kategori produk (misalnya dress, pants, coat)                             |
| `rented for`     | Tujuan penyewaan pakaian (misalnya wedding, party, vacation)              |
| `fit`            | Umpan balik tentang kecocokan pakaian terhadap pengguna (`fit`, `small`, `large`) |
| `size`           | Ukuran standar pakaian yang digunakan                                     |
| `rating`         | Rating dari produk berdasarkan pengalaman pengguna                         |
| `bust size`      | Ukuran lingkar dada pengguna (misalnya `34B`, `36C`)                      |
| `weight`         | Berat badan pengguna dalam satuan pound                                   |
| `height`         | Tinggi badan pengguna dalam satuan feet dan inchi                         |
| `age`            | Usia pengguna                                                             |
| `body type`      | Tipe tubuh pengguna (misalnya athletic, pear, hourglass)                  |

Beberapa fitur seperti `review_text` dan `review_summary` tidak digunakan dalam pemodelan karena tidak relevan untuk pendekatan berbasis konten. Fokus diberikan pada fitur-fitur kategorikal dan numerikal yang menggambarkan karakteristik pengguna dan produk, yang digunakan untuk membangun sistem rekomendasi personal dan kontekstual.
### Detail missing values
| Kolom       | Jumlah Missing Value |
|-------------|----------------------|
| fit         | 0                    |
| user_id     | 0                    |
| bust size   | 18411                |
| item_id     | 0                    |
| weight      | 29982                |
| rating      | 82                   |
| rented for  | 10                   |
| body type   | 14637                |
| category    | 0                    |
| height      | 677                  |
| size        | 0                    |
| age         | 960                  |
| review_date | 0                    |

## Data Preparation
- Kolom tidak relevan (`review_text`, `review_summary`) dibuang.
- Data missing ditangani:
  - Modus untuk `body type`, `bust size`
  - Median untuk `weight`, `age` (skewed distribution)
  - Mean untuk `height` (normal distribution)
- `bust size` dipisah menjadi `band_size` (numerik) dan `cup_size_raw` (kategorikal).
- Kolom `review_date` dikonversi menjadi `season`.
- Label diselaraskan (penyatuan sinonim, perbaikan typo).
- Duplikat dihapus.
- TF-IDF digunakan untuk representasi fitur kategorikal: `category`, `rented for`, `season`, `body type`, dan `cup_size_raw`.
- Normalisasi (StandardScaler) diterapkan pada fitur numerikal: `weight`, `height`, `size`, `age`, `band_size`.
- Kedua jenis fitur digabung dengan `scipy.sparse.hstack`.

## Modelling & Results
### Modelling
- Profil pengguna dibuat dari rata-rata vektor item yang pernah cocok (`fit`).
- Rekomendasi dihitung dengan cosine similarity terhadap semua item, difilter agar tidak menyarankan item yang sudah dilihat user.
### Results
- Rekomendasi diuji untuk beberapa pengguna sebagai contoh.
- Sistem dapat mengembalikan 5 rekomendasi terbaik berdasarkan kecocokan vektor fitur.
- Implementasi tambahan memungkinkan pemfilteran rekomendasi berdasarkan musim.
- Contoh hasil:
  - Untuk `user_id = 151944`, direkomendasikan `item_id = [1531631, 162634, 1487216, 432275, 131533]`
  - Musim: hasil direkomendasikan untuk setiap musim (Winter, Spring, Summer, Fall)

## Evaluation

---

> 📌 Catatan: Sistem ini bersifat **Content-Based**, sehingga tidak bergantung pada rating pengguna lain. Sangat cocok untuk cold-start item (item baru), tapi terbatas jika user baru belum pernah menyewa pakaian (cold-start user).
