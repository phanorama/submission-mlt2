# Rekomendasi Pakaian Personal Berdasarkan Riwayat Kecocokan dan Preferensi Musiman
**alias: pandorarian**
## Project Overview

### Latar Belakang

Sistem rekomendasi ini dikembangkan untuk memberikan saran pakaian kepada pengguna berdasarkan histori kecocokan pakaian sebelumnya (`fit`) dan mempertimbangkan musim saat rekomendasi diberikan. Dengan memanfaatkan Content-Based Filtering yang menggabungkan TF-IDF untuk fitur kategorikal dan normalisasi untuk fitur numerikal, sistem ini bertujuan untuk memberikan rekomendasi yang relevan dan kontekstual.

### Literature Review

#### Content-Based Filtering
Content-Based Filtering (CBF) adalah metode sistem rekomendasi yang memanfaatkan informasi dan karakteristik dari item yang telah disukai pengguna untuk merekomendasikan item baru yang serupa. Pendekatan ini membangun **profil pengguna berdasarkan fitur item yang telah diberi rating tinggi atau dinyatakan cocok**. CBF sangat berguna dalam skenario di mana **interaksi antar pengguna terbatas atau tidak tersedia**, seperti pada pengguna baru atau platform dengan data rating yang tidak saling terkoneksi antar user [1].
#### TF-IDF untuk Representasi Fitur Kategorikal
TF-IDF (Term Frequency-Inverse Document Frequency) adalah teknik pembobotan dalam text mining yang digunakan untuk menilai seberapa penting suatu kata dalam dokumen relatif terhadap kumpulan dokumen. Dalam konteks sistem rekomendasi, TF-IDF dapat digunakan untuk mengubah **fitur kategorikal seperti jenis pakaian, musim, dan tipe tubuh menjadi vektor numerik yang bisa dibandingkan antar item** [2].
#### Cosine Similarity untuk Pengukuran Kecocokan
Cosine similarity adalah metrik jarak yang digunakan untuk mengukur kesamaan antara dua vektor dengan menghitung cosinus dari sudut di antara mereka. Ini sangat cocok untuk TF-IDF karena skala absolut tidak penting — hanya arah vektor yang relevan. Dalam sistem ini, cosine similarity digunakan untuk menghitung **kesamaan antara vektor profil pengguna dan vektor tiap item** [3].
#### Normalisasi Data dengan StandardScaler
Dalam sistem rekomendasi berbasis konten, fitur numerikal seperti berat badan, tinggi badan, usia, ukuran pakaian, dan ukuran band dapat memiliki skala nilai yang berbeda-beda. Jika digunakan tanpa normalisasi, fitur dengan skala lebih besar dapat mendominasi perhitungan similarity dan menyebabkan bias. Oleh karena itu, fitur numerik dinormalisasi menggunakan **StandardScaler** dari scikit-learn, yang melakukan transformasi data ke distribusi standar dengan:
- **Mean = 0**
- **Standard deviation = 1**
  
Dengan melakukan normalisasi ini, setiap fitur numerik memberikan kontribusi yang seimbang dalam perhitungan jarak antar vektor (cosine similarity), sehingga hasil rekomendasi menjadi lebih akurat dan adil [4], [5].

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

- **Jumlah baris atau transaksi:** 192.544
- **Jumlah kolom: 15**
- **Jumlah baris data asli duplikat: 189**
- **Jumlah missing values: 64759**

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
| `rating`         | Rating dari produk berdasarkan pengalaman pengguna `(10,  8,  4,  6,  2)` |
| `bust size`      | Ukuran lingkar dada pengguna (misalnya `34B`, `36C`)                      |
| `weight`         | Berat badan pengguna dalam satuan pound                                   |
| `height`         | Tinggi badan pengguna dalam satuan feet dan inchi                         |
| `age`            | Usia pengguna                                                             |
| `body type`      | Tipe tubuh pengguna (misalnya athletic, pear, hourglass)                  |


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
| reviwe text |  0                   |
| body type   | 14637                |
| review summary | 0                 |
| category    | 0                    |
| height      | 677                  |
| size        | 0                    |
| age         | 960                  |
| review_date | 0                    |

## Data Preparation
1. **Penghapusan kolom tidak relevan**: Kolom `review_summary` dan `review_text` dibuang karena tidak dibutuhkan untuk tujuan sistem rekomendasi.
2. **Penanganan missing values untuk kolom `rating` dan `rented for`**: Baris dengan nilai kosong pada kolom `rating` dan `rented for` dihapus menggunakan `dropna()` karena memiliki sedikit missing value.
3. **Imputasi missing values kolom kategorikal**: Kolom `bust size` dan `body type` diisi dengan modus (nilai yang paling sering muncul) karena berjenis data kategorikal.
4. **Konversi dan imputasi kolom `weight`**: 
   - Satuan diubah dari pounds (lbs) menjadi kilogram (kg) dengan mengalikan 0.453592
   - Missing values diisi dengan median karena distribusi data skewed (skewness = 1.396 > 1)
5. **Konversi dan imputasi kolom `height`**: 
   - Format diubah dari feet'inches" menjadi satuan inci terlebih dahulu
   - Missing values diisi dengan mean karena distribusi mendekati normal (skewness ≈ 0)
   - Kemudian dikonversi ke satuan sentimeter (cm) dengan mengalikan 2.54
6. **Imputasi kolom `age`**: Missing values diisi dengan median karena distribusi data skewed (skewness > 1).
7. **Pembulatan nilai `weight`**: Nilai berat dibatasi hingga dua digit di belakang koma untuk konsistensi.
8. **Pemisahan kolom `bust size`**: 
   - Kolom `bust size` dipecah menjadi dua kolom baru:
     - `band_size`: menyimpan angka (numerik) yang merepresentasikan lingkar dada
     - `cup_size_raw`: menyimpan huruf (kategorikal) yang merepresentasikan ukuran cup
9. **Konversi `review_date` menjadi `season`**: 
   - Tanggal ulasan dikonversi menjadi musim (Winter, Spring, Summer, Fall)
   - Hal ini dilakukan untuk mengetahui kapan pengguna menyewa dan memberikan rating
10. **Penghapusan kolom yang sudah direpresentasikan**: Kolom `bust size` dan `review_date` dihapus karena sudah direpresentasikan dalam bentuk fitur baru.
11. **Perbaikan label pada `cup_size_raw`**: Label `ddde` (hasil dari pemisahan `ddd/e`) diganti dengan `e` untuk konsistensi.
12. **Konsolidasi label `rented for`**: Label `party: cocktail` digabungkan menjadi `party` untuk perumuman kategori.
13. **Konsolidasi label `category`**: 
    - Bentuk jamak dan tunggal dikonsolidasi (contoh: `pant` → `pants`, `legging` → `leggings`)
    - Perbaikan typo dan sinonim (contoh: `sweatshirt` → `sweatershirt`, `tee` → `t-shirt`)
    - Perbaikan anomali kategori berdasarkan analisis review text (contoh: `for` → `turtleneck`, `print` → `dress`)
14. **Penghapusan data duplikat**: Data yang terduplikat dihapus untuk memastikan kualitas dataset.
15. **Penggabungan fitur kategorikal**: Fitur kategorikal (`category`, `rented for`, `season`, `body type`, `cup_size_raw`) digabungkan menjadi satu kolom `text_features`.
16. **Vektorisasi fitur kategorikal**: Fitur kategorikal yang telah digabung diubah menjadi representasi TF-IDF menggunakan `TfidfVectorizer`.
17. **Normalisasi fitur numerikal**: Fitur numerikal (`weight`, `height`, `size`, `age`, `band_size`) dinormalisasi menggunakan `StandardScaler` untuk menghindari bias akibat perbedaan skala.
18. **Penggabungan vektor fitur**: Fitur kategorikal (TF-IDF) dan fitur numerikal (normalized) digabungkan menggunakan `scipy.sparse.hstack` untuk membentuk vektor fitur akhir yang akan digunakan dalam sistem rekomendasi.

## Modeling
- Profil pengguna dibuat dari rata-rata vektor item yang pernah cocok (`fit`).
- Rekomendasi dihitung dengan cosine similarity terhadap semua item, difilter agar tidak menyarankan item yang sudah dilihat user.
- Rekomendasi diuji untuk beberapa pengguna sebagai contoh.
- Sistem dapat mengembalikan 5 rekomendasi terbaik berdasarkan kecocokan vektor fitur.
- Implementasi tambahan memungkinkan pemfilteran rekomendasi berdasarkan musim.
- Hasilnya, sebagai contoh untuk `user_id = 151944`, direkomendasikan `item_id = [1531631, 162634, 1487216, 432275, 131533]` oleh model

**Rekomendasi Teratas untuk `user_id = 151944`:**  
| item_id | similarity | category |
|---------|------------|----------|
| 1531631 | 0.8562     | gown     |
| 162634  | 0.8526     | gown     |
| 1487216 | 0.8511     | gown     |
| 432275  | 0.8482     | gown     |
| 131533  | 0.8458     | gown     |

- Dan hasil direkomendasikan untuk setiap musim (Winter, Spring, Summer, Fall)

## Evaluation
* **Metrik**: RMSE, dan MAE

### Rumus RMSE:

$$RMSE = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$

### Rumus MAE:

$$MAE = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$


### Hasil evaluasi
Evaluasi dilakukan terhadap sistem rekomendasi berbasis *content-based filtering* yang bertujuan merekomendasikan pakaian kepada pengguna berdasarkan histori peminjaman sebelumnya. Sistem ini diuji dalam dua skenario: sebelum dan sesudah menambahkan preferensi musim pengguna sebagai bagian dari skor rekomendasi (*hybrid score*).

#### 🔹 Sebelum Menambahkan Preferensi Musim

Rekomendasi diberikan berdasarkan kemiripan vektor fitur item dengan profil pengguna (berdasarkan item yang pernah dinyatakan "fit").
Evaluasi Prediktif (skala dinormalisasi ke (2, 4, 6, 8, 10)):
- **RMSE**: 4.5981  
- **MAE** : 3.7143

Distribusi musim dari item rekomendasi tidak sesuai dengan histori musim item yang pernah disukai pengguna.

#### 🔹 Setelah Menambahkan Preferensi Musim (*Hybrid Score*)

Sistem ditingkatkan dengan memperhitungkan preferensi musim berdasarkan riwayat peminjaman pengguna. Skor akhir dihitung sebagai:

$$\text{hybrid_score} = 0.6 × \text{similarity} + 0.2 × \text{season_preference}$$

**Rekomendasi Teratas untuk `user_id = 151944` dengan preferensi musim:**
| item_id | similarity | category |
|---------|------------|----------|
| 132738  | 0.8261     | gown     |
| 1986986 | 0.8240     | gown     |
| 987536  | 0.8212     | gown     |
| 898283  | 0.8195     | gown     |
| 153475  | 0.8193     | gown     |

Evaluasi Hybrid Score (skala dinormalisasi ke (2, 4, 6, 8, 10)):

- **RMSE**: 4.2762  
- **MAE** : 3.4286

Distribusi musim dari item rekomendasi menjadi lebih selaras dengan histori musim pengguna, menunjukkan bahwa sistem berhasil menyesuaikan preferensi waktu (musim) pengguna ke dalam proses rekomendasi.

---

## ✅ Kesimpulan

1. **Model rekomendasi berbasis konten (content-based filtering) telah berhasil membangun sistem rekomendasi yang personal dan berbasis histori pengguna.**
2. **Penambahan preferensi musim meningkatkan akurasi dan relevansi rekomendasi**, yang ditunjukkan oleh penurunan nilai RMSE dari **4.5981** ke **4.2762**, serta MAE dari **3.7143** ke **3.4286**.
3. Sistem ini fleksibel dan dapat dikembangkan lebih lanjut, misalnya dengan mempertimbangkan konteks waktu lainnya, atau menggabungkan elemen collaborative filtering untuk pendekatan hybrid yang lebih kuat.

## Referensi
[1] P. Lops, M. De Gemmis, and G. Semeraro, "Content-based Recommender Systems: State of the Art and Trends," in *Recommender Systems Handbook*, F. Ricci, L. Rokach, B. Shapira, and P. B. Kantor, Eds. Springer, 2011, pp. 73–105. \
[2] J. Ramos, "Using TF-IDF to Determine Word Relevance in Document Queries," in *Proceedings of the First Instructional Conference on Machine Learning*, 2003. \
[3] A. Huang, "Similarity Measures for Text Document Clustering," in *Proc. 6th New Zealand Computer Science Research Student Conf. (NZCSRSC)*, Christchurch, 2008. \
[4] J. Han, J. Pei, and M. Kamber, *Data Mining: Concepts and Techniques*, 3rd ed. Morgan Kaufmann, 2011. \
[5] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," *J. Mach. Learn. Res.*, vol. 12, pp. 2825–2830, 2011. 


> 📌 Catatan: Sistem ini bersifat **Content-Based**, sehingga tidak bergantung pada rating pengguna lain. Sangat cocok untuk cold-start item (item baru), tapi terbatas jika user baru belum pernah menyewa pakaian (cold-start user).
