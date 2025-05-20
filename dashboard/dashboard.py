import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import date # Penting: Import the date object specifically

# --- PATH KONFIGURASI ---
# Sesuaikan path ini agar sesuai dengan lokasi file main_data.csv Anda.
# Contoh: Jika main_data.csv ada di folder 'dashboard' di samping dashboard.py:
DATA_PATH = "dashboard/main_data.csv"
# Jika main_data.csv ada di folder yang sama dengan dashboard.py:
# DATA_PATH = "main_data.csv"

# --- FUNGSI LOAD & CLEAN DATA ---
@st.cache_data
def load_data():
    """
    Memuat dataset dari path yang ditentukan.
    Menampilkan error dan menghentikan aplikasi jika file tidak ditemukan.
    """
    if not os.path.exists(DATA_PATH):
        st.error(f"❌ File tidak ditemukan: `{DATA_PATH}`. Pastikan path dan nama file benar.")
        st.stop()
    df = pd.read_csv(DATA_PATH)
    return df

def clean_data(df_raw):
    """
    Melakukan pembersihan data pada DataFrame mentah.
    Meliputi konversi tipe data, penanganan duplikat, dan filter tahun.
    """
    df_cleaned = df_raw.copy()

    # 1. Konversi 'dteday' ke tipe datetime
    df_cleaned['dteday'] = pd.to_datetime(df_cleaned['dteday'])

    # 2. Cek dan filter data tahun yang tidak relevan (asumsi dataset bike sharing berakhir di 2012)
    # Sesuaikan angka 2012 ini jika rentang tahun dataset Anda berbeda.
    if df_cleaned['dteday'].dt.year.max() > 2012:
        st.warning(f"⚠️ Dataset mengandung data tahun {df_cleaned['dteday'].dt.year.max()} atau lebih baru. Memfilter data hingga tahun 2012 sesuai dataset asli.")
        df_cleaned = df_cleaned[df_cleaned['dteday'].dt.year <= 2012]

    # 3. Handle Duplicates
    initial_rows = len(df_cleaned)
    df_cleaned.drop_duplicates(inplace=True)
    if len(df_cleaned) < initial_rows:
        st.info(f"✅ Ditemukan dan dihapus {initial_rows - len(df_cleaned)} data duplikat.")

    # Tambahkan proses cleaning lainnya sesuai notebook Anda (missing values, outliers, dll.)
    # Contoh:
    # df_cleaned.dropna(inplace=True) # Jika Anda menangani missing values dengan dropna
    # df_cleaned['windspeed'] = np.where(df_cleaned['windspeed'] > upper_bound, upper_bound, df_cleaned['windspeed']) # Contoh capping

    return df_cleaned

# --- LOAD DAN CLEAN DATA AWAL ---
df_raw = load_data()
df = clean_data(df_raw.copy()) # Panggil fungsi cleaning

# Pastikan kolom yang dibutuhkan ada setelah cleaning
# Menambahkan 'hr' dan 'weekday' karena digunakan dalam analisis di notebook
required_columns = ['dteday', 'season', 'weathersit', 'cnt', 'temp', 'registered', 'casual', 'hr', 'weekday']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"❌ Kolom berikut tidak ditemukan dalam data setelah pembersihan: {', '.join(missing_columns)}. Harap periksa dataset Anda atau sesuaikan `required_columns`.")
    st.stop()

# --- JUDUL DASHBOARD ---
st.title("📊 Dashboard Analisis Penggunaan Sepeda")

# --- SIDEBAR UNTUK FILTER DATA ---
st.sidebar.header("🔍 Filter Data")

# Filter berdasarkan Tanggal (Memastikan tipe data datetime.date untuk st.date_input)
# Mengambil tanggal min/max dari DataFrame yang sudah di-clean dan diubah ke datetime.date
min_date_val = df['dteday'].min().date()
max_date_val = df['dteday'].max().date()

selected_date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=[min_date_val, max_date_val], # Gunakan 'value' bukan 'default'
    min_value=min_date_val,
    max_value=max_date_val
)

# Konversi tanggal yang dipilih dari date_input kembali ke Timestamp Pandas untuk filtering
# Handle kasus di mana selected_date_range mungkin hanya satu elemen saat pertama kali dimuat
if len(selected_date_range) == 2:
    start_date_filter = pd.to_datetime(selected_date_range[0])
    end_date_filter = pd.to_datetime(selected_date_range[1])
elif len(selected_date_range) == 1:
    start_date_filter = pd.to_datetime(selected_date_range[0])
    end_date_filter = pd.to_datetime(selected_date_range[0]) # Jika hanya 1 tanggal dipilih, anggap sebagai rentang 1 hari
else: # Fallback jika ada masalah, gunakan rentang penuh dari data asli
    start_date_filter = df['dteday'].min()
    end_date_filter = df['dteday'].max()


# Mapping untuk label yang lebih mudah dibaca pada filter dan visualisasi
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


# --- TERAPKAN FILTER PADA DATAFRAME UTAMA ---
df_filtered = df[
    (df['dteday'] >= start_date_filter) &
    (df['dteday'] <= end_date_filter) &
    (df['season_label'].isin(selected_season)) &
    (df['weathersit_label'].isin(selected_weather))
].copy() # Tambahkan .copy() untuk menghindari SettingWithCopyWarning jika Anda memodifikasi df_filtered lebih lanjut

# --- METRIC UTAMA (Selalu di atas) ---
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

# Pertanyaan Bisnis 1: Apakah terdapat pola musiman yang signifikan dalam jumlah penyewaan sepeda berdasarkan bulan dan tahun?
st.header("1. Pola Musiman dalam Penggunaan Sepeda")

# 1.1 Tren Rata-rata Penyewaan Sepeda per Bulan (Total, Registered, Casual)
# (Sesuai dengan plot di Notebook)
st.subheader("1.1 Tren Rata-rata Penyewaan Sepeda per Bulan")
df_filtered['month'] = df_filtered['dteday'].dt.month # Pastikan kolom 'month' ada
monthly_usage_type = df_filtered.groupby('month')[['cnt', 'registered', 'casual']].mean().reset_index() # Gunakan mean() sesuai notebook

fig_monthly_trend, ax_monthly_trend = plt.subplots(figsize=(12, 6))
sns.lineplot(data=monthly_usage_type, x='month', y='cnt', label='Total', marker='o', ax=ax_monthly_trend)
sns.lineplot(data=monthly_usage_type, x='month', y='registered', label='Terdaftar', marker='x', ax=ax_monthly_trend)
sns.lineplot(data=monthly_usage_type, x='month', y='casual', label='Kasual', marker='s', ax=ax_monthly_trend)

ax_monthly_trend.set_xticks(range(1, 13))
ax_monthly_trend.set_xlabel("Bulan")
ax_monthly_trend.set_ylabel("Rata-rata Penyewaan")
ax_monthly_trend.set_title("Tren Rata-rata Penyewaan Sepeda (Total, Terdaftar, Kasual) per Bulan")
ax_monthly_trend.grid(True, linestyle='--', alpha=0.5)
ax_monthly_trend.legend(title='Tipe Pengguna')
st.pyplot(fig_monthly_trend)


# 1.2 Tren Rata-rata Penyewaan Sepeda per Tahun (Total, Registered, Casual)
# (Sesuai dengan plot di Notebook)
st.subheader("1.2 Tren Rata-rata Penyewaan Sepeda Antar Tahun")
df_filtered['year'] = df_filtered['dteday'].dt.year # Pastikan kolom 'year' ada
yearly_usage = df_filtered.groupby('year')[['cnt', 'registered', 'casual']].mean().reset_index() # Gunakan mean() sesuai notebook

fig_yearly_trend, ax_yearly_trend = plt.subplots(figsize=(10, 5))
sns.lineplot(data=yearly_usage, x='year', y='cnt', label='Total', marker='o', ax=ax_yearly_trend)
sns.lineplot(data=yearly_usage, x='year', y='registered', label='Terdaftar', marker='x', ax=ax_yearly_trend)
sns.lineplot(data=yearly_usage, x='year', y='casual', label='Kasual', marker='s', ax=ax_yearly_trend)

ax_yearly_trend.set_xticks(yearly_usage['year'].unique())
ax_yearly_trend.set_xlabel("Tahun")
ax_yearly_trend.set_ylabel("Rata-rata Penyewaan")
ax_yearly_trend.set_title("Tren Rata-rata Penyewaan Sepeda Antar Tahun")
ax_yearly_trend.grid(True, linestyle='--', alpha=0.5)
ax_yearly_trend.legend(title='Tipe Pengguna')
st.pyplot(fig_yearly_trend)


# Tambahan dari Pertanyaan 1. Ini ada di notebook Anda tapi mungkin belum di dashboard.
# Rata-rata Penggunaan Sepeda Berdasarkan Musim (cnt)
st.subheader("1.3 Rata-rata Penggunaan Sepeda Berdasarkan Musim")
season_avg_counts = df_filtered.groupby('season_label')['cnt'].mean().reset_index()

ordered_seasons = ['Musim Semi', 'Musim Panas', 'Musim Gugur', 'Musim Dingin']
season_avg_counts['season_label'] = pd.Categorical(season_avg_counts['season_label'], categories=ordered_seasons, ordered=True)
season_avg_counts = season_avg_counts.sort_values('season_label')

fig_season_usage, ax_season_usage = plt.subplots(figsize=(10, 5))
sns.barplot(x='season_label', y='cnt', data=season_avg_counts, palette='viridis', ax=ax_season_usage)
ax_season_usage.set_xlabel("Musim")
ax_season_usage.set_ylabel("Rata-rata Penyewaan")
ax_season_usage.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Musim")
st.pyplot(fig_season_usage)


# Tambahan dari Pertanyaan 1. Ini ada di notebook Anda tapi mungkin belum di dashboard.
# Rata-rata Penggunaan Sepeda Berdasarkan Kondisi Cuaca (cnt)
st.subheader("1.4 Rata-rata Penggunaan Sepeda Berdasarkan Kondisi Cuaca")
weather_avg_counts = df_filtered.groupby('weathersit_label')['cnt'].mean().reset_index()

ordered_weather_for_plot = ["Cerah / Berawan", "Berkabut / Mendung", "Hujan Ringan / Salju Ringan", "Hujan Lebat / Badai"]
weather_avg_counts['weathersit_label'] = pd.Categorical(weather_avg_counts['weathersit_label'], categories=ordered_weather_for_plot, ordered=True)
weather_avg_counts = weather_avg_counts.sort_values('weathersit_label')

fig_weather_usage, ax_weather_usage = plt.subplots(figsize=(10, 5))
sns.barplot(x='weathersit_label', y='cnt', data=weather_avg_counts, palette='plasma', ax=ax_weather_usage)
ax_weather_usage.set_xlabel("Kondisi Cuaca")
ax_weather_usage.set_ylabel("Rata-rata Penyewaan")
ax_weather_usage.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
st.pyplot(fig_weather_usage)

st.markdown("---")


# Pertanyaan Bisnis 2: Seberapa besar kontribusi pengguna terdaftar (registered) dibandingkan dengan pengguna kasual (casual) dalam total penyewaan sepeda?
st.header("2. Proporsi Pengguna Terdaftar dan Kasual")

# 2.1 Proporsi Pengguna Registered vs Casual (Overall)
# (Sesuai dengan pie chart di Notebook)
st.subheader("2.1 Proporsi Pengguna Terdaftar vs Kasual (Overall)")
user_type_overall = df_filtered[['registered', 'casual']].sum().reset_index()
user_type_overall.columns = ['Tipe Pengguna', 'Total']

fig_pie, ax_pie = plt.subplots(figsize=(7, 7))
# Pastikan labels sesuai dengan 'Tipe Pengguna'
ax_pie.pie(user_type_overall['Total'], labels=['Terdaftar', 'Kasual'], autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62'])
ax_pie.set_title("Proporsi Pengguna Terdaftar vs Kasual (Overall)")
st.pyplot(fig_pie)


# 2.2 Kontribusi Pengguna Berdasarkan Hari Kerja vs Akhir Pekan
# (Sesuai dengan bar plot di Notebook)
st.subheader("2.2 Kontribusi Pengguna Berdasarkan Hari Kerja vs Akhir Pekan")
# 0: Minggu, 6: Sabtu -> Akhir Pekan. Lainnya Hari Kerja
df_filtered['is_weekend'] = df_filtered['weekday'].isin([0, 6])
df_filtered['day_type'] = df_filtered['is_weekend'].map({True: 'Akhir Pekan', False: 'Hari Kerja'})

user_type_by_daytype = df_filtered.groupby('day_type')[['registered', 'casual']].sum().reset_index()
user_type_by_daytype_melted = user_type_by_daytype.melt(id_vars='day_type', var_name='User Type', value_name='Total Rides')

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


# 2.3 Kontribusi Pengguna Berdasarkan Kondisi Cuaca
# (Sesuai dengan bar plot di Notebook)
st.subheader("2.3 Kontribusi Pengguna Berdasarkan Kondisi Cuaca")
user_type_by_weather = df_filtered.groupby('weathersit_label')[['registered', 'casual']].sum().reset_index()
user_type_by_weather_melted = user_type_by_weather.melt(id_vars='weathersit_label', var_name='User Type', value_name='Total Rides')

user_type_by_weather_melted['weathersit_label'] = pd.Categorical(user_type_by_weather_melted['weathersit_label'], categories=ordered_weather_for_plot, ordered=True)
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

st.subheader("Kesimpulan untuk Pertanyaan 1: Pola Musiman dalam Penggunaan Sepeda")
st.markdown("""
- **Pola Musiman yang Signifikan:** Analisis menunjukkan pola musiman yang jelas, dengan puncak penyewaan sepeda (baik total, terdaftar, maupun kasual) terjadi pada **Musim Panas** (sekitar bulan Juni-Agustus) dan **Musim Gugur** (sekitar September-November). Ini menunjukkan bahwa cuaca hangat dan kondisi yang lebih stabil sangat mendukung aktivitas bersepeda. Sebaliknya, **Musim Dingin** dan awal **Musim Semi** memiliki jumlah penyewaan yang jauh lebih rendah.
- **Tren Tahunan Meningkat:** Terdapat peningkatan yang signifikan dalam jumlah penyewaan sepeda secara keseluruhan dari tahun 2011 ke 2012, menandakan pertumbuhan adopsi layanan.
- **Pengaruh Cuaca:** Kondisi cuaca yang cerah atau berawan berkorelasi langsung dengan peningkatan jumlah penyewaan. Semakin buruk cuaca (hujan atau salju), semakin drastis penurunan penggunaan sepeda.
""")
st.subheader("Rekomendasi untuk Pertanyaan 1:")
st.markdown("""
- **Optimalisasi Sumber Daya Musiman:** Tingkatkan ketersediaan armada sepeda dan personil (untuk perawatan/distribusi) selama musim puncak (Musim Panas & Gugur) untuk memenuhi permintaan dan memaksimalkan potensi pendapatan. Kurangi sumber daya pada musim sepi untuk efisiensi.
- **Program Promosi Off-Season:** Kembangkan kampanye pemasaran atau diskon menarik selama musim dingin atau cuaca buruk untuk mendorong penggunaan di luar musim puncak, mungkin dengan menyoroti manfaat kesehatan atau alternatif transportasi.
- **Strategi Adaptif Cuaca:** Gunakan data prakiraan cuaca untuk mengoptimalkan penempatan sepeda dan strategi promosi harian. Misalnya, tawarkan diskon kecil pada hari-hari dengan cuaca sedikit kurang ideal untuk mempertahankan minat.
""")

st.subheader("Kesimpulan untuk Pertanyaan 2: Proporsi Pengguna Terdaftar dan Kasual")
st.markdown("""
- **Dominasi Pengguna Terdaftar:** Pengguna terdaftar secara konsisten menyumbang **mayoritas** dari total penyewaan, terutama pada **hari kerja**. Ini menunjukkan bahwa mereka menggunakan layanan ini sebagai bagian dari rutinitas harian (misalnya, komuter).
- **Pengguna Kasual untuk Rekreasi:** Pengguna kasual menunjukkan proporsi kontribusi yang lebih tinggi pada **akhir pekan**, yang mengindikasikan penggunaan untuk tujuan rekreasi atau wisata.
- **Sensitivitas Cuaca Kasual Lebih Tinggi:** Pengguna kasual cenderung lebih sensitif terhadap kondisi cuaca buruk; proporsi mereka menurun lebih drastis dibandingkan pengguna terdaftar saat cuaca tidak mendukung.
""")
st.subheader("Rekomendasi untuk Pertanyaan 2:")
st.markdown("""
- **Perkuat Loyalitas Pengguna Terdaftar:** Fokus pada program loyalitas (membership tier, reward points), paket langganan yang lebih fleksibel, dan peningkatan infrastruktur (stasiun/sepeda) untuk mempertahankan dan meningkatkan frekuensi pengguna terdaftar.
- **Tarik Pengguna Kasual di Akhir Pekan:** Targetkan pengguna kasual dengan promosi khusus akhir pekan, kemitraan dengan event lokal atau tempat wisata, dan penyediaan rute rekreasi yang direkomendasikan.
- **Konversi Pengguna Kasual:** Tawarkan insentif pendaftaran atau program trial untuk mengubah pengguna kasual menjadi anggota terdaftar setelah pengalaman positif, terutama pada hari-hari dengan cuaca cerah.
- **Diferensiasi Layanan Berdasarkan Cuaca:** Pertimbangkan untuk menyediakan sepeda dengan fitur lebih tangguh atau layanan pengiriman/penjemputan pada hari-hari dengan cuaca yang tidak ideal, atau promosikan jalur-jalur yang lebih terlindungi dari cuaca buruk.
""")

# --- FOOTER ---
st.markdown("---")
st.markdown("**Dashboard Analisis Penggunaan Sepeda** | Dikembangkan dengan dedikasi dan data yang akurat.")