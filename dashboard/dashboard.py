import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import date

# Load dataset
@st.cache_data
def load_data():
    # Pastikan path ini benar di komputermu.
    df = pd.read_csv("../main_data.csv")
    return df

df = load_data()

# Konversi kolom tanggal
df['dteday'] = pd.to_datetime(df['dteday'])
# Batasi data hanya sampai akhir 2012 sesuai dengan rentang data di gambar-gambar referensi
df = df[df['dteday'].dt.year < 2013]


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
    value=(start_date_min, start_date_max), # Nilai default sama dengan rentang data penuh 2011-2012
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

# --- 4 VISUALISASI YANG KAMU INGINKAN ---

# 1. Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim (SESUAI image_61cdb6.png dan image_605e32.png)
st.subheader("🗓️ Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")

df_agg_monthly_notebook = df_filtered.groupby(['year_month', 'season'])[['cnt']].sum().reset_index()

# Pastikan urutan bulan benar
df_agg_monthly_notebook['year_month_dt'] = pd.to_datetime(df_agg_monthly_notebook['year_month'])
df_agg_monthly_notebook = df_agg_monthly_notebook.sort_values('year_month_dt')

fig, ax = plt.subplots(figsize=(14, 6)) # Ukuran figure disesuaikan

# Menggunakan palette 'rocket' dan alpha untuk area shaded agar mirip gambar
sns.lineplot(data=df_agg_monthly_notebook, x='year_month', y='cnt', hue='season', marker='o', ax=ax,
             errorbar=('ci', 95), alpha=0.5, palette='rocket')

ax.set_title("Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")
ax.set_xlabel("year_month") # Sesuai gambar
ax.set_ylabel("Jumlah Penyewaan Sepeda")

# Mengatur x-tick untuk tampilan yang lebih rapi seperti gambar
xticks_labels = df_agg_monthly_notebook['year_month'].unique()
ax.set_xticks(xticks_labels[::2]) # Tampilkan setiap 2 bulan
ax.set_xticklabels(xticks_labels[::2], rotation=45, ha='right') # Rotate dan align right

ax.legend(title='season', loc='upper right') # Posisi legenda
ax.grid(False) # Sesuai gambar, tidak ada grid

# Batasi Y-axis agar terlihat lebih mirip
ax.set_ylim(bottom=-10000, top=165000) # Sesuaikan bottom agar ada sedikit ruang di bawah 0

plt.tight_layout() # Untuk layout yang rapi
st.pyplot(fig)


# 2. Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca (SESUAI image_600001.png, image_5fffe2.png, image_61bf31.png, image_61cd7b.png)
st.subheader("🌦️ Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
fig, ax = plt.subplots(figsize=(10, 6))
# Menggunakan warna biru default Seaborn/Matplotlib agar mirip gambar
sns.boxplot(data=df_filtered, x='weathersit', y='cnt', ax=ax, color='#1f77b4') # Warna 'tab:blue' atau '#1f77b4' sama

ax.set_title("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
ax.set_xlabel("Kondisi Cuaca (Weathersit)") # Sesuai gambar
ax.set_ylabel("Jumlah Penyewaan Sepeda Harian")
ax.grid(False) # Sesuai gambar, tidak ada grid
ax.set_ylim(bottom=-100, top=9000) # Sesuaikan jika data max berbeda
plt.tight_layout()
st.pyplot(fig)


# 3. Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari (SESUAI image_61cab4.png)
st.subheader("👥 Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari")
df_grouped_pct_prop = df_filtered.groupby(['weathersit', 'day_type'])[['casual', 'registered']].sum().reset_index()
df_grouped_pct_prop['total'] = df_grouped_pct_prop['casual'] + df_grouped_pct_prop['registered']
df_grouped_pct_prop['casual_pct'] = (df_grouped_pct_prop['casual'] / df_grouped_pct_prop['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
# Palette 'tab10' cocok untuk warna biru dan oranye di gambar
sns.barplot(data=df_grouped_pct_prop, x='weathersit', y='casual_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)') # Sesuai gambar
ax.set_ylabel('Proporsi Penyewaan Kasual (%)') # Sesuai gambar
ax.set_title('Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari')
ax.legend(title='Jenis Hari', loc='upper right') # Sesuai gambar
ax.tick_params(axis='x', rotation=0)
ax.grid(False) # Sesuai gambar, tidak ada grid
ax.set_ylim(bottom=0, top=26) # Sesuaikan jika data max berbeda
plt.tight_layout()
st.pyplot(fig)


# 4. Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari (SESUAI image_61ca90.png)
st.subheader("👥 Rata-rata Proporsi Pengguna Terdaftar per Kondisi Cuaca dan Jenis Hari")
df_grouped_pct_prop['registered_pct'] = (df_grouped_pct_prop['registered'] / df_grouped_pct_prop['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
# Palette 'tab10' cocok untuk warna biru dan oranye di gambar
sns.barplot(data=df_grouped_pct_prop, x='weathersit', y='registered_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)') # Sesuai gambar
ax.set_ylabel('Proporsi Penyewaan Terdaftar (%)') # Sesuai gambar
ax.set_title('Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari')
ax.legend(title='Jenis Hari', loc='upper left') # Sesuai gambar
ax.tick_params(axis='x', rotation=0)
ax.grid(False) # Sesuai gambar, tidak ada grid
ax.set_ylim(bottom=0, top=90) # Sesuaikan jika data max berbeda
plt.tight_layout()
st.pyplot(fig)


st.markdown("---")
st.markdown("🚲 **Bike Sharing Dashboard** | Dibuat dengan ❤️ oleh Data Analyst")