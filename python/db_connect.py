import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Bağlantı Motoru
DB_USER = "postgres"
DB_PASSWORD = "fenerlipanda"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "airline_db"

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

# 2. Havayolları Gecikme Sorgusu
query = """
SELECT 
    a.airline,
    ROUND(AVG(f.departure_delay), 2) AS avg_delay_minutes
FROM flights f
INNER JOIN airlines a ON f.airline = a.iata_code
GROUP BY a.airline
ORDER BY avg_delay_minutes DESC;
"""

print("Veri çekiliyor...")
df = pd.read_sql(query, engine)

# 3. Görselleştirme Ayarları (Seaborn & Matplotlib)
plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")

# Yatay bar grafiği (en çok geciken en üstte)
barplot = sns.barplot(
    data=df,
    x="avg_delay_minutes",
    y="airline",
    palette="flare"
)

# Başlık ve eksen etiketleri
plt.title("ABD Havayolları Ortalama Kalkış Gecikmeleri (Dakika)", fontsize=14, fontweight="bold", pad=15)
plt.xlabel("Ortalama Gecikme (Dakika)", fontsize=12)
plt.ylabel("Havayolu Şirketi", fontsize=12)

# Çubukların ucuna değerleri yazdırma
for p in barplot.patches:
    width = p.get_width()
    barplot.annotate(
        f'{width:.1f} dk',
        (width, p.get_y() + p.get_height() / 2.),
        ha='left', va='center',
        xytext=(5, 0), textcoords='offset points',
        fontsize=10, fontweight="bold", color="#333333"
    )

plt.tight_layout()

# Grafiği resim olarak kaydet ve ekranda göster
plt.savefig("airline_delays.png", dpi=300)
print("Grafik 'airline_delays.png' olarak kaydedildi!")
plt.show()