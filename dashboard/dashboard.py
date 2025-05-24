import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import date

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    return df

df = load_data()
df['dteday'] = pd.to_datetime(df['dteday'])
df = df[df['dteday'].dt.year < 2013]

# --- LABELING ---
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
df['season_label'] = df['season'].map(season_mapping)

weather_mapping = {1: "Cerah / Berawan", 2: "Berkabut / Mendung", 3: "Hujan Ringan / Salju Ringan", 4: "Hujan Lebat / Badai"}
df['weathersit_label'] = df['weathersit'].map(weather_mapping)

df['year_month'] = df['dteday'].dt.to_period('M').astype(str)
df['day_type'] = df['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'})

# --- DASHBOARD TITLE ---
st.title("📊 Bike Sharing Dashboard")

# --- SIDEBAR FILTER ---
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

# --- DATA FILTERING (nonaktifkan dulu untuk tes) ---
# start_date_filter = pd.to_datetime(selected_date[0])
# end_date_filter = pd.to_datetime(selected_date[-1])
# df_filtered = df[
#     (df['dteday'] >= start_date_filter) &
#     (df['dteday'] <= end_date_filter) &
#     (df['season_label'].isin(selected_season)) &
#     (df['weathersit_label'].isin(selected_weather))
# ].copy()
df_filtered = df.copy()

st.metric("🚴 Total Pengguna Setelah Filter:", f"{df_filtered['cnt'].sum():,}".replace(",", "."))

# --- VISUALISASI 1 ---
st.subheader("🗓️ Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")

# Pakai 'season' (angka 1–4) seperti di notebook
df_agg_monthly = df_filtered.groupby(['year_month', 'season'], sort=False)[['cnt']].sum().reset_index()
df_agg_monthly['year_month_dt'] = pd.to_datetime(df_agg_monthly['year_month'])
df_agg_monthly = df_agg_monthly.sort_values('year_month_dt')

fig, ax = plt.subplots(figsize=(14, 6))
sns.lineplot(
    data=df_agg_monthly,
    x='year_month',
    y='cnt',
    hue='season',
    marker='o',
    ax=ax,
    errorbar=None  # hilangkan shading / CI
)

ax.set_title("Tren Penyewaan Sepeda Bulanan Total berdasarkan Musim")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Penyewaan Sepeda")
ax.legend(title='Musim', loc='upper right')
ax.tick_params(axis='x', rotation=45)
ax.grid(False)
plt.tight_layout()
st.pyplot(fig)


# --- VISUALISASI 2 ---
st.subheader("🌦️ Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df_filtered, x='weathersit', y='cnt', ax=ax, color='#1f77b4')
ax.set_title("Distribusi Penyewaan Sepeda Berdasarkan Kondisi Cuaca")
ax.set_xlabel("Kondisi Cuaca (Weathersit)")
ax.set_ylabel("Jumlah Penyewaan Sepeda Harian")
ax.grid(False)
plt.tight_layout()
st.pyplot(fig)

# --- VISUALISASI 3 ---
st.subheader("👥 Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari")

df_grouped = df_filtered.groupby(['weathersit', 'day_type'], sort=False)[['casual', 'registered']].sum().reset_index()
df_grouped['total'] = df_grouped['casual'] + df_grouped['registered']
df_grouped['casual_pct'] = (df_grouped['casual'] / df_grouped['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_grouped, x='weathersit', y='casual_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)')
ax.set_ylabel('Proporsi Penyewaan Kasual (%)')
ax.set_title('Rata-rata Proporsi Penyewaan Kasual per Kondisi Cuaca dan Jenis Hari')
ax.legend(title='Jenis Hari', loc='upper right')
ax.tick_params(axis='x', rotation=0)
ax.grid(False)
plt.tight_layout()
st.pyplot(fig)

# --- VISUALISASI 4 ---
st.subheader("👥 Rata-rata Proporsi Pengguna Terdaftar per Kondisi Cuaca dan Jenis Hari")

df_grouped['registered_pct'] = (df_grouped['registered'] / df_grouped['total']) * 100

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_grouped, x='weathersit', y='registered_pct', hue='day_type', palette='tab10', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)')
ax.set_ylabel('Proporsi Penyewaan Terdaftar (%)')
ax.set_title('Rata-rata Proporsi Penyewaan Terdaftar per Kondisi Cuaca dan Jenis Hari')
ax.legend(title='Jenis Hari', loc='upper left')
ax.tick_params(axis='x', rotation=0)
ax.grid(False)
plt.tight_layout()
st.pyplot(fig)

st.markdown("---")
st.markdown("🚲 **Bike Sharing Dashboard** | Dibuat dengan ❤️ oleh Data Analyst")
