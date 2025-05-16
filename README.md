# 🚴‍♀️ Bike Trend Dashboard ✨

Panduan menjalankan dashboard analisis tren penggunaan sepeda.

---

## ⚙️ Setup & Jalankan Aplikasi

Pastikan Anda berada di dalam folder `submission/`.

Gunakan salah satu metode berikut untuk menyiapkan environment, lalu jalankan aplikasi dengan Streamlit.

```bash
# === [ Opsi 1: Menggunakan Anaconda ] ===

conda create --name main-ds python= 3.13
conda activate main-ds
pip install -r requirements.txt

# === [ Opsi 2: Menggunakan Virtual Environment (venv) ] ===

python -m venv myenv

# Untuk Windows
myenv\Scripts\activate

# Untuk macOS / Linux
source myenv/bin/activate

# Install dependensi
pip install -r requirements.txt

# === [ Menjalankan Aplikasi Streamlit ] ===
streamlit run .\dashboard\dashboard.py

