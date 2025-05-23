import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import date

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
# ### PENTING: Batasi data hanya sampai akhir 2012 jika data 2013/2014 tidak lengkap
df = df[df['dteday'].dt.year < 2013]


# --- DATA PREPROCESSING UNTUK DASHBOARD ---
# Lakukan semua preprocessing di sini agar konsisten dengan notebook dan dashboard

# Mapping untuk sidebar dan plot
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
df['season_label'] = df['season'].map(season_mapping)

weather_mapping = {1: "Cerah / Berawan", 2: "Berkabut / Mendung", 3: "Hujan Ringan / Salju Ringan", 4: "Hujan Lebat / Badai"}
df['weathersit_label'] = df['weathersit'].map(weather_mapping)

# Kolom 'year_month' untuk tren bulanan
df['year_month'] = df['dteday'].dt.to_period('M').astype(str)

# Kolom 'day_type' untuk proporsi kasual/terdaftar dan stacked bar plot
df['day_type'] = df['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'})


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
# Mengikuti urutan dan tampilan persis seperti di gambar yang kamu unggah

# 1. Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim (SESUAI image_61cdb6.png)
st.subheader("🗓️ Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")
df_agg_monthly = df_filtered.groupby(['year_month', 'season'])[['cnt']].sum().reset_index()
# Pastikan urutan bulan benar
df_agg_monthly['year_month_dt'] = pd.to_datetime(df_agg_monthly['year_month'])
df_agg_monthly = df_agg_monthly.sort_values('year_month_dt')

fig, ax = plt.subplots(figsize=(14, 6)) # Ukuran figure disesuaikan
# Menggunakan hue='season' (angka) dan palette kustom untuk nuansa yang mirip
# Warna bisa diatur manual jika palette tidak pas
custom_palette_season = {
    1: '#F4CCCC', # Mirip pink muda
    2: '#D9EDC8', # Mirip hijau muda
    3: '#A3D9D9', # Mirip biru muda
    4: '#E0BBE4'  # Mirip ungu muda
}
# Seaborn default palette has limited colors, 'rocket' or 'magma' could be close.
# Let's try to match with custom colors for precise replication
sns.lineplot(data=df_agg_monthly, x='year_month', y='cnt', hue='season', marker='o', ax=ax,
             palette=custom_palette_season, errorbar=('ci', 95), alpha=0.8) # alpha untuk transparan area
ax.set_title("Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")
ax.set_xlabel("year_month") # Sesuai gambar
ax.set_ylabel("Jumlah Penyewaan Sepeda")
# Mengatur x-tick untuk tampilan yang lebih rapi seperti gambar
xticks = df_agg_monthly['year_month'].unique()
ax.set_xticks(xticks[::2]) # Tampilkan setiap 2 bulan
ax.tick_params(axis='x', rotation=45)
ax.legend(title='season', loc='upper right') # Posisi legenda
ax.grid(False) # Sesuai gambar, tidak ada grid
# Batasi Y-axis agar terlihat lebih mirip
ax.set_ylim(bottom=0, top=160000) # Sesuaikan jika data max berbeda
st.pyplot(fig)


# 2. Rata-rata Jumlah Pengguna Per Jam (SESUAI image_622fb1.jpg - atas kiri)
st.subheader("📈 Rata-rata Jumlah Pengguna Per Jam")
hourly_trend = df_filtered.groupby('hr')['cnt'].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 5)) # Ukuran figure disesuaikan
sns.lineplot(x='hr', y='cnt', data=hourly_trend, marker='o', color='dodgerblue', ax=ax) # Warna dodgerblue sudah mirip
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Pengguna")
ax.set_title("Rata-rata Pengguna Sepeda Setiap Jam")
ax.set_xticks(range(0, 24, 5)) # Loncat 5 jam agar mirip gambar (0, 5, 10, 15, 20)
ax.grid(False) # Sesuai gambar, tidak ada grid
# Batasi Y-axis agar terlihat lebih mirip
ax.set_ylim(bottom=0, top=400) # Sesuaikan jika data max berbeda
st.pyplot(fig)


# 3. Rata-rata Penggunaan Sepeda per Jam berdasarkan Cuaca (SESUAI image_61bf8b.png / image_622fb1.jpg - bawah kiri)
st.subheader("🌤️ Rata-rata Penggunaan Sepeda per Jam berdasarkan Cuaca")
# Pastikan menggunakan weathersit_label untuk legenda yang mudah dibaca
hourly_weather = df_filtered.groupby(['hr', 'weathersit_label'])['cnt'].mean().reset_index()

# Urutan legend dan warna agar mirip dengan gambar
weather_order = ["Berkabut / Mendung", "Cerah / Berawan", "Hujan Ringan / Salju Ringan", "Hujan Lebat / Badai"]
custom_palette_weather = {
    "Berkabut / Mendung": '#FF8C00',  # Orange
    "Cerah / Berawan": '#1f77b4',     # Biru standar matplotlib
    "Hujan Ringan / Salju Ringan": '#2ca02c', # Hijau standar matplotlib
    "Hujan Lebat / Badai": '#DC143C'  # Merah tua
}
fig, ax = plt.subplots(figsize=(12, 6)) # Ukuran figure disesuaikan
sns.lineplot(data=hourly_weather, x="hr", y="cnt", hue="weathersit_label", marker='o', ax=ax,
             hue_order=weather_order, palette=custom_palette_weather)
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Pengguna")
ax.set_title("Tren Penggunaan Sepeda per Jam & Cuaca")
# Menyesuaikan posisi legenda seperti di gambar
ax.legend(title="Cuaca", loc='upper left', frameon=True)
ax.set_xticks(range(0, 24, 5)) # Loncat 5 jam agar mirip gambar
ax.grid(False) # Sesuai gambar, tidak ada grid
# Batasi Y-axis agar terlihat lebih mirip
ax.set_ylim(bottom=0, top=550) # Sesuaikan jika data max berbeda
st.pyplot(fig)


# 4. Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca (SESUAI image_61bf31.png / image_622fb1.jpg - kanan bawah)
st.subheader("🌦️ Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
fig, ax = plt.subplots(figsize=(10, 6)) # Ukuran figure disesuaikan
# Menggunakan weathersit (angka) untuk sumbu X agar sama persis dengan gambar
sns.boxplot(data=df_filtered, x='weathersit', y='cnt', ax=ax, color='tab:blue') # Warna biru standar seaborn/matplotlib
ax.set_title("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
ax.set_xlabel("Kondisi Cuaca (Weathersit)") # Sesuai gambar
ax.set_ylabel("Jumlah Penyewaan Sepeda Harian")
# Label sumbu X akan otomatis 1, 2, 3 sesuai angka di kolom 'weathersit'
ax.grid(False) # Sesuai gambar, tidak ada grid
# Batasi Y-axis agar terlihat lebih mirip
ax.set_ylim(bottom=0, top=9000) # Sesuaikan jika data max berbeda
st.pyplot(fig)


# 5. Pengguna Casual vs Registered (Hari Kerja vs Libur) - Stacked Bar Plot (SESUAI image_622c4b.png - kiri tengah)
st.subheader("👥 Total Pengguna Berdasarkan Hari Kerja vs Libur")
# Gunakan df_filtered['workingday'] untuk sumbu X agar sama persis dengan gambar
grouped_data_day_type = df_filtered.groupby('workingday')[['casual', 'registered']].sum().reset_index()

fig, ax = plt.subplots(figsize=(8, 6)) # Ukuran figure disesuaikan
# Plotting manual untuk kontrol warna dan label yang lebih baik
bottom_casual = [0, 0] # Karena hanya 2 bar
bottom_registered = grouped_data_day_type['casual']

bars_casual = ax.bar(grouped_data_day_type['workingday'], grouped_data_day_type['casual'],
                     label='Casual', color='skyblue') # Warna biru muda
bars_registered = ax.bar(grouped_data_day_type['workingday'], grouped_data_day_type['registered'],
                       bottom=grouped_data_day_type['casual'], label='Registered', color='salmon') # Warna orange/merah muda

ax.set_title("Total Pengguna Berdasarkan Hari Kerja vs Libur")
ax.set_xlabel("") # Sesuai gambar, tidak ada label X
ax.set_ylabel("Total Pengguna") # Sesuai gambar
# Atur x-tick labels secara manual agar sesuai dengan gambar
ax.set_xticks([0, 1])
ax.set_xticklabels(['Hari Libur', 'Hari Kerja']) # Label sesuai gambar
ax.tick_params(axis='x', rotation=0) # Pastikan label tidak miring
ax.legend(title='Jenis Pengguna', loc='upper left') # Posisi legenda
ax.grid(False) # Sesuai gambar, tidak ada grid
# Batasi Y-axis agar terlihat lebih mirip
ax.set_ylim(bottom=0, top=2500000) # Sesuaikan jika data max berbeda
st.pyplot(fig)


# 6. Pengaruh Suhu terhadap Penggunaan Sepeda (SESUAI image_622c4b.png - kiri bawah)
st.subheader("🌡️ Pengaruh Suhu terhadap Penggunaan Sepeda")
# Bins dan labels suhu sesuai dengan kodemu
temp_bins = [0, 8.2, 16.4, 24.6, 32.8, 41]
temp_labels = ['0-8°C', '8-16°C', '16-24°C', '24-32°C', '32-41°C'] # Label yang lebih ringkas
df_filtered['temp_group'] = pd.cut(df_filtered['temp'] * 41, bins=temp_bins, labels=temp_labels, right=False)

fig, ax = plt.subplots(figsize=(10, 5)) # Ukuran figure disesuaikan
# estimator=sum karena ingin melihat jumlah total, bukan rata-rata
# Palette 'Oranges' mirip dengan gambar, gunakan `order` untuk memastikan urutan
sns.barplot(x='temp_group', y='cnt', data=df_filtered, estimator=sum, palette='Oranges', ax=ax, order=temp_labels)
ax.set_xlabel("") # Sesuai gambar, tidak ada label X
ax.set_ylabel("Pengguna") # Sesuai gambar
ax.set_title("Pengaruh Suhu terhadap Jumlah Pengguna")
ax.tick_params(axis='x', rotation=0) # Pastikan label tidak miring
ax.grid(False) # Sesuai gambar, tidak ada grid
# Batasi Y-axis agar terlihat lebih mirip
ax.set_ylim(bottom=0, top=1400000) # Sesuaikan jika data max berbeda
st.pyplot(fig)


# 7. Pengaruh Kelembaban terhadap Penggunaan Sepeda (Tidak ada gambar referensi, pertahankan)
st.subheader("💧 Pengaruh Kelembaban terhadap Penggunaan Sepeda")
hum_bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
hum_labels = ['Sangat Kering', 'Kering', 'Normal', 'Lembab', 'Sangat Lembab']
df_filtered['hum_group'] = pd.cut(df_filtered['hum'], bins=hum_bins, labels=hum_labels, right=False)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='hum_group', y='cnt', data=df_filtered, estimator=sum, palette='BuGn', ax=ax, order=hum_labels)
ax.set_xlabel("Kelompok Kelembaban")
ax.set_ylabel("Jumlah Pengguna")
ax.set_title("Pengaruh Kelembaban terhadap Jumlah Pengguna")
ax.tick_params(axis='x', rotation=30)
ax.grid(True, linestyle='--', alpha=0.6, axis='y') # Grid tetap ada karena tidak ada referensi gambar
st.pyplot(fig)


# 8. Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari (SESUAI image_622c4b.png - kanan atas)
st.subheader("👥 Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari")
# df_grouped_pct_prop dihitung ulang agar selalu berdasarkan df_filtered
# Gunakan 'weathersit' (angka) dan 'day_type' (Hari Libur/Hari Kerja)
df_grouped_pct_prop = df_filtered.groupby(['weathersit', 'day_type'])[['casual', 'registered']].sum().reset_index()
df_grouped_pct_prop['total'] = df_grouped_pct_prop['casual'] + df_grouped_pct_prop['registered']
df_grouped_pct_prop['casual_pct'] = (df_grouped_pct_prop['casual'] / df_grouped_pct_prop['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6)) # Ukuran figure disesuaikan
# Palette 'tab10' atau 'deep' bisa mirip. Coba 'tab10' untuk warna biru dan oranye yang pas.
sns.barplot(data=df_grouped_pct_prop, x='weathersit', y='casual_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)') # Sesuai gambar
ax.set_ylabel('Proporsi Penyewaan Kasual (%)') # Sesuai gambar
ax.set_title('Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari') # Sesuai gambar
ax.legend(title='Jenis Hari', loc='upper right') # Sesuai gambar
ax.tick_params(axis='x', rotation=0) # Tidak ada rotasi di gambar
ax.grid(False) # Sesuai gambar, tidak ada grid
# Batasi Y-axis agar terlihat lebih mirip
ax.set_ylim(bottom=0, top=25) # Sesuaikan jika data max berbeda
st.pyplot(fig)


# 9. Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari (SESUAI image_622c4b.png - kanan bawah)
st.subheader("👥 Rata-rata Proporsi Pengguna Terdaftar per Kondisi Cuaca dan Jenis Hari")
# df_grouped_pct_prop sudah dihitung di atas, tambahkan saja kolom registered_pct
df_grouped_pct_prop['registered_pct'] = (df_grouped_pct_prop['registered'] / df_grouped_pct_prop['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6)) # Ukuran figure disesuaikan
sns.barplot(data=df_grouped_pct_prop, x='weathersit', y='registered_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)') # Sesuai gambar
ax.set_ylabel('Proporsi Penyewaan Terdaftar (%)') # Sesuai gambar
ax.set_title('Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari') # Sesuai gambar
ax.legend(title='Jenis Hari', loc='upper left') # Sesuai gambar
ax.tick_params(axis='x', rotation=0) # Tidak ada rotasi di gambar
ax.grid(False) # Sesuai gambar, tidak ada grid
# Batasi Y-axis agar terlihat lebih mirip
ax.set_ylim(bottom=0, top=90) # Sesuaikan jika data max berbeda
st.pyplot(fig)


st.markdown("---")
st.markdown("🚲 **Bike Sharing Dashboard** | Dibuat dengan ❤️ oleh Data Analyst")