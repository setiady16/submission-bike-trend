import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# --- LOAD DATA ---
day_df = pd.read_csv("day_fix.csv")
hour_df = pd.read_csv("hour_fix.csv")

# Tambah kolom 'data_type' untuk info tapi kita tidak pakai filter berdasarkan tipe dataset
day_df['data_type'] = 'Harian'
hour_df['data_type'] = 'Per Jam'

# Gabungkan kedua dataset
df = pd.concat([day_df, hour_df], ignore_index=True)

# --- PREPROCESS ---
df['dteday'] = pd.to_datetime(df['dteday'])

# Mapping season dan weather
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
weather_mapping = {
    1: "Cerah/Berawan",
    2: "Berkabut",
    3: "Hujan Ringan",
    4: "Hujan Lebat"
}

df['season_label'] = df['season'].map(season_mapping)
df['weathersit_label'] = df['weathersit'].map(weather_mapping)

# Kalau ada kolom 'hr' buat kolom datetime lengkap, kalau enggak pake 'dteday' saja
if 'hr' in df.columns:
    df['hr'] = df['hr'].fillna(0).astype(int)
    df['datetime'] = df['dteday'] + pd.to_timedelta(df['hr'], unit='h')
else:
    df['datetime'] = df['dteday']

# --- FILTER DATA ---
st.sidebar.header("🔍 Filter Data")

start_date_min = df['dteday'].min().date()
start_date_max = df['dteday'].max().date()

selected_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(start_date_min, start_date_max),
    min_value=start_date_min,
    max_value=start_date_max,
)

selected_season = st.sidebar.multiselect(
    "Pilih Musim",
    df['season_label'].dropna().unique(),
    default=df['season_label'].dropna().unique()
)

selected_weather = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca",
    df['weathersit_label'].dropna().unique(),
    default=df['weathersit_label'].dropna().unique()
)

start_date_filter = pd.to_datetime(selected_date[0])
end_date_filter = pd.to_datetime(selected_date[1])

df_filtered = df[
    (df['dteday'] >= start_date_filter) &
    (df['dteday'] <= end_date_filter) &
    (df['season_label'].isin(selected_season)) &
    (df['weathersit_label'].isin(selected_weather))
].copy()

# Jika ada kolom workingday, buat label hari kerja/libur
if 'workingday' in df_filtered.columns:
    df_filtered['day_type'] = df_filtered['workingday'].map({0: 'Akhir Pekan', 1: 'Hari Kerja'})

# --- DASHBOARD ---
st.title("📊 Bike Sharing Dashboard")
st.metric("🚴 Total Pengguna Setelah Filter:", f"{df_filtered['cnt'].sum():,}".replace(",", "."))

# --- VISUALISASI 1: Tren Penyewaan Bulanan ---
st.subheader("🗓️ Tren Penyewaan Sepeda Bulanan berdasarkan Musim")

df_filtered['year_month'] = df_filtered['dteday'].dt.to_period('M').astype(str)
df_agg_monthly = df_filtered.groupby(['year_month', 'season_label'], sort=False)['cnt'].sum().reset_index()
df_agg_monthly['year_month_dt'] = pd.to_datetime(df_agg_monthly['year_month'])
df_agg_monthly = df_agg_monthly.sort_values('year_month_dt')

fig, ax = plt.subplots(figsize=(14, 6))
sns.lineplot(
    data=df_agg_monthly,
    x='year_month',
    y='cnt',
    hue='season_label',
    marker='o',
    ax=ax,
    errorbar=None
)
ax.set_title("Tren Penyewaan Sepeda Bulanan berdasarkan Musim")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Penyewaan Sepeda")
ax.legend(title='Musim', loc='upper right')
ax.tick_params(axis='x', rotation=45)
ax.grid(False)
plt.tight_layout()
st.pyplot(fig)

# --- VISUALISASI 2: Distribusi Penyewaan Berdasarkan Cuaca ---
st.subheader("🌦️ Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df_filtered, x='weathersit_label', y='cnt', ax=ax2, color='#1f77b4')
ax2.set_title("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
ax2.set_xlabel("Kondisi Cuaca")
ax2.set_ylabel("Jumlah Penyewaan Sepeda")
ax2.grid(False)
plt.tight_layout()
st.pyplot(fig2)

# --- PROPORSI PENYEWAAN KASUAL & TERDAFTAR (Jika ada kolom) ---
if 'casual' in df_filtered.columns and 'registered' in df_filtered.columns and 'workingday' in df_filtered.columns:
    df_grouped = df_filtered.groupby(['weathersit_label', 'day_type']).agg({
        'casual': 'sum',
        'registered': 'sum',
        'cnt': 'sum'
    }).reset_index()

    # Hitung persentase penyewaan kasual dan terdaftar
    df_grouped['casual_pct'] = (df_grouped['casual'] / df_grouped['cnt']) * 100
    df_grouped['registered_pct'] = (df_grouped['registered'] / df_grouped['cnt']) * 100

    # Urutan label cuaca supaya konsisten
    order = ['Cerah/Berawan', 'Berkabut', 'Hujan Ringan', 'Hujan Lebat']

    st.subheader("👥 Proporsi Penyewaan Kasual dan Terdaftar per Kondisi Cuaca dan Jenis Hari")

    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_grouped, x='weathersit_label', y='casual_pct', hue='day_type', order=order, ax=ax3)
    ax3.set_title('Proporsi Penyewaan Kasual (%) per Kondisi Cuaca dan Jenis Hari')
    ax3.set_xlabel('Kondisi Cuaca')
    ax3.set_ylabel('Persentase Penyewaan Kasual (%)')
    ax3.legend(title='Jenis Hari')
    st.pyplot(fig3)

    fig4, ax4 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_grouped, x='weathersit_label', y='registered_pct', hue='day_type', order=order, ax=ax4)
    ax4.set_title('Proporsi Penyewaan Terdaftar (%) per Kondisi Cuaca dan Jenis Hari')
    ax4.set_xlabel('Kondisi Cuaca')
    ax4.set_ylabel('Persentase Penyewaan Terdaftar (%)')
    ax4.legend(title='Jenis Hari')
    st.pyplot(fig4)

st.markdown("---")
st.markdown("🚲 **Bike Sharing Dashboard** | Dibuat dengan ❤️ oleh Data Analyst")
