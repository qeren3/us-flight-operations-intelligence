import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from db_connect import read_query

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
df = read_query(query)

plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")
barplot = sns.barplot(data=df, x="avg_delay_minutes", y="airline", palette="flare")
plt.title("ABD Havayolları Ortalama Kalkış Gecikmeleri (Dakika)", fontsize=14, fontweight="bold", pad=15)
plt.xlabel("Ortalama Gecikme (Dakika)", fontsize=12)
plt.ylabel("Havayolu Şirketi", fontsize=12)

for patch in barplot.patches:
    width = patch.get_width()
    barplot.annotate(
        f"{width:.1f} dk",
        (width, patch.get_y() + patch.get_height() / 2),
        ha="left", va="center", xytext=(5, 0), textcoords="offset points",
        fontsize=10, fontweight="bold", color="#333333"
    )

plt.tight_layout()
plt.savefig("airline_delays.png", dpi=300)
print("Grafik 'airline_delays.png' olarak kaydedildi!")
plt.show()
