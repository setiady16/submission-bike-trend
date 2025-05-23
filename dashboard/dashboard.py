import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import date # Ini sudah ada, tapi perlu dipastikan

# Load dataset
@st.cache_data
def load_data():
    # Pastikan path ke main_data.csv benar.
    # Jika main_data.csv ada di folder "dashboard" di dalam folder proyek,
    # maka path ini sudah benar.
    df = pd.read_csv("dashboard/main_data.csv")
    return df

df = load_data()

# Konversi kolom tanggal
df['dteday'] = pd.to_datetime(df['dteday'])
# ### PENYESUAIAN/TAMBAHAN: Hindari data 2024 jika tidak lengkap
df = df[df['dteday'].dt.year < 2013] # Data bike sharing biasanya sampai akhir 2012. Sesuaikan jika datasetmu beda.

# --- DATA PREPROCESSING UNTUK DASHBOARD ---
# Lakukan semua preprocessing di sini agar konsisten dengan notebook

# Mapping untuk sidebar dan plot
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
df['season_label'] = df['season'].map(season_mapping)

weather_mapping = {1: "Cerah / Berawan", 2: "Berkabut / Mendung", 3: "Hujan Ringan / Salju Ringan", 4: "Hujan Lebat / Badai"}
df['weathersit_label'] = df['weathersit'].map(weather_mapping)

# Kolom 'year_month' untuk tren bulanan
df['year_month'] = df['dteday'].dt.to_period('M').astype(str)

# Kolom 'day_type' untuk proporsi kasual/terdaftar
df['day_type'] = df['workingday'].map({0: 'Akhir Pekan', 1: 'Hari Kerja'})


# Judul Dashboard
st.title("📊 Bike Sharing Dashboard")

# Sidebar Filter
st.sidebar.header("🔍 Filter Data")

start_date_min = df['dteday'].min().date()
start_date_max = df['dteday'].max().date()

selected_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(start_date_min, start_date_max),
    min_value=start_date_min,
    max_value=start_date_max,
)

selected_season = st.sidebar.multiselect("Pilih Musim", df['season_label'].unique(), default=df['season_label'].unique())
selected_weather = st.sidebar.multiselect("Pilih Kondisi Cuaca", df['weathersit_label'].unique(), default=df['weathersit_label'].unique())

# Terapkan Filter
start_date_filter = pd.to_datetime(selected_date[0])
end_date_filter = pd.to_datetime(selected_date[-1])

df_filtered = df[
    (df['dteday'] >= start_date_filter) &
    (df['dteday'] <= end_date_filter) &
    (df['season_label'].isin(selected_season)) &
    (df['weathersit_label'].isin(selected_weather))
].copy() # Tambahkan .copy() untuk menghindari SettingWithCopyWarning

# Total Pengguna (Pastikan ini dihitung setelah filter)
st.metric("🚴 Total Pengguna Setelah Filter:", f"{df_filtered['cnt'].sum():,}".replace(",", "."))

# --- VISUALISASI ---
# Mengikuti urutan yang disepakati di notebook:
# 1. Tren Umum
# 2. Pengaruh Waktu (Jam)
# 3. Pengaruh Cuaca
# 4. Pengaruh Hari Kerja/Libur & Suhu & Kelembaban

# 1. Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim (BARU/PENYESUAIAN)
st.subheader("🗓️ Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")
# Agregasi bulanan untuk total, registered, casual (untuk plot Tren Bulanan)
df_agg_monthly = df_filtered.groupby(['year_month', 'season_label'])[['cnt', 'registered', 'casual']].sum().reset_index()

fig, ax = plt.subplots(figsize=(14, 6))
sns.lineplot(data=df_agg_monthly, x='year_month', y='cnt', hue='season_label', marker='o', ax=ax)
ax.set_title("Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")
ax.set_xlabel("Bulan - Tahun")
ax.set_ylabel("Jumlah Penyewaan Sepeda")
ax.set_xticks(ax.get_xticks()[::2]) # Mengurangi jumlah label x-axis agar tidak terlalu ramai
ax.tick_params(axis='x', rotation=45)
ax.legend(title='Musim') # Menggunakan season_label untuk legenda
ax.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig)


# 2. Rata-rata Jumlah Pengguna Per Jam
st.subheader("📈 Rata-rata Jumlah Pengguna Per Jam")
hourly_trend = df_filtered.groupby('hr')['cnt'].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(x='hr', y='cnt', data=hourly_trend, marker='o', color='dodgerblue', ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Pengguna")
ax.set_title("Rata-rata Pengguna Sepeda Setiap Jam")
ax.set_xticks(range(0, 24, 2)) # Tampilkan semua jam, loncat 2 agar tidak terlalu ramai
ax.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig)

# 3. Rata-rata Penggunaan Sepeda per Jam berdasarkan Cuaca
st.subheader("🌤️ Rata-rata Penggunaan Sepeda per Jam berdasarkan Cuaca")
hourly_weather = df_filtered.groupby(['hr', 'weathersit_label'])['cnt'].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=hourly_weather, x="hr", y="cnt", hue="weathersit_label", marker='o', ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Pengguna")
ax.set_title("Tren Penggunaan Sepeda per Jam & Cuaca")
ax.legend(title="Kondisi Cuaca") # Menggunakan weathersit_label untuk legenda
ax.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig)

# 4. Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca (PENYESUAIAN Judul & Label)
st.subheader("🌦️ Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df_filtered, x='weathersit_label', y='cnt', ax=ax) # Menggunakan weathersit_label
ax.set_title("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
ax.set_xlabel("Kondisi Cuaca") # Label sudah menggunakan weathersit_label
ax.set_ylabel("Jumlah Penyewaan Sepeda Harian")
# ax.set_xticks(ticks=[0, 1, 2, 3], labels=['Cerah/Mendung', 'Kabut/Berawan', 'Salju Ringan', 'Hujan Lebat/Badai']) # Tidak perlu jika sudah pakai weathersit_label
ax.grid(True, linestyle='--', alpha=0.6, axis='y')
st.pyplot(fig)


# 5. Pengguna Casual vs Registered (Hari Kerja vs Libur) - Stacked Bar Plot
st.subheader("👥 Total Pengguna Berdasarkan Hari Kerja vs Libur")
grouped_data_day_type = df_filtered.groupby('day_type')[['casual', 'registered']].sum().reset_index()

fig, ax = plt.subplots(figsize=(8, 6))
# Untuk stacked bar plot, lebih mudah jika data di-pivot atau langsung plot dari df_workingday_holiday
grouped_data_day_type.set_index('day_type')[['casual', 'registered']].plot(
    kind='bar', stacked=True, color=['skyblue', 'salmon'], ax=ax
)
ax.set_title("Total Pengguna Berdasarkan Hari Kerja vs Libur")
ax.set_xlabel("Jenis Hari")
ax.set_ylabel("Total Pengguna")
ax.tick_params(axis='x', rotation=0) # Pastikan label tidak miring
ax.legend(title='Jenis Pengguna')
ax.grid(True, linestyle='--', alpha=0.6, axis='y')
st.pyplot(fig)


# 6. Pengaruh Suhu
# Pastikan bins dan labels sesuai dengan yang kamu inginkan dan konsisten dengan notebook
temp_bins = [0, 8.2, 16.4, 24.6, 32.8, 41]
temp_labels = ['Sangat Dingin (0-8°C)', 'Dingin (8-16°C)', 'Normal (16-24°C)', 'Hangat (24-32°C)', 'Panas (32-41°C)']
df_filtered['temp_group'] = pd.cut(df_filtered['temp'] * 41, bins=temp_bins, labels=temp_labels, right=False) # right=False agar batas atas tidak inklusif

st.subheader("🌡️ Pengaruh Suhu terhadap Penggunaan Sepeda")
fig, ax = plt.subplots(figsize=(10, 5))
# estimator=sum karena ingin melihat jumlah total, bukan rata-rata
sns.barplot(x='temp_group', y='cnt', data=df_filtered, estimator=sum, palette='YlOrRd', ax=ax, order=temp_labels) # Tambahkan order
ax.set_xlabel("Kelompok Suhu")
ax.set_ylabel("Jumlah Pengguna")
ax.set_title("Pengaruh Suhu terhadap Jumlah Pengguna")
ax.tick_params(axis='x', rotation=30) # Rotasi label agar tidak tumpang tindih
ax.grid(True, linestyle='--', alpha=0.6, axis='y')
st.pyplot(fig)

# 7. Pengaruh Kelembaban (Sudah ada di kodemu, pastikan konsisten)
hum_bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
hum_labels = ['Sangat Kering', 'Kering', 'Normal', 'Lembab', 'Sangat Lembab']
df_filtered['hum_group'] = pd.cut(df_filtered['hum'], bins=hum_bins, labels=hum_labels, right=False) # right=False

st.subheader("💧 Pengaruh Kelembaban terhadap Penggunaan Sepeda")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='hum_group', y='cnt', data=df_filtered, estimator=sum, palette='BuGn', ax=ax, order=hum_labels) # Tambahkan order
ax.set_xlabel("Kelompok Kelembaban")
ax.set_ylabel("Jumlah Pengguna")
ax.set_title("Pengaruh Kelembaban terhadap Jumlah Pengguna")
ax.tick_params(axis='x', rotation=30)
ax.grid(True, linestyle='--', alpha=0.6, axis='y')
st.pyplot(fig)


# 8. Proporsi Casual per Kondisi Cuaca dan Jenis Hari
st.subheader("👥 Proporsi Pengguna Kasual per Kondisi Cuaca dan Jenis Hari")
# df_grouped_pct dihitung ulang agar selalu berdasarkan df_filtered
df_grouped_pct = df_filtered.groupby(['weathersit_label', 'day_type'])[['casual', 'registered']].sum().reset_index()
df_grouped_pct['total'] = df_grouped_pct['casual'] + df_grouped_pct['registered']
df_grouped_pct['casual_pct'] = (df_grouped_pct['casual'] / df_grouped_pct['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_grouped_pct, x='weathersit_label', y='casual_pct', hue='day_type', palette='Blues', ax=ax)
ax.set_xlabel('Kondisi Cuaca') # Menggunakan weathersit_label
ax.set_ylabel('Proporsi Penyewaan Kasual (%)')
ax.set_title('Rata-rata Proporsi Penyewaan Kasual')
ax.legend(title='Jenis Hari')
ax.tick_params(axis='x', rotation=15) # Rotasi sedikit agar tidak tumpang tindih
ax.grid(True, linestyle='--', alpha=0.6, axis='y')
st.pyplot(fig)


# 9. Proporsi Registered per Kondisi Cuaca dan Jenis Hari
st.subheader("👥 Proporsi Pengguna Terdaftar per Kondisi Cuaca dan Jenis Hari")
# df_grouped_pct sudah dihitung di atas, tambahkan saja kolom registered_pct
df_grouped_pct['registered_pct'] = (df_grouped_pct['registered'] / df_grouped_pct['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_grouped_pct, x='weathersit_label', y='registered_pct', hue='day_type', palette='Oranges', ax=ax)
ax.set_xlabel('Kondisi Cuaca') # Menggunakan weathersit_label
ax.set_ylabel('Proporsi Penyewaan Terdaftar (%)')
ax.set_title('Rata-rata Proporsi Penyewaan Terdaftar')
ax.legend(title='Jenis Hari')
ax.tick_params(axis='x', rotation=15)
ax.grid(True, linestyle='--', alpha=0.6, axis='y')
st.pyplot(fig)

st.markdown("---")
st.markdown("🚲 **Bike Sharing Dashboard** | Dibuat dengan ❤️ oleh Data Analyst")