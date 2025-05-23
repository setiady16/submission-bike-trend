import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import date

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("C:/Users/ADVAN/OneDrive/submission/submission/dashboard/main_data.csv")
    return df

df = load_data()

# Konversi kolom tanggal
df['dteday'] = pd.to_datetime(df['dteday'])
df = df[df['dteday'].dt.year < 2013] # Batasi data jika tidak lengkap di 2013/2014


# --- DATA PREPROCESSING UNTUK DASHBOARD ---
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
df['season_label'] = df['season'].map(season_mapping)

weather_mapping = {1: "Cerah / Berawan", 2: "Berkabut / Mendung", 3: "Hujan Ringan / Salju Ringan", 4: "Hujan Lebat / Badai"}
df['weathersit_label'] = df['weathersit'].map(weather_mapping)

df['year_month'] = df['dteday'].dt.to_period('M').astype(str)
df['day_type'] = df['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'})


st.title("📊 Bike Sharing Dashboard")

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

start_date_filter = pd.to_datetime(selected_date[0])
end_date_filter = pd.to_datetime(selected_date[-1])

df_filtered = df[
    (df['dteday'] >= start_date_filter) &
    (df['dteday'] <= end_date_filter) &
    (df['season_label'].isin(selected_season)) &
    (df['weathersit_label'].isin(selected_weather))
].copy()


st.metric("🚴 Total Pengguna Setelah Filter:", f"{df_filtered['cnt'].sum():,}".replace(",", "."))

# --- VISUALISASI YANG DIMINTA AGAR MIRIP KODE NOTEBOOK ---
# 1. Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim (SESUAI image_61cdb6.png dan kode notebook)
st.subheader("🗓️ Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")

# Agregasi bulanan untuk total, registered, casual (sesuaikan dengan kode notebook)
# Kode notebookmu melakukan groupby berdasarkan ['year_month', 'season', 'weathersit']
# Namun, visualisasi yang ingin kamu tiru (image_61cdb6.png) hanya menggunakan 'year_month' dan 'season'.
# Jadi kita akan mengikuti agregasi yang sesuai dengan visualisasi yang diinginkan.
df_agg_monthly_notebook = df_filtered.groupby(['year_month', 'season'])[['cnt']].sum().reset_index()

# Pastikan urutan bulan benar
df_agg_monthly_notebook['year_month_dt'] = pd.to_datetime(df_agg_monthly_notebook['year_month'])
df_agg_monthly_notebook = df_agg_monthly_notebook.sort_values('year_month_dt')

fig, ax = plt.subplots(figsize=(14, 6)) # Ukuran figure disesuaikan

# Menggunakan parameter yang mirip dengan kode notebook
# Hue='season' (angka) dan marker='o' sudah sama.
# errorbar=('ci', 95) untuk area shaded.
sns.lineplot(data=df_agg_monthly_notebook, x='year_month', y='cnt', hue='season', marker='o', ax=ax,
             errorbar=('ci', 95)) # Hapus palette kustom untuk menggunakan default Seaborn

ax.set_title("Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")
ax.set_xlabel("year_month") # Sesuai gambar
ax.set_ylabel("Jumlah Penyewaan Sepeda")

# Mengatur x-tick untuk tampilan yang lebih rapi seperti gambar
xticks = df_agg_monthly_notebook['year_month'].unique()
ax.set_xticks(xticks[::2]) # Tampilkan setiap 2 bulan
ax.tick_params(axis='x', rotation=45)

ax.legend(title='season', loc='upper right') # Posisi legenda
ax.grid(False) # Sesuai gambar, tidak ada grid

# Batasi Y-axis agar terlihat lebih mirip (tetap dipertahankan dari versi sebelumnya)
ax.set_ylim(bottom=0, top=160000)

plt.tight_layout() # Tambahkan ini untuk meniru tight_layout() dari notebook

st.pyplot(fig)

# 2. Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca
st.subheader("🌦️ Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df_filtered, x='weathersit', y='cnt', ax=ax, color='tab:blue')
ax.set_title("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
ax.set_xlabel("Kondisi Cuaca (Weathersit)")
ax.set_ylabel("Jumlah Penyewaan Sepeda Harian")
ax.grid(False)
ax.set_ylim(bottom=0, top=9000)
st.pyplot(fig)

# 3. Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari
st.subheader("👥 Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari")
df_grouped_pct_prop = df_filtered.groupby(['weathersit', 'day_type'])[['casual', 'registered']].sum().reset_index()
df_grouped_pct_prop['total'] = df_grouped_pct_prop['casual'] + df_grouped_pct_prop['registered']
df_grouped_pct_prop['casual_pct'] = (df_grouped_pct_prop['casual'] / df_grouped_pct_prop['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_grouped_pct_prop, x='weathersit', y='casual_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)')
ax.set_ylabel('Proporsi Penyewaan Kasual (%)')
ax.set_title('Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari')
ax.legend(title='Jenis Hari', loc='upper right')
ax.tick_params(axis='x', rotation=0)
ax.grid(False)
ax.set_ylim(bottom=0, top=25)
st.pyplot(fig)

# 4. Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari
st.subheader("👥 Rata-rata Proporsi Pengguna Terdaftar per Kondisi Cuaca dan Jenis Hari")
df_grouped_pct_prop['registered_pct'] = (df_grouped_pct_prop['registered'] / df_grouped_pct_prop['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_grouped_pct_prop, x='weathersit', y='registered_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)')
ax.set_ylabel('Proporsi Penyewaan Terdaftar (%)')
ax.set_title('Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari')
ax.legend(title='Jenis Hari', loc='upper left')
ax.tick_params(axis='x', rotation=0)
ax.grid(False)
ax.set_ylim(bottom=0, top=90)
st.pyplot(fig)


st.markdown("---")
st.markdown("🚲 **Bike Sharing Dashboard** | Dibuat dengan ❤️ oleh Data Analyst")