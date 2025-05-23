import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Pastikan df_day sudah dimuat atau dibuat di awal notebook
# Contoh (jika df_day belum ada, sesuaikan dengan sumber datamu)
# df_day = pd.read_csv('day.csv') # Misalnya jika datasetnya day.csv
# df_day['dteday'] = pd.to_datetime(df_day['dteday'])

# --- BAGIAN 1: PERSIAPAN DATA UNTUK PLOTTING ---
# df_seasonal, df_agg sudah ada di kodemu yang pertama
df_seasonal = df_day[['dteday', 'cnt', 'registered', 'casual', 'season', 'weathersit', 'hr']].copy()
df_seasonal['dteday'] = pd.to_datetime(df_seasonal['dteday'])
df_seasonal['year_month'] = df_seasonal['dteday'].dt.to_period('M').astype(str)

# Agregasi bulanan untuk total, registered, casual (untuk plot Tren Bulanan)
df_agg_monthly = df_seasonal.groupby(['year_month', 'season'])[['cnt', 'registered', 'casual']].sum().reset_index()


# Data untuk Rata-rata Penggunaan Sepeda Per Jam
df_hourly_avg = df_day.groupby('hr')[['cnt']].mean().reset_index()

# Data untuk Rata-rata Penggunaan Sepeda per Jam Berdasarkan Cuaca
df_hourly_weather_avg = df_day.groupby(['hr', 'weathersit'])[['cnt']].mean().reset_index()

# Data untuk Total Pengguna Berdasarkan Hari Kerja vs Libur
# Pastikan 'workingday' dan 'casual'/'registered' ada di df_day
df_workingday_holiday = df_day.groupby('workingday')[['casual', 'registered']].sum().reset_index()
df_workingday_holiday['day_type'] = df_workingday_holiday['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'})


# Data untuk Pengaruh Suhu terhadap Penggunaan Sepeda
# Misal, kategorikan suhu atau gunakan rata-rata per suhu
# df_temp_agg = df_day.groupby(pd.cut(df_day['temp'], bins=5, labels=False))['cnt'].mean().reset_index()
# Atau langsung grouping berdasarkan nilai temp jika tidak terlalu banyak diskrit
df_temp_agg = df_day.groupby('temp')['cnt'].mean().reset_index()


# Data untuk Proporsi Pengguna Kasual/Terdaftar (df_agg_pct) - seperti di kodemu yang kedua
# Asumsi df_agg_pct sudah dibuat di tempat lain, atau buat ulang jika perlu
# Contoh pembuatan df_agg_pct (sesuaikan kolom jika ada perbedaan)
# df_temp_for_prop = df_day.groupby(['weathersit', 'workingday'])[['casual', 'registered']].sum().reset_index()
# df_temp_for_prop['total'] = df_temp_for_prop['casual'] + df_temp_for_prop['registered']
# df_temp_for_prop['casual_pct'] = (df_temp_for_prop['casual'] / df_temp_for_prop['total']) * 100
# df_temp_for_prop['registered_pct'] = (df_temp_for_prop['registered'] / df_temp_for_prop['total']) * 100
# df_temp_for_prop['day_type'] = df_temp_for_prop['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'})
# df_agg_pct = df_temp_for_prop


# --- BAGIAN 2: PLOTTING VISUALISASI ---
# Urutan diusulkan berdasarkan alur pertanyaan bisnis:
# 1. Tren Umum
# 2. Pengaruh Waktu (Jam)
# 3. Pengaruh Cuaca
# 4. Pengaruh Hari Kerja/Libur & Suhu

# 1. Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim
plt.figure(figsize=(14, 6))
sns.lineplot(data=df_agg_monthly, x='year_month', y='cnt', hue='season', marker='o')
plt.title("Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")
plt.xlabel("Bulan - Tahun")
plt.ylabel("Jumlah Penyewaan Sepeda")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 2. Rata-rata Jumlah Pengguna Sepeda Per Jam (BARU)
plt.figure(figsize=(12, 6))
sns.lineplot(data=df_hourly_avg, x='hr', y='cnt', marker='o')
plt.title("Rata-rata Jumlah Pengguna Sepeda Per Jam")
plt.xlabel("Jam")
plt.ylabel("Rata-rata Pengguna")
plt.xticks(range(0, 24)) # Tampilkan semua jam
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 3. Rata-rata Penggunaan Sepeda per Jam Berdasarkan Cuaca (BARU)
plt.figure(figsize=(12, 6))
sns.lineplot(data=df_hourly_weather_avg, x='hr', y='cnt', hue='weathersit', marker='o')
plt.title("Rata-rata Penggunaan Sepeda per Jam Berdasarkan Cuaca")
plt.xlabel("Jam")
plt.ylabel("Rata-rata Pengguna")
plt.xticks(range(0, 24))
plt.legend(title='Kondisi Cuaca', loc='upper left', labels=['Cerah / Mendung', 'Kabut / Berawan', 'Salju Ringan / Hujan Ringan', 'Hujan Lebat / Badai']) # Sesuaikan label weathersit
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 4. Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_day, x='weathersit', y='cnt') # Menggunakan df_day untuk distribusi harian
plt.title("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
plt.xlabel("Kondisi Cuaca (Weathersit)")
plt.ylabel("Jumlah Penyewaan Sepeda Harian")
plt.xticks(ticks=[0, 1, 2, 3], labels=['Cerah/Mendung', 'Kabut/Berawan', 'Salju Ringan', 'Hujan Lebat/Badai']) # Sesuaikan label weathersit
plt.tight_layout()
plt.show()

# 5. Total Pengguna Berdasarkan Hari Kerja vs Libur (BARU - Stacked Bar Plot)
plt.figure(figsize=(8, 6))
# Untuk stacked bar plot, lebih mudah jika data di-pivot atau langsung plot dari df_workingday_holiday
df_workingday_holiday[['casual', 'registered']].plot(
    kind='bar', stacked=True, figsize=(8,6),
    color=['skyblue', 'salmon']
)
plt.title("Total Pengguna Berdasarkan Hari Kerja vs Libur")
plt.xlabel("Jenis Hari")
plt.ylabel("Total Pengguna")
plt.xticks(ticks=[0, 1], labels=['Hari Libur', 'Hari Kerja'], rotation=0)
plt.legend(title='Jenis Pengguna')
plt.tight_layout()
plt.show()

# 6. Pengaruh Suhu terhadap Penggunaan Sepeda (BARU)
plt.figure(figsize=(10, 6))
sns.barplot(data=df_temp_agg, x='temp', y='cnt', palette='viridis') # asumsi 'temp' adalah nilai numerik atau kategori
plt.title("Pengaruh Suhu terhadap Penggunaan Sepeda")
plt.xlabel("Suhu (Normalisasi)") # Jika suhu sudah dinormalisasi
plt.ylabel("Rata-rata Penggunaan Sepeda")
plt.tight_layout()
plt.show()


# 7. Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari
# Pastikan df_agg_pct sudah dibuat di awal notebook
plt.figure(figsize=(12, 6))
sns.barplot(data=df_agg_pct, x='weathersit', y='casual_pct', hue='day_type', palette='deep')
plt.title('Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari')
plt.xlabel('Kondisi Cuaca (weathersit)')
plt.ylabel('Proporsi Penyewaan Kasual (%)')
plt.legend(title='Jenis Hari')
plt.xticks(ticks=[0, 1, 2, 3], labels=['Cerah/Mendung', 'Kabut/Berawan', 'Salju Ringan', 'Hujan Lebat/Badai']) # Sesuaikan label weathersit
plt.tight_layout()
plt.show()

# 8. Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari
# Pastikan df_agg_pct sudah dibuat di awal notebook
plt.figure(figsize=(12, 6))
sns.barplot(data=df_agg_pct, x='weathersit', y='registered_pct', hue='day_type', palette='deep')
plt.title('Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari')
plt.xlabel('Kondisi Cuaca (weathersit)')
plt.ylabel('Proporsi Penyewaan Terdaftar (%)')
plt.legend(title='Jenis Hari')
plt.xticks(ticks=[0, 1, 2, 3], labels=['Cerah/Mendung', 'Kabut/Berawan', 'Salju Ringan', 'Hujan Lebat/Badai']) # Sesuaikan label weathersit
plt.tight_layout()
plt.show()