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

# Konversi kolom tanggal
df['dteday'] = pd.to_datetime(df['dteday'])
df = df[df['dteday'].dt.year < 2024]  # Hindari data 2024

# Judul
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

season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
df['season_label'] = df['season'].map(season_mapping)
selected_season = st.sidebar.multiselect("Pilih Musim", df['season_label'].unique(), default=df['season_label'].unique())

weather_mapping = {1: "Cerah / Berawan", 2: "Berkabut / Mendung", 3: "Hujan Ringan / Salju Ringan", 4: "Hujan Lebat / Badai"}
df['weathersit_label'] = df['weathersit'].map(weather_mapping)
selected_weather = st.sidebar.multiselect("Pilih Kondisi Cuaca", df['weathersit_label'].unique(), default=df['weathersit_label'].unique())

# Terapkan Filter
start_date_filter = pd.to_datetime(selected_date[0])
end_date_filter = pd.to_datetime(selected_date[-1])

df_filtered = df[
    (df['dteday'] >= start_date_filter) &
    (df['dteday'] <= end_date_filter) &
    (df['season_label'].isin(selected_season)) &
    (df['weathersit_label'].isin(selected_weather))
]

# Total Pengguna
st.metric("🚴 Total Pengguna Setelah Filter:", f"{df_filtered['cnt'].sum():,}".replace(",", "."))

# Visualisasi 1: Tren per jam
hourly_trend = df_filtered.groupby('hr')['cnt'].mean().reset_index()
st.subheader("📈 Rata-rata Jumlah Pengguna Per Jam")
fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(x='hr', y='cnt', data=hourly_trend, marker='o', color='dodgerblue', ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Pengguna")
ax.set_title("Rata-rata Pengguna Sepeda Setiap Jam")
ax.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig)

# Visualisasi 2: Tren per jam berdasarkan cuaca
hourly_weather = df_filtered.groupby(['hr', 'weathersit_label'])['cnt'].mean().reset_index()
st.subheader("🌤️ Rata-rata Penggunaan Sepeda per Jam berdasarkan Cuaca")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=hourly_weather, x="hr", y="cnt", hue="weathersit_label", marker='o', ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata Pengguna")
ax.set_title("Tren Penggunaan Sepeda per Jam & Cuaca")
ax.legend(title="Cuaca")
ax.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig)

# Visualisasi 3: Casual vs Registered
grouped_data = df_filtered.groupby('workingday')[['casual', 'registered']].sum().reset_index()
st.subheader("👥 Pengguna Casual vs Registered (Hari Kerja vs Libur)")
fig, ax = plt.subplots(figsize=(8, 6))
x = np.arange(len(grouped_data))
width = 0.5
ax.bar(x, grouped_data['casual'], width, label='Casual', color='skyblue')
ax.bar(x, grouped_data['registered'], width, bottom=grouped_data['casual'], label='Registered', color='salmon')
ax.set_xticks(x)
ax.set_xticklabels(grouped_data['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'}))
ax.set_ylabel("Total Pengguna")
ax.set_title("Total Pengguna Berdasarkan Hari Kerja vs Libur")
ax.legend()
st.pyplot(fig)

# Visualisasi 4: Pengaruh Suhu
temp_bins = [0, 8.2, 16.4, 24.6, 32.8, 41]
temp_labels = ['Sangat Dingin (0-8°C)', 'Dingin (8-16°C)', 'Normal (16-24°C)', 'Hangat (24-32°C)', 'Panas (32-41°C)']
df_filtered['temp_group'] = pd.cut(df_filtered['temp'] * 41, bins=temp_bins, labels=temp_labels)

st.subheader("🌡️ Pengaruh Suhu terhadap Penggunaan Sepeda")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='temp_group', y='cnt', data=df_filtered, estimator=sum, palette='YlOrRd', ax=ax)
ax.set_xlabel("Kelompok Suhu")
ax.set_ylabel("Jumlah Pengguna")
ax.set_title("Pengaruh Suhu terhadap Jumlah Pengguna")
st.pyplot(fig)

# Visualisasi 5: Pengaruh Kelembaban
hum_bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
hum_labels = ['Sangat Kering', 'Kering', 'Normal', 'Lembab', 'Sangat Lembab']
df_filtered['hum_group'] = pd.cut(df_filtered['hum'], bins=hum_bins, labels=hum_labels)

st.subheader("💧 Pengaruh Kelembaban terhadap Penggunaan Sepeda")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='hum_group', y='cnt', data=df_filtered, estimator=sum, palette='BuGn', ax=ax)
ax.set_xlabel("Kelompok Kelembaban")
ax.set_ylabel("Jumlah Pengguna")
ax.set_title("Pengaruh Kelembaban terhadap Jumlah Pengguna")
st.pyplot(fig)

# Visualisasi 6: Proporsi Casual
st.subheader("📊 Proporsi Pengguna Kasual per Kondisi Cuaca dan Jenis Hari")
df_filtered['day_type'] = df_filtered['workingday'].map({0: 'Akhir Pekan', 1: 'Hari Kerja'})
df_grouped_pct = df_filtered.groupby(['weathersit', 'day_type'])[['casual', 'registered']].sum().reset_index()
df_grouped_pct['total'] = df_grouped_pct['casual'] + df_grouped_pct['registered']
df_grouped_pct['casual_pct'] = (df_grouped_pct['casual'] / df_grouped_pct['total']) * 100
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_grouped_pct, x='weathersit', y='casual_pct', hue='day_type', palette='Blues', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)')
ax.set_ylabel('Proporsi Penyewaan Kasual (%)')
ax.set_title('Rata-rata Proporsi Penyewaan Kasual')
ax.legend(title='Jenis Hari')
st.pyplot(fig)

# Visualisasi 7: Proporsi Registered
st.subheader("📊 Proporsi Pengguna Terdaftar per Kondisi Cuaca dan Jenis Hari")
df_grouped_pct['registered_pct'] = (df_grouped_pct['registered'] / df_grouped_pct['total']) * 100
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_grouped_pct, x='weathersit', y='registered_pct', hue='day_type', palette='Oranges', ax=ax)
ax.set_xlabel('Kondisi Cuaca (weathersit)')
ax.set_ylabel('Proporsi Penyewaan Terdaftar (%)')
ax.set_title('Rata-rata Proporsi Penyewaan Terdaftar')
ax.legend(title='Jenis Hari')
st.pyplot(fig)

st.markdown("---")
st.markdown("🚲 **Bike Sharing Dashboard** | Dibuat dengan ❤️ oleh Data Analyst")
