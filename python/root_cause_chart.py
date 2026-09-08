import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# 1. Veritabanı Bağlantısı
DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "airline_db"

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

# 2. Kök Neden Sorgusu
query = """
SELECT 
    ROUND(SUM(late_aircraft_delay) / 60.0, 0) AS "Zincirleme (Geç Gelen Uçak)",
    ROUND(SUM(airline_delay) / 60.0, 0) AS "Havayolu Operasyonu",
    ROUND(SUM(air_system_delay) / 60.0, 0) AS "Hava Trafik Sistemi (NAS)",
    ROUND(SUM(weather_delay) / 60.0, 0) AS "Hava Muhalefeti",
    ROUND(SUM(security_delay) / 60.0, 0) AS "Güvenlik"
FROM flights
WHERE departure_delay > 0;
"""

print("Kök neden verisi çekiliyor...")
df = pd.read_sql(query, engine)

# Tabloyu grafik için uygun formata getiriyoruz (Tek satırdan İsim-Değer ikilisine)
categories = list(df.columns)
values = df.iloc[0].values

# Renk paleti (Modern ve dengeli)
colors = ['#e76f51', '#f4a261', '#e9c46a', '#2a9d8f', '#264653']

# 3. Halka Grafik (Donut Chart) Çizimi
plt.figure(figsize=(9, 9))
wedges, texts, autotexts = plt.pie(
    values, 
    labels=categories, 
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    pctdistance=0.75,
    textprops={'fontsize': 11}
)

# Ortadaki beyaz yuvarlağı ekleyip halka görünümü veriyoruz
centre_circle = plt.Circle((0, 0), 0.55, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

# Yüzde yazılarının stilini güzelleştirme
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_weight('bold')
    autotext.set_fontsize(11)

plt.title("ABD Uçuş Gecikmelerinin Kök Neden Dağılımı (Saat Bazlı)", fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()

# Kaydet ve Göster
plt.savefig("root_cause_distribution.png", dpi=300)
print("Grafik 'root_cause_distribution.png' olarak kaydedildi!")
plt.show()