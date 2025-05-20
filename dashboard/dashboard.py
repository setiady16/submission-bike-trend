import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- PATH KONFIGURASI ---
# Pastikan DATA_PATH mengarah ke lokasi yang benar
# Jika main_data.csv berada di folder yang sama dengan dashboard.py, gunakan "main_data.csv"
# Jika main_data.csv ada di folder 'data' di sebelah dashboard.py, gunakan "data/main_data.csv"
DATA_PATH = "dashboard/main_data.csv" # Sesuaikan ini jika lokasi file berbeda

# --- FUNGSI LOAD & CLEAN DATA ---
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"❌ File tidak ditemukan: `{DATA_PATH}`. Pastikan path dan nama file benar.")
        st.stop()
    df = pd.read_csv(DATA_PATH)
    return df

def clean_data(df_raw):
    df_cleaned = df_raw.copy()

    # 1. Konversi dteday ke datetime
    df_cleaned['dteday'] = pd.to_datetime(df_cleaned['dteday'])

    # 2. Cek dan filter tahun 2024 (jika ada)
    # Asumsi dataset bike sharing berakhir di 2012
    # Jika dataset Anda memiliki rentang tahun yang berbeda, sesuaikan angka 2012 ini.
    if df_cleaned['dteday'].dt.year.max() > 2012:
        st.warning(f"⚠️ Dataset mengandung data tahun {df_cleaned['dteday'].dt.year.max()} atau lebih baru. Memfilter data hingga tahun 2012 sesuai dataset asli.")
        df_cleaned = df_cleaned[df_cleaned['dteday'].dt.year <= 2012]

    # 3. Handle Duplicates
    initial_rows = len(df_cleaned)
    df_cleaned.drop_duplicates(inplace=True)
    if len(df_cleaned) < initial_rows:
        st.info(f"✅ Ditemukan dan dihapus {initial_rows - len(df_cleaned)} data duplikat.")

    # 4. Handle Missing Values (Tambahkan logika ini sesuai notebook Anda jika ada)
    # Contoh:
    # if df_cleaned.isnull().sum().any():
    #     st.info("ℹ️ Terdapat missing values. Menangani missing values...")
    #     df_cleaned.dropna(inplace=True) # Atau imputasi dengan median/mean

    # 5. Handle Outliers (Implementasikan capping jika Anda memutuskan ini di notebook Anda)
    # Contoh untuk capping windspeed:
    # if 'windspeed' in df_cleaned.columns:
    #     Q1_windspeed = df_cleaned['windspeed'].quantile(0.25)
    #     Q3_windspeed = df_cleaned['windspeed'].quantile(0.75)
    #     IQR_windspeed = Q3_windspeed - Q1_windspeed
    #     lower_bound_windspeed = Q1_windspeed - 1.5 * IQR_windspeed
    #     upper_bound_windspeed = Q3_windspeed + 1.5 * IQR_windspeed
    #     df_cleaned['windspeed'] = np.where(df_cleaned['windspeed'] > upper_bound_windspeed, upper_bound_windspeed, df_cleaned['windspeed'])
    #     df_cleaned['windspeed'] = np.where(df_cleaned['windspeed'] < lower_bound_windspeed, lower_bound_windspeed, df_cleaned['windspeed'])
    #     st.info("✅ Outlier pada 'windspeed' ditangani dengan capping.")
    # Jika tidak ada penanganan outlier, Anda bisa menghapus bagian ini atau biarkan sebagai komentar.

    return df_cleaned

# --- LOAD DAN CLEAN DATA AWAL ---
df_raw = load_data()
df = clean_data(df_raw.copy()) # Panggil fungsi cleaning

# Cek kolom yang dibutuhkan setelah cleaning
# Menambahkan 'hr' dan 'weekday' karena digunakan dalam visualisasi
required_columns = ['dteday', 'season', 'weathersit', 'cnt', 'temp', 'registered', 'casual', 'hr', 'weekday']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"❌ Kolom berikut tidak ditemukan dalam data setelah pembersihan: {', '.join(missing_columns)}. Harap periksa dataset Anda.")
    st.stop()


# --- JUDUL DASHBOARD ---
st.title("📊 Dashboard Analisis Penggunaan Sepeda")

# --- SIDEBAR UNTUK FILTER DATA ---
st.sidebar.header("🔍 Filter Data")

# Filter berdasarkan Tanggal (perbaikan .date() untuk st.date_input)
start_date_min = df['dteday'].min().date()
end_date_max = df['dteday'].max().date()
selected_date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [start_date_min, end_date_max], # Nilai default
    min_value=start_date_min,
    max_value=end_date_max
)

# Pastikan selected_date_range memiliki 2 elemen
if len(selected_date_range) == 2:
    start_date_filter = pd.to_datetime(selected_date_range[0])
    end_date_filter = pd.to_datetime(selected_date_range[1])
else: # Handle case where only one date is selected (e.g., initial load or single date picked)
    start_date_filter = pd.to_datetime(selected_date_range[0])
    end_date_filter = pd.to_datetime(selected_date_range[0]) # Treat as single day if only one selected

# Mapping untuk label yang lebih mudah dibaca
season_mapping = {1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur', 4: 'Musim Dingin'}
df['season_label'] = df['season'].map(season_mapping)
selected_season = st.sidebar.multiselect(
    "Pilih Musim", df['season_label'].unique(), default=df['season_label'].unique()
)

weather_mapping = {
    1: "Cerah / Berawan",
    2: "Berkabut / Mendung",
    3: "Hujan Ringan / Salju Ringan",
    4: "Hujan Lebat / Badai"
}
df['weathersit_label'] = df['weathersit'].map(weather_mapping)
selected_weather = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca", df['weathersit_label'].unique(), default=df['weathersit_label'].unique()
)

weekday_mapping = {
    0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'
}
df['weekday_label'] = df['weekday'].map(weekday_mapping)


# --- TERAPKAN FILTER ---
df_filtered = df[
    (df['dteday'] >= start_date_filter) &
    (df['dteday'] <= end_date_filter) &
    (df['season_label'].isin(selected_season)) &
    (df['weathersit_label'].isin(selected_weather))
]

# --- METRIC UTAMA ---
total_users = df_filtered['cnt'].sum()
total_registered = df_filtered['registered'].sum()
total_casual = df_filtered['casual'].sum()

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🚴 Total Pengguna", f"{total_users:,}".replace(",", "."))
with col2:
    st.metric("🤵 Pengguna Terdaftar", f"{total_registered:,}".replace(",", "."))
with col3:
    st.metric("🚶‍♂️ Pengguna Kasual", f"{total_casual:,}".replace(",", "."))
st.markdown("---")


# --- VISUALISASI BERDASARKAN PERTANYAAN BISNIS ---

# Pertanyaan Bisnis 1: Bagaimana pola penggunaan sepeda (total, terdaftar, dan kasual) bervariasi berdasarkan musim dan kondisi cuaca sepanjang tahun?
st.header("1. Pola Penggunaan Sepeda Berdasarkan Musim dan Cuaca")

# 1.1 Tren Penyewaan Sepeda per Bulan (Total, Registered, Casual) - untuk pola musiman
st.subheader("1.1 Tren Penyewaan Sepeda per Bulan")
df_filtered['month'] = df_filtered['dteday'].dt.month
monthly_usage_type = df_filtered.groupby('month')[['cnt', 'registered', 'casual']].sum().reset_index()

fig_monthly_trend, ax_monthly_trend = plt.subplots(figsize=(12, 6))
sns.lineplot(data=monthly_usage_type, x='month', y='cnt', label='Total', marker='o', ax=ax_monthly_trend)
sns.lineplot(data=monthly_usage_type, x='month', y='registered', label='Terdaftar', marker='x', ax=ax_monthly_trend)
sns.lineplot(data=monthly_usage_type, x='month', y='casual', label='Kasual', marker='s', ax=ax_monthly_trend)

ax_monthly_trend.set_xticks(range(1, 13))
ax_monthly_trend.set_xlabel("Bulan")
ax_monthly_trend.set_ylabel("Jumlah Penyewaan")
ax_monthly_trend.set_title("Tren Penyewaan Sepeda (Total, Terdaftar, Kasual) per Bulan")
ax_monthly_trend.grid(True, linestyle='--', alpha=0.5)
ax_monthly_trend.legend(title='Tipe Pengguna')
st.pyplot(fig_monthly_trend)


# 1.2 Tren Penyewaan Sepeda per Tahun (untuk melihat pertumbuhan/penurunan keseluruhan)
st.subheader("1.2 Tren Penyewaan Sepeda Antar Tahun")
df_filtered['year'] = df_filtered['dteday'].dt.year
yearly_usage = df_filtered.groupby('year')[['cnt', 'registered', 'casual']].sum().reset_index()

fig_yearly_trend, ax_yearly_trend = plt.subplots(figsize=(10, 5))
sns.lineplot(data=yearly_usage, x='year', y='cnt', label='Total', marker='o', ax=ax_yearly_trend)
sns.lineplot(data=yearly_usage, x='year', y='registered', label='Terdaftar', marker='x', ax=ax_yearly_trend)
sns.lineplot(data=yearly_usage, x='year', y='casual', label='Kasual', marker='s', ax=ax_yearly_trend)

# Hanya tampilkan tahun yang ada di data
ax_yearly_trend.set_xticks(yearly_usage['year'].unique())
ax_yearly_trend.set_xlabel("Tahun")
ax_yearly_trend.set_ylabel("Total Penyewaan")
ax_yearly_trend.set_title("Tren Penyewaan Sepeda Antar Tahun (2011-2012)")
ax_yearly_trend.grid(True, linestyle='--', alpha=0.5)
ax_yearly_trend.legend(title='Tipe Pengguna')
st.pyplot(fig_yearly_trend)


# 1.3 Rata-rata Penggunaan Sepeda Berdasarkan Musim (seasons)
st.subheader("1.3 Rata-rata Penggunaan Sepeda Berdasarkan Musim")
season_counts = df_filtered.groupby('season_label')[['cnt', 'registered', 'casual']].mean().reset_index()

# Urutkan berdasarkan urutan musim yang benar (Spring, Summer, Fall, Winter)
ordered_seasons = ['Musim Semi', 'Musim Panas', 'Musim Gugur', 'Musim Dingin']
season_counts['season_label'] = pd.Categorical(season_counts['season_label'], categories=ordered_seasons, ordered=True)
season_counts = season_counts.sort_values('season_label')

fig_season_usage, ax_season_usage = plt.subplots(figsize=(10, 5))
sns.barplot(x='season_label', y='cnt', data=season_counts, palette='viridis', ax=ax_season_usage)
ax_season_usage.set_xlabel("Musim")
ax_season_usage.set_ylabel("Rata-rata Penyewaan")
ax_season_usage.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Musim")
st.pyplot(fig_season_usage)


# 1.4 Rata-rata Penggunaan Sepeda Berdasarkan Kondisi Cuaca (weathersit)
st.subheader("1.4 Rata-rata Penggunaan Sepeda Berdasarkan Kondisi Cuaca")
weather_counts = df_filtered.groupby('weathersit_label')[['cnt', 'registered', 'casual']].mean().reset_index()

# Urutkan berdasarkan tingkat keparahan cuaca (lebih baik ke lebih buruk)
ordered_weather = ["Cerah / Berawan", "Berkabut / Mendung", "Hujan Ringan / Salju Ringan", "Hujan Lebat / Badai"]
weather_counts['weathersit_label'] = pd.Categorical(weather_counts['weathersit_label'], categories=ordered_weather, ordered=True)
weather_counts = weather_counts.sort_values('weathersit_label')

fig_weather_usage, ax_weather_usage = plt.subplots(figsize=(10, 5))
sns.barplot(x='weathersit_label', y='cnt', data=weather_counts, palette='plasma', ax=ax_weather_usage)
ax_weather_usage.set_xlabel("Kondisi Cuaca")
ax_weather_usage.set_ylabel("Rata-rata Penyewaan")
ax_weather_usage.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
st.pyplot(fig_weather_usage)

st.markdown("---")


# Pertanyaan Bisnis 2: Bagaimana proporsi penyewaan sepeda oleh pengguna terdaftar dan kasual bervariasi antara hari kerja/akhir pekan dan kondisi cuaca, serta rekomendasi strategis apa yang dapat diberikan?
st.header("2. Proporsi Pengguna Terdaftar dan Kasual")

# 2.1 Proporsi Pengguna Registered vs Casual (Overall)
st.subheader("2.1 Proporsi Pengguna Terdaftar vs Kasual (Overall)")
user_type_overall = df_filtered[['registered', 'casual']].sum().reset_index()
user_type_overall.columns = ['Tipe Pengguna', 'Total']

fig_pie, ax_pie = plt.subplots(figsize=(7, 7))
ax_pie.pie(user_type_overall['Total'], labels=user_type_overall['Tipe Pengguna'], autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62'])
ax_pie.set_title("Proporsi Pengguna Terdaftar vs Kasual (Overall)")
st.pyplot(fig_pie)


# 2.2 Proporsi Pengguna Berdasarkan Hari Kerja vs Akhir Pekan
st.subheader("2.2 Proporsi Pengguna Berdasarkan Hari Kerja vs Akhir Pekan")
# 0: Minggu, 6: Sabtu -> Akhir Pekan. Lainnya Hari Kerja
df_filtered['is_weekend'] = df_filtered['weekday'].isin([0, 6])
df_filtered['day_type'] = df_filtered['is_weekend'].map({True: 'Akhir Pekan', False: 'Hari Kerja'})

user_type_by_daytype = df_filtered.groupby('day_type')[['registered', 'casual']].sum().reset_index()
user_type_by_daytype_melted = user_type_by_daytype.melt(id_vars='day_type', var_name='User Type', value_name='Total Rides')

# Urutkan kategori day_type
ordered_day_type = ['Hari Kerja', 'Akhir Pekan']
user_type_by_daytype_melted['day_type'] = pd.Categorical(user_type_by_daytype_melted['day_type'], categories=ordered_day_type, ordered=True)
user_type_by_daytype_melted = user_type_by_daytype_melted.sort_values('day_type')

fig_daytype, ax_daytype = plt.subplots(figsize=(10, 5))
sns.barplot(data=user_type_by_daytype_melted, x='day_type', y='Total Rides', hue='User Type', ax=ax_daytype, palette='Paired')
ax_daytype.set_xlabel("Tipe Hari")
ax_daytype.set_ylabel("Jumlah Penyewaan")
ax_daytype.set_title("Kontribusi Pengguna Terdaftar & Kasual (Hari Kerja vs Akhir Pekan)")
ax_daytype.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig_daytype)


# 2.3 Proporsi Pengguna Berdasarkan Kondisi Cuaca
st.subheader("2.3 Proporsi Pengguna Berdasarkan Kondisi Cuaca")
user_type_by_weather = df_filtered.groupby('weathersit_label')[['registered', 'casual']].sum().reset_index()
user_type_by_weather_melted = user_type_by_weather.melt(id_vars='weathersit_label', var_name='User Type', value_name='Total Rides')

# Urutkan kategori cuaca
user_type_by_weather_melted['weathersit_label'] = pd.Categorical(user_type_by_weather_melted['weathersit_label'], categories=ordered_weather, ordered=True)
user_type_by_weather_melted = user_type_by_weather_melted.sort_values('weathersit_label')

fig_weather_prop, ax_weather_prop = plt.subplots(figsize=(10, 5))
sns.barplot(data=user_type_by_weather_melted, x='weathersit_label', y='Total Rides', hue='User Type', ax=ax_weather_prop, palette='pastel')
ax_weather_prop.set_xlabel("Kondisi Cuaca")
ax_weather_prop.set_ylabel("Jumlah Penyewaan")
ax_weather_prop.set_title("Kontribusi Pengguna Terdaftar & Kasual Berdasarkan Kondisi Cuaca")
ax_weather_prop.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig_weather_prop)


st.markdown("---")

# --- KESIMPULAN DAN REKOMENDASI ---
st.header("💡 Kesimpulan dan Rekomendasi")

st.subheader("Kesimpulan untuk Pertanyaan 1: Pola Penggunaan Sepeda Berdasarkan Musim dan Cuaca")
st.markdown("""
- **Pola Musiman:** Penggunaan sepeda (total, terdaftar, dan kasual) menunjukkan pola musiman yang jelas, dengan puncak penyewaan terjadi pada **Musim Panas** (sekitar Juni-Agustus) dan **Musim Gugur** (sekitar September-November). Bulan-bulan ini kemungkinan besar memiliki kondisi cuaca yang paling ideal untuk bersepeda. Sebaliknya, **Musim Dingin** (Desember-Februari) dan **Musim Semi** awal menunjukkan jumlah penyewaan yang jauh lebih rendah.
- **Tren Antar Tahun:** Dari tahun 2011 ke 2012, terdapat **peningkatan signifikan** dalam total jumlah penyewaan sepeda, baik oleh pengguna terdaftar maupun kasual, menunjukkan pertumbuhan adopsi layanan.
- **Pengaruh Cuaca:** Kondisi cuaca **Cerah / Berawan** berkorelasi positif dengan jumlah penyewaan tertinggi. Semakin buruk kondisi cuaca (misalnya, hujan ringan/salju ringan), semakin rendah rata-rata penyewaan sepeda.
""")
st.subheader("Rekomendasi untuk Pertanyaan 1:")
st.markdown("""
- **Manajemen Inventaris Musiman:** Tingkatkan ketersediaan sepeda dan staf dukungan pada bulan-bulan puncak (Musim Panas dan Gugur) untuk memenuhi permintaan yang tinggi dan memaksimalkan pendapatan. Kurangi ketersediaan pada musim sepi untuk efisiensi operasional.
- **Promosi Musim Dingin:** Pertimbangkan kampanye promosi atau diskon khusus pada Musim Dingin untuk mendorong penggunaan sepeda meskipun kondisi cuaca kurang mendukung.
- **Strategi Cuaca:** Integrasikan prakiraan cuaca ke dalam operasional untuk penyesuaian ketersediaan sepeda dan penempatan stasiun secara dinamis, terutama saat cuaca buruk diperkirakan.
""")

st.subheader("Kesimpulan untuk Pertanyaan 2: Proporsi Pengguna Terdaftar dan Kasual")
st.markdown("""
- **Dominasi Pengguna Terdaftar:** Pengguna terdaftar secara konsisten menyumbang **proporsi mayoritas** dari total penyewaan, terutama pada **hari kerja**, menunjukkan bahwa mereka adalah komuter atau pengguna rutin.
- **Pengguna Kasual di Akhir Pekan:** Pengguna kasual memiliki **proporsi kontribusi yang lebih tinggi pada akhir pekan** dibandingkan hari kerja, mengindikasikan penggunaan untuk tujuan rekreasi atau wisata.
- **Sensitivitas Cuaca Kasual:** Pengguna kasual menunjukkan **sensitivitas yang lebih tinggi terhadap kondisi cuaca buruk**. Proporsi mereka menurun drastis saat cuaca tidak ideal, sementara pengguna terdaftar cenderung lebih stabil.
""")
st.subheader("Rekomendasi untuk Pertanyaan 2:")
st.markdown("""
- **Perkuat Loyalitas Pengguna Terdaftar:** Fokus pada program loyalitas, paket langganan yang menarik, dan perbaikan layanan untuk mempertahankan dan meningkatkan frekuensi pengguna terdaftar.
- **Targetkan Pengguna Kasual untuk Rekreasi:** Kembangkan strategi pemasaran khusus (misalnya, promosi paket tur sepeda, kemitraan dengan tempat wisata) yang menargetkan pengguna kasual pada akhir pekan dan hari libur.
- **Konversi Pengguna Kasual:** Tawarkan insentif atau program perkenalan untuk mendorong pengguna kasual mendaftar sebagai anggota, terutama setelah pengalaman positif pada cuaca baik.
- **Mitigasi Dampak Cuaca:** Untuk pengguna kasual, sediakan opsi atau informasi alternatif (misalnya, promosi untuk hari cerah berikutnya) saat cuaca buruk, atau pertimbangkan untuk menawarkan sepeda dengan fitur perlindungan cuaca.
""")

# --- FOOTER ---
st.markdown("---")
st.markdown("**Dashboard Analisis Penggunaan Sepeda** | Dikembangkan dengan dedikasi dan data yang akurat.")