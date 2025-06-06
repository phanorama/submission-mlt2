# -*- coding: utf-8 -*-
"""notebook MLT2

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_fDKcRO7XERsvUYK9s_0XL-O_OO5EorN

# Install & Import Library
"""

!pip install kagglehub -q

import kagglehub
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import scipy.sparse

"""# Load Data

load dataset dari kaggle
"""

# Download latest version
path = kagglehub.dataset_download("rmisra/clothing-fit-dataset-for-size-recommendation")

print("Path to dataset files:", path)

"""ubah dari json format ke bentuk dataframe pandas"""

json_path = os.path.join(path, "renttherunway_final_data.json")
df = pd.read_json(json_path, lines=True)
df.head()

"""# Eksplorasi Data

kita menyimpan dataset asli terlebih dahulu
"""

df_ori = df.copy()

"""untuk melihat jumlah baris dan kolom"""

print(f"jumlah baris = {df.shape[0]}, jumlah kolom = {df.shape[1]}")

"""untuk melihat jumlah data duplikat"""

print(f"Jumlah data duplikat: {df.duplicated().sum()}")

"""informasi lengkap dataset"""

df.info()

"""muat ulang `review_date` ke bentuk datetime"""

df['review_date'] = pd.to_datetime(df['review_date'])
df['review_date']

"""lihat label unik di beberapa kolom"""

df['bust size'].unique()

df['rating'].unique()

df['rented for'].unique()

df['body type'].unique()

df['category'].unique()

"""cek data kosong"""

print(df.isna().sum(), f", Jumlah baris: {len(df)}, Jumlah missing values: {df.isna().sum().sum()}")

"""# Data Preparation

karena tidak membutuhkan `review_summary` dan `review_text` dari tujuan kita, maka akan dibuang saja
"""

df.drop(columns=['review_summary', 'review_text'], inplace=True)

"""karena fitur `rating` dan `rented for` memiliki sedikit missing value, maka akan di drop saja"""

df = df.dropna(subset=['rating', 'rented for'])

"""untuk mengisi nilai kosong `bust size` dan `body type`, menggunakan modus karena type data object"""

# Imputasi kolom kategori dengan modus
df['bust size'] = df['bust size'].fillna(df['bust size'].mode()[0])
df['body type'] = df['body type'].fillna(df['body type'].mode()[0])

"""untuk melakukan imputasi kolom `weight`, akan melihat distribusi datanya sebagai berikut"""

df['weight'] = df['weight'].str.replace('lbs', '', regex=False).astype(float)

df['weight'].skew()

"""karena sangat skewness (1.39555123013035 > 1), maka akan menggunakan median untuk imputasi kolom `weight` dan diubah ke satuan standar internasional (kg)"""

df['weight'] = df['weight'].fillna(df['weight'].median()).apply(lambda x: x * 0.453592)

"""lakukan hal yang sama untuk `height` dan `age` dengan cek distribusi dahulu. `height` diubah dari feet'inchi" menjadi satuan inchi"""

df['height'] = df['height'].apply(lambda x: int(x.split("'")[0]) * 12 + int(x.split('"')[0].split()[-1]) if pd.notnull(x) else np.nan)

print(f"{df['height'].skew(), df['age'].skew()}")

"""karena `height`~ 0, digunakan mean untuk imputasi dan diubah satuan dari inchi ke satuan standar internasional (cm). sedangkan `age` menggunakan median karena nilai skewed > 1, menandakan data terdistribusi miring"""

df['height'] = df['height'].fillna(df['height'].mean()).apply(lambda x: x * 2.54)
df['age'] = df['age'].fillna(df['age'].median())

"""kemudian untuk memastikan, akan dicek lagi missing values sebagai berikut"""

df.isna().sum()

df.head()

"""data hampir dirapihkan, sekarang dilakukan perapihan data lagi pada kolom `bust size`, `weight` dan `review date`

disini akan membatasi dua digit belakang koma untuk `weight`
"""

df['weight'] = df['weight'].round(2)

df.head()

"""sekarang kita ingin mendalami fitur `bust size`, dikarenakan memiliki banyak jenis satuan. `bust size`(Lingkar dada) kita pecah jadi dua kolom, yaitu `band_size` (Lingkar dada (di bawah payudara, sekitar tulang rusuk)) dan `cup_size_raw` (Selisih antara lingkar payudara dan lingkar dada) dimana `band_size` menyimpan angkanya dan `cup_size_raw` menyimpan kode hurufnya yang bersifat kategorikal ordinal"""

def parse_bust_size(size):
    if pd.isnull(size):
        return np.nan, np.nan
    match = re.match(r"(\d+)([a-zA-Z/+]+)", size)
    if match:
        band = int(match.group(1))
        cup = match.group(2).lower().replace('+', '').replace('/', '')
        return band, cup
    return np.nan, np.nan

df[['band_size', 'cup_size_raw']] = df['bust size'].apply(lambda x: pd.Series(parse_bust_size(x)))

df.head()

"""kemudian kita ingin `review date` dijadikan `season`, karena kita ingin tahu kapan pengguna menyewa tersebut sehingga memberikan rating yang sedemikian tersebut"""

def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

# Buat kolom baru 'season'
df['season'] = df['review_date'].apply(get_season)

df.head()

"""sekarang kita membuang kolom `bust size` dan `review_date` karena udah di representasikan dalam bentuk lain"""

df.drop(columns=['bust size', 'review_date'], inplace=True)

df.head()

"""untuk memastikan, cek ulang missing value apakah ada atau tidak"""

df.isna().sum()

"""lalu kita akan cek karakteristik label dari `cup_size_raw`"""

df['cup_size_raw'].unique()

"""kita lihat terdapat `ddde` pada jenis label. ini berasal dari fitur sebelumnya yang pake `ddd/e` seperti 34ddd/e (bisa diliat jenis label di bagian `bust size` di data preparation). dalam hal ini, `ddde` akan diganti dengan `e`"""

df['cup_size_raw'] = df['cup_size_raw'].replace('ddde', 'e')

"""sekarang akan kita ingin melihat lagi jenis label `rented for`"""

df['rented for'].unique()

df[df['rented for'] == 'party: cocktail']

"""`party: cocktail` akan digabungkan ke `party` untuk bentuk perumuman"""

df['rented for'] = df['rented for'].replace({'party: cocktail': 'party'})

"""sekarang akan kita ingin melihat lagi jenis label `categorical` (masih sama bentuknya di bagian data preparation)"""

df['category'].unique()

"""ada banyak duplikasi dalam bentuk jamak dan tunggal, kita akan konsilidasi dalam satu bentuk pada proses berikut"""

consolidation_map = {
    'pant': 'pants',
    'legging': 'leggings',
    'trouser': 'trousers',
    'culotte': 'culottes',
    'skirt': 'skirts'
}

df['category'] = df['category'].replace(consolidation_map)

"""dan ada dalam bentuk typo dan sinonim teks, kita akan perbaiki dalam satu bentuk pada proses berikut"""

alternate_mapping = {
    'sweatshirt': 'sweatershirt',
    'tight': 'tights',
    'kaftan': 'caftan',
    'tee' : 't-shirt'
}

df['category'] = df['category'].replace(alternate_mapping)

"""lalu kita cek lagi"""

df['category'].unique()

"""kita melihat ada barang yang tidak relevan, misalnya print dan for"""

df[df['category'] == 'for']

"""`category: for` terlihat hanya untuk barang dengan `item_id` = 2270513, kita akan analisis `review_text` dari dataset aslinya"""

# Tampilkan seluruh isi string di kolom
pd.set_option('display.max_colwidth', None)
df_ori[df_ori['item_id'] == 2270513]['review_text']

"""terlihat ini kategori sebagai 'turtleneck' untuk for ini, sekarang kita analisis 'print' lanjutannya"""

df[df['category'] == 'print']

"""hal yang sama terjadi untuk `category: print`, hanya terlihat untuk `item_id: 545632` kita akan melihat `review_text` barang tersebut dari dataset aslinya"""

pd.set_option('display.max_colwidth', None)
df_ori[df_ori['item_id'] == 545632]['review_text'].head()

"""terlihat secara eksplisit ini kategori serupa dress untuk print. selanjutnya kita akan ubah dalam satu bentuk sebagai berikut"""

anomali_mapping = {
    'for': 'turtleneck',
    'print': 'dress'
}

df['category'] = df['category'].replace(anomali_mapping)

"""sekarang `category` sudah aman dengan jenis label sebagai berikut"""

df['category'].unique()

"""karena tidak ada kejanggalan pada data ketegorical yang lain, kemudian akan di cek apakah ada data yang terduplikat"""

df.duplicated().sum()

"""kita akan menghapus data duplikat"""

df = df.drop_duplicates().copy()

df.duplicated().sum()

"""kita gabungkan data kategorical jadi satu"""

df['text_features'] = (
    df['category'].astype(str) + ' ' +
    df['rented for'].astype(str) + ' ' +
    df['season'].astype(str) + ' ' +
    df['body type'].astype(str) + ' ' +
    df['cup_size_raw'].astype(str)
)

"""kita akan melakukan vektorisasi dengan tf-idf untuk data kategorikal"""

tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df['text_features'])  # Bentuk: (n_samples, n_tfidf_features)

"""sekarang lakukan normalisasi untuk data numerik"""

numerical_features = ['weight', 'height', 'size', 'age', 'band_size']

scaler = StandardScaler()
scaled_numerical = scaler.fit_transform(df[numerical_features])  # Bentuk: (n_samples, n_numerical_features)

"""sekarang kita gabungkan keduanya"""

# Konversi scaled_numerical ke bentuk sparse agar bisa digabung
numerical_sparse = scipy.sparse.csr_matrix(scaled_numerical)

# Gabungkan fitur akhir
item_vectors = scipy.sparse.hstack([tfidf_matrix, numerical_sparse])  # Shape: (n_items, total_features)

"""dataset telah siap digunakan untuk tahap selanjutnya.

# Model Development dengan Content Based Filtering

Tujuan :
1. Merekomendasikan pakaian baru yang cocok untuk pengguna berdasarkan histori pakaian yang telah mereka merasa pas ("fit").
2. Merekomendasikan pakaian baru yang cocok untuk pengguna berdasarkan histori pakaian yang telah mereka merasa pas ("fit") di musim saat direkomendasikan.

Buat Profil User dari Item yang "fit"
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

user_id = 151944

# Ambil item user yang 'fit'
user_items = df[(df['user_id'] == user_id) & (df['fit'] == 'fit')]
user_indices = user_items.index

if len(user_indices) == 0:
    print(f"❗ User {user_id} belum memiliki item dengan 'fit'. Tidak bisa membuat user profile.")
    user_profile_vector = None
else:
    user_profile_vector = np.asarray(item_vectors[user_indices].mean(axis=0)).reshape(1, -1)

"""Hitung Similarity dan Rekomendasi"""

if user_profile_vector is not None:
    # Hitung cosine similarity user profile vs semua item
    similarity_scores = cosine_similarity(user_profile_vector, item_vectors).flatten()

    # Copy df supaya tidak overwrite
    df_copy = df.copy()
    df_copy['similarity'] = similarity_scores

    # Filter item yang sudah dilihat user
    seen_item_ids = df_copy[df_copy['user_id'] == user_id]['item_id'].unique()
    candidate_df = df_copy[~df_copy['item_id'].isin(seen_item_ids)].copy()

    # Ambil top-N rekomendasi
    top_n = 5
    recommendations = candidate_df.sort_values(by='similarity', ascending=False).head(top_n)

    print(f"Rekomendasi untuk user {user_id}:")
    print(recommendations[['item_id', 'similarity', 'category']])
else:
    recommendations = None

"""sekarang telah dibikin sistem rekomendasi, sebagai contoh `user_id = 151944` direkomendasikan `item_id = [1531631, 162634, 1487216, 432275, 131533]`"""

seasons = df['season'].unique()

for season in seasons:
    print(f"\n📅 Rekomendasi untuk musim: {season}")

    seasonal_candidates = candidate_df[candidate_df['season'] == season]

    if len(seasonal_candidates) == 0:
        print("Tidak ada kandidat item untuk musim ini.")
        continue

    seasonal_top = seasonal_candidates.sort_values(by='similarity', ascending=False).head(top_n)

    print(seasonal_top[['item_id', 'similarity', 'category', 'season']])

"""selain itu, juga bisa ditampilkan rekomendasi `item_id` sesuai musim. tinggal diintegrasikan musimnya dengan tanggal kejadian saat itu di interface pengguna

## Evaluation
"""

from sklearn.metrics import mean_squared_error, mean_absolute_error

# Ambil rating asli user
rated_items = df.dropna(subset=['rating'])
rated_df = df_copy[(df_copy['item_id'].isin(rated_items['item_id'])) & (df_copy['user_id'] == user_id)].copy()

if rated_df.empty:
    print("⚠️ User belum punya rating untuk evaluasi.")
else:
    y_pred = rated_df['similarity'].values
    y_true = rated_df['rating'].values

    # Normalisasi similarity ke 2, 4, 6, 8, 10
    valid_ratings = np.array([2.0, 4.0, 6.0, 8.0, 10.0])

    if y_pred.max() == y_pred.min():
        y_pred_norm = np.full_like(y_pred, 6)
    else:
        y_pred_scaled = 1 + (y_pred - y_pred.min()) / (y_pred.max() - y_pred.min()) * 9
        y_pred_norm = np.array([valid_ratings[np.abs(valid_ratings - val).argmin()] for val in y_pred_scaled])

    rmse = np.sqrt(mean_squared_error(y_true, y_pred_norm))
    mae = mean_absolute_error(y_true, y_pred_norm)

    print("\n📈 Evaluasi Prediktif (Normalized to 1–10):")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE : {mae:.4f}")

# Lihat distribusi musim dari item yang disukai user
liked_seasons = df[(df['user_id'] == user_id) & (df['fit'] == 'fit')]['season'].value_counts()

# Bandingkan dengan musim dari rekomendasi teratas
recommended_seasons = recommendations['season'].value_counts()

# Gabungkan untuk perbandingan
season_compare = pd.DataFrame({
    'Liked by user': liked_seasons,
    'Recommended': recommended_seasons
}).fillna(0)

season_compare.plot(kind='bar', figsize=(8,4), title='Perbandingan Musim: History vs Rekomendasi')
plt.ylabel('Jumlah Item')
plt.show()

"""item yang disukai user hanya ada di fall dan summer, dan rekomendasi sistem malah dominan di spring, kita akan tambahkan Preferensi Musim ke rekomendasi"""

# Hitung preferensi musim user (dari item 'fit')
liked_seasons = df[(df['user_id'] == user_id) & (df['fit'] == 'fit')]['season'].value_counts(normalize=True)

# Gabungkan ke candidate_df
candidate_df['season_pref'] = candidate_df['season'].map(liked_seasons).fillna(0)

# Gabungkan dengan similarity
alpha = 0.6  # bobot similarity
beta = 0.2   # bobot musim

candidate_df['hybrid_score'] = alpha * candidate_df['similarity'] + beta * candidate_df['season_pref']

# Ambil rekomendasi baru
recommendations = candidate_df.sort_values(by='hybrid_score', ascending=False).head(top_n)
print(recommendations[['item_id', 'similarity', 'category']])

recommended_seasons = recommendations['season'].value_counts()

season_compare = pd.DataFrame({
    'Liked by user': liked_seasons,
    'Recommended (w/ season pref)': recommended_seasons
}).fillna(0)

season_compare.plot(kind='bar', figsize=(8,4), title='Perbandingan Musim: User History vs Rekomendasi Baru')
plt.ylabel('Jumlah Item')
plt.show()

"""kemudian hitung ulang metrik evaluasi"""

from sklearn.metrics import mean_squared_error, mean_absolute_error

# Ambil item yang pernah dirating user
rated_items = df.dropna(subset=['rating'])
rated_df = df_copy[(df_copy['item_id'].isin(rated_items['item_id'])) & (df_copy['user_id'] == user_id)].copy()

if rated_df.empty:
    print("⚠️ User belum punya rating untuk evaluasi.")
else:
    # Hitung preferensi musim user
    liked_seasons = df[(df['user_id'] == user_id) & (df['fit'] == 'fit')]['season'].value_counts(normalize=True)
    rated_df['season_pref'] = rated_df['season'].map(liked_seasons).fillna(0)

    # Hitung hybrid_score untuk rated_df
    alpha = 0.6
    beta = 0.2
    rated_df['hybrid_score'] = alpha * rated_df['similarity'] + beta * rated_df['season_pref']

    # Ground truth & prediction
    y_true = rated_df['rating'].values
    y_pred_raw = rated_df['hybrid_score'].values

    # Normalisasi ke range 2,4,6,8,10
    valid_ratings = np.array([2.0, 4.0, 6.0, 8.0, 10.0])

    if y_pred_raw.max() == y_pred_raw.min():
        y_pred_norm = np.full_like(y_pred_raw, 6)
    else:
        y_pred_scaled = 1 + (y_pred_raw - y_pred_raw.min()) / (y_pred_raw.max() - y_pred_raw.min()) * 9
        y_pred_norm = np.array([valid_ratings[np.abs(valid_ratings - val).argmin()] for val in y_pred_scaled])

    # Hitung metrik
    rmse = np.sqrt(mean_squared_error(y_true, y_pred_norm))
    mae = mean_absolute_error(y_true, y_pred_norm)

    print("\n📈 Evaluasi Hybrid Score (Normalized to 1–10):")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE : {mae:.4f}")