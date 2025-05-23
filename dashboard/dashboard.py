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
# ### PENTING: Jika data 2024 tidak lengkap atau tidak relevan, batasi.
# Asumsi data hanya sampai akhir 2012, jika datasetmu berbeda, sesuaikan tahunnya.
df = df[df['dteday'].dt.year < 2013]


# --- DATA PREPROCESSING UNTUK DASHBOARD ---
# Lakukan semua preprocessing di sini agar konsisten dengan notebook dan dashboard

# Mapping untuk sidebar dan plot
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
df['season_label'] = df['season'].map(season_mapping) # Akan digunakan untuk legenda di plot Tren Bulanan

weather_mapping = {1: "Cerah / Berawan", 2: "Berkabut / Mendung", 3: "Hujan Ringan / Salju Ringan", 4: "Hujan Lebat / Badai"}
df['weathersit_label'] = df['weathersit'].map(weather_mapping)

# Kolom 'year_month' untuk tren bulanan
df['year_month'] = df['dteday'].dt.to_period('M').astype(str)

# Kolom 'day_type' untuk proporsi kasual/terdaftar dan stacked bar plot
df['day_type'] = df['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'}) # Menggunakan Hari Libur/Hari Kerja sesuai gambar


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
df_agg_monthly = df_filtered.groupby(['year_month', 'season'])[['cnt']].sum().reset_index() # Groupby season (angka) untuk legenda angka
# Pastikan urutan bulan benar
df_agg_monthly['year_month_dt'] = pd.to_datetime(df_agg_monthly['year_month'])
df_agg_monthly = df_agg_monthly.sort_values('year_month_dt')

fig, ax = plt.subplots(figsize=(14, 6))
# Menggunakan hue='season' (angka) dan palette 'rocket' untuk nuansa yang mirip dengan gambar
sns.lineplot(data=df_agg_monthly, x='year_month', y='cnt', hue='season', marker='o', ax=ax, palette='rocket', errorbar=('ci', 95)) # errorbar untuk area shaded
ax.set_title("Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")
ax.set_xlabel("year_month") # Sesuai gambar
ax.set_ylabel("Jumlah Penyewaan Sepeda")
# Mengatur x-tick untuk tampilan yang lebih rapi seperti gambar
# Ambil setiap 2 bulan untuk label, dan pastikan rotasi 45
xticks = df_agg_monthly['year_month'].unique()
ax.set_xticks(xticks[::2])
ax.tick_params(axis='x', rotation=45)
ax.legend(title='season')
ax.grid(False) # Sesuai gambar, tidak ada grid
st.pyplot(fig)


# 2. Rata-rata Jumlah Pengguna Per Jam (SESUAI image_622fb1.jpg - atas kiri)
st.subheader("📈 Rata-rata Jumlah Pengguna Per Jam")
hourly_trend = df_filtered.groupby('hr')['cnt'].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(x='hr', y='cnt', data=hourly_trend, marker='o', color='dodgerblue', ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Pengguna")
ax.set_title("Rata-rata Pengguna Sepeda Setiap Jam")
ax.set_xticks(range(0, 24, 5)) # Loncat 5 jam agar mirip gambar
ax.grid(False) # Sesuai gambar, tidak ada grid
st.pyplot(fig)


# 3. Rata-rata Penggunaan Sepeda per Jam berdasarkan Cuaca (SESUAI image_622fb1.jpg - bawah kiri)
st.subheader("🌤️ Rata-rata Penggunaan Sepeda per Jam berdasarkan Cuaca")
# Pastikan menggunakan weathersit_label untuk legenda yang mudah dibaca
hourly_weather = df_filtered.groupby(['hr', 'weathersit_label'])['cnt'].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=hourly_weather, x="hr", y="cnt", hue="weathersit_label", marker='o', ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Pengguna")
ax.set_title("Tren Penggunaan Sepeda per Jam & Cuaca")
# Menyesuaikan posisi legenda seperti di gambar
ax.legend(title="Cuaca", loc='upper left', frameon=True)
ax.grid(False) # Sesuai gambar, tidak ada grid
st.pyplot(fig)


# 4. Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca (SESUAI image_61cd7b.png dan image_622fb1.jpg - bawah kanan)
st.subheader("🌦️ Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
fig, ax = plt.subplots(figsize=(10, 6))
# Menggunakan weathersit (angka) untuk sumbu X agar sama persis dengan gambar
sns.boxplot(data=df_filtered, x='weathersit', y='cnt', ax=ax)
ax.set_title("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
ax.set_xlabel("Kondisi Cuaca (Weathersit)") # Sesuai gambar
ax.set_ylabel("Jumlah Penyewaan Sepeda Harian")
# Label sumbu X akan otomatis 1, 2, 3 sesuai angka di kolom 'weathersit'
ax.grid(False) # Sesuai gambar, tidak ada grid
st.pyplot(fig)


# 5. Total Pengguna Berdasarkan Hari Kerja vs Libur (SESUAI image_622c4b.png - kiri tengah)
st.subheader("👥 Total Pengguna Berdasarkan Hari Kerja vs Libur")
# Gunakan df_filtered['workingday'] untuk sumbu X agar sama persis dengan gambar
grouped_data_day_type = df_filtered.groupby('workingday')[['casual', 'registered']].sum().reset_index()

fig, ax = plt.subplots(figsize=(8, 6))
grouped_data_day_type.set_index('workingday')[['casual', 'registered']].plot(
    kind='bar', stacked=True, color=['skyblue', 'salmon'], ax=ax
)
ax.set_title("Total Pengguna Berdasarkan Hari Kerja vs Libur")
ax.set_xlabel("") # Sesuai gambar, tidak ada label X
ax.set_ylabel("Total Pengguna")
# Atur x-tick labels secara manual agar sesuai dengan gambar
ax.set_xticks([0, 1])
ax.set_xticklabels(['Hari Libur', 'Hari Kerja']) # Label sesuai gambar
ax.tick_params(axis='x', rotation=0) # Pastikan label tidak miring
ax.legend(title='Jenis Pengguna', loc='upper right') # Sesuai gambar
ax.grid(False) # Sesuai gambar, tidak ada grid
st.pyplot(fig)


# 6. Pengaruh Suhu terhadap Penggunaan Sepeda (SESUAI image_622c4b.png - kiri bawah)
st.subheader("🌡️ Pengaruh Suhu terhadap Penggunaan Sepeda")
# Bins dan labels suhu sesuai dengan kodemu
temp_bins = [0, 8.2, 16.4, 24.6, 32.8, 41]
temp_labels = ['0-8°C', '8-16°C', '16-24°C', '24-32°C', '32-41°C'] # Label yang lebih ringkas seperti di gambar
df_filtered['temp_group'] = pd.cut(df_filtered['temp'] * 41, bins=temp_bins, labels=temp_labels, right=False)

fig, ax = plt.subplots(figsize=(10, 5))
# estimator=sum karena ingin melihat jumlah total, bukan rata-rata
# Palette 'Oranges' mirip dengan gambar, gunakan `order` untuk memastikan urutan
sns.barplot(x='temp_group', y='cnt', data=df_filtered, estimator=sum, palette='Oranges', ax=ax, order=temp_labels)
ax.set_xlabel("") # Sesuai gambar, tidak ada label X
ax.set_ylabel("Pengguna") # Sesuai gambar
ax.set_title("Pengaruh Suhu terhadap Jumlah Pengguna")
ax.tick_params(axis='x', rotation=0) # Pastikan label tidak miring
ax.grid(False) # Sesuai gambar, tidak ada grid
st.pyplot(fig)


# 7. Pengaruh Kelembaban terhadap Penggunaan Sepeda (Ini belum ada gambar referensinya, pakai kode lama)
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


# 8. Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari (SESUAI image_61cab4.png dan image_622c4b.png - kanan atas)
st.subheader("👥 Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari")
# df_grouped_pct dihitung ulang agar selalu berdasarkan df_filtered
# Gunakan 'weathersit' (angka) dan 'day_type' (Hari Libur/Hari Kerja)
df_grouped_pct_prop = df_filtered.groupby(['weathersit', 'day_type'])[['casual', 'registered']].sum().reset_index()
df_grouped_pct_prop['total'] = df_grouped_pct_prop['casual'] + df_grouped_pct_prop['registered']
df_grouped_pct_prop['casual_pct'] = (df_grouped_pct_prop['casual'] / df_grouped_pct_prop['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
# Palette 'tab10' atau 'deep' bisa mirip, 'Blues' untuk satu hue
sns.barplot(data=df_grouped_pct_prop, x='weathersit', y='casual_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)') # Sesuai gambar
ax.set_ylabel('Proporsi Penyewaan Kasual (%)') # Sesuai gambar
ax.set_title('Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari') # Sesuai gambar
ax.legend(title='Jenis Hari', loc='upper right') # Sesuai gambar
ax.tick_params(axis='x', rotation=0) # Tidak ada rotasi di gambar
ax.grid(False) # Sesuai gambar, tidak ada grid
st.pyplot(fig)


# 9. Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari (SESUAI image_61ca90.png dan image_622c4b.png - kanan bawah)
st.subheader("👥 Rata-rata Proporsi Pengguna Terdaftar per Kondisi Cuaca dan Jenis Hari")
# df_grouped_pct_prop sudah dihitung di atas, tambahkan saja kolom registered_pct
df_grouped_pct_prop['registered_pct'] = (df_grouped_pct_prop['registered'] / df_grouped_pct_prop['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_grouped_pct_prop, x='weathersit', y='registered_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)') # Sesuai gambar
ax.set_ylabel('Proporsi Penyewaan Terdaftar (%)') # Sesuai gambar
ax.set_title('Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari') # Sesuai gambar
ax.legend(title='Jenis Hari', loc='upper left') # Sesuai gambar
ax.tick_params(axis='x', rotation=0) # Tidak ada rotasi di gambar
ax.grid(False) # Sesuai gambar, tidak ada grid
st.pyplot(fig)


st.markdown("---")
st.markdown("🚲 **Bike Sharing Dashboard** | Dibuat dengan ❤️ oleh Data Analyst")