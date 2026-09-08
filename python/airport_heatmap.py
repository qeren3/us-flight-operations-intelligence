import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Veritabanı Bağlantısı
DB_USER = "postgres"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "airline_db"

connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

# 2. En Yoğun 10 Havalimanı (Doğrudan kod filtreleme)
top_airports = ('ATL', 'ORD', 'DFW', 'DEN', 'LAX', 'SFO', 'PHX', 'IAH', 'LAS', 'MSP')

query = f"""
SELECT 
    origin_airport,
    month,
    ROUND(AVG(departure_delay), 1) AS avg_delay
FROM flights
WHERE origin_airport IN {top_airports}
  AND departure_delay IS NOT NULL
GROUP BY origin_airport, month
ORDER BY origin_airport, month;
"""

print("Veri çekiliyor...")
df = pd.read_sql(query, engine)

# Havalimanlarına şehir etiketleri ekleyelim
airport_labels = {
    'ATL': 'ATL (Atlanta)',
    'ORD': 'ORD (Chicago)',
    'DFW': 'DFW (Dallas)',
    'DEN': 'DEN (Denver)',
    'LAX': 'LAX (Los Angeles)',
    'SFO': 'SFO (San Francisco)',
    'PHX': 'PHX (Phoenix)',
    'IAH': 'IAH (Houston)',
    'LAS': 'LAS (Las Vegas)',
    'MSP': 'MSP (Minneapolis)'
}
df['airport_label'] = df['origin_airport'].map(airport_labels)

# 3. Pivot Tablo
heatmap_data = df.pivot(index='airport_label', columns='month', values='avg_delay')

print("Çekilen aylar:", heatmap_data.columns.tolist())

# Ay isimleri eşleştirmesi
month_dict = {
    1: 'Oca', 2: 'Şub', 3: 'Mar', 4: 'Nis', 5: 'May', 6: 'Haz',
    7: 'Tem', 8: 'Ağu', 9: 'Eyl', 10: 'Eki', 11: 'Kas', 12: 'Ara'
}
heatmap_data.columns = [month_dict.get(m, m) for m in heatmap_data.columns]

# 4. Çizim
plt.figure(figsize=(13, 7))
sns.set_theme(style="white")

sns.heatmap(
    heatmap_data, 
    cmap="YlOrRd", 
    annot=True, 
    fmt=".1f", 
    linewidths=.5, 
    cbar_kws={'label': 'Ortalama Kalkış Gecikmesi (Dakika)'}
)

plt.title("En Yoğun 10 ABD Havalimanında Aylık Gecikme Isı Haritası", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Aylar", fontsize=12)
plt.ylabel("Havalimanı", fontsize=12)
plt.tight_layout()

plt.savefig("airport_monthly_heatmap.png", dpi=300)
print("Isı haritası 'airport_monthly_heatmap.png' olarak güncellendi!")
plt.show()