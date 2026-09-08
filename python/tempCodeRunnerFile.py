import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Bağlantı Motoru
DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "airline_db"

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

# 2. Saatlik Gecikme Sorgusu
query = """
SELECT 
    scheduled_departure / 100 AS departure_hour,
    ROUND(AVG(departure_delay), 2) AS avg_delay_minutes
FROM flights
WHERE scheduled_departure IS NOT NULL
GROUP BY departure_hour
ORDER BY departure_hour ASC;
"""

print("Saatlik veri çekiliyor...")
df = pd.read_sql(query, engine)

# 0-23 saat aralığı dışındaki olası hatalı uç değerleri filtreleyelim
df = df[(df['departure_hour'] >= 0) & (df['departure_hour'] <= 23)]

# 3. Çizgi Grafiği Çizimi
plt.figure(figsize=(12, 6))
plt.ylim(0, 18)
sns.set_theme(style="whitegrid")

# Çizgi ve noktalar
plt.plot(
    df['departure_hour'], 
    df['avg_delay_minutes'], 
    marker='o', 
    color='#d90429', 
    linewidth=2.5, 
    markersize=6, 
    label='Ortalama Gecikme (dk)'
)

# Eğrinin altını doldurarak derinlik hissi verme
plt.fill_between(df['departure_hour'], df['avg_delay_minutes'], color='#d90429', alpha=0.15)

# Zirve noktayı (Saat 20:00) vurgulama
peak_hour = df.loc[df['avg_delay_minutes'].idxmax()]
plt.scatter(peak_hour['departure_hour'], peak_hour['avg_delay_minutes'], color='#7d0217', s=120, zorder=5)
plt.annotate(
    f"Zirve: {peak_hour['avg_delay_minutes']} dk\n(Saat {int(peak_hour['departure_hour'])}:00)",
    xy=(peak_hour['departure_hour'], peak_hour['avg_delay_minutes']),
    xytext=(peak_hour['departure_hour'] - 3.5, peak_hour['avg_delay_minutes'] + 0.8),
    arrowprops=dict(facecolor='#7d0217', shrink=0.08, width=1.5, headwidth=8),
    fontweight='bold',
    fontsize=10
)

# Eksenler ve başlık
plt.title("Günün Saatlerine Göre Ortalama Uçuş Gecikmeleri (Trend Analizi)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Planlanan Kalkış Saati (00:00 - 23:00)", fontsize=12)
plt.ylabel("Ortalama Gecikme (Dakika)", fontsize=12)
plt.xticks(range(0, 24))
plt.tight_layout()

# Kaydet ve Göster
plt.savefig("hourly_delay_trend.png", dpi=300)
print("Grafik 'hourly_delay_trend.png' olarak kaydedildi!")
plt.show()