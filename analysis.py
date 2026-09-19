"""
Global COVID-19 Health Analytics - Python Analysis
Author: Kennedy Onyango
Purpose: Load data from MySQL, generate charts for Tableau dashboard
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Connect to MySQL
engine = create_engine("mysql+pymysql://analyst:analyst123@localhost/health_data")

# Set chart style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("Connected. Loading data...")

# ---- Chart 1: Kenya Vaccination Rollout ----
kenya_vax = pd.read_sql("""
    SELECT date, people_vaccinated, people_fully_vaccinated, population
    FROM covid_data
    WHERE location = 'Kenya' AND people_vaccinated IS NOT NULL
    ORDER BY date
""", engine)

kenya_vax['pct_one_dose'] = 100 * kenya_vax['people_vaccinated'] / kenya_vax['population']
kenya_vax['pct_full'] = 100 * kenya_vax['people_fully_vaccinated'] / kenya_vax['population']

plt.figure()
plt.plot(kenya_vax['date'], kenya_vax['pct_one_dose'], label='At least 1 dose', color='#1f77b4')
plt.plot(kenya_vax['date'], kenya_vax['pct_full'], label='Fully vaccinated', color='#2ca02c')
plt.title("Kenya COVID-19 Vaccination Rollout")
plt.xlabel("Date")
plt.ylabel("% of Population")
plt.legend()
plt.tight_layout()
plt.savefig("chart1_kenya_vaccination.png", dpi=150)
print("Saved chart1_kenya_vaccination.png")

# ---- Chart 2: Vaccination Coverage vs GDP ----
vax_gdp = pd.read_sql("""
    SELECT location,
           MAX(people_fully_vaccinated) AS fully_vaxed,
           MAX(population) AS pop,
           MAX(gdp_per_capita) AS gdp
    FROM covid_data
    WHERE continent IS NOT NULL
    GROUP BY location
    HAVING fully_vaxed IS NOT NULL AND gdp IS NOT NULL
""", engine)

vax_gdp['pct_fully'] = 100 * vax_gdp['fully_vaxed'] / vax_gdp['pop']
# Remove impossible values (>100% due to non-resident vaccination)
vax_gdp = vax_gdp[(vax_gdp['pct_fully'] >= 0) & (vax_gdp['pct_fully'] <= 100)]

plt.figure()
sns.scatterplot(data=vax_gdp, x='gdp', y='pct_fully', alpha=0.6, s=50)
plt.xscale('log')
plt.title("Vaccination Coverage vs GDP per Capita (by Country)")
plt.xlabel("GDP per Capita (log scale, USD)")
plt.ylabel("% Fully Vaccinated")
plt.tight_layout()
plt.savefig("chart2_vax_vs_gdp.png", dpi=150)
print("Saved chart2_vax_vs_gdp.png")

# ---- Chart 3: Cases per 100k by Continent ----
continents = pd.read_sql("""
    SELECT continent,
           ROUND(100000.0 * SUM(new_cases) / MAX(population), 0) AS cases_per_100k,
           ROUND(100000.0 * SUM(new_deaths) / MAX(population), 0) AS deaths_per_100k
    FROM covid_data
    WHERE continent IS NOT NULL
    GROUP BY continent
    ORDER BY cases_per_100k DESC
""", engine)

fig, ax = plt.subplots(1, 2, figsize=(14, 6))
sns.barplot(data=continents, y='continent', x='cases_per_100k', ax=ax[0], palette='Reds_r')
ax[0].set_title("Cases per 100,000 by Continent")
ax[0].set_xlabel("Cases per 100k")
ax[0].set_ylabel("")

sns.barplot(data=continents, y='continent', x='deaths_per_100k', ax=ax[1], palette='Blues_r')
ax[1].set_title("Deaths per 100,000 by Continent")
ax[1].set_xlabel("Deaths per 100k")
ax[1].set_ylabel("")

plt.tight_layout()
plt.savefig("chart3_continent_rates.png", dpi=150)
print("Saved chart3_continent_rates.png")

# ---- Chart 4: Monthly Cases - Kenya vs UK vs South Africa vs Germany ----
monthly = pd.read_sql("""
    WITH monthly AS (
      SELECT location,
             DATE_FORMAT(date, '%%Y-%%m') AS month,
             SUM(new_cases) AS monthly_cases
      FROM covid_data
      WHERE location IN ('Kenya', 'United Kingdom', 'South Africa', 'Germany')
      GROUP BY location, DATE_FORMAT(date, '%%Y-%%m')
    )
    SELECT month,
           SUM(CASE WHEN location = 'Kenya' THEN monthly_cases END) AS kenya,
           SUM(CASE WHEN location = 'United Kingdom' THEN monthly_cases END) AS uk,
           SUM(CASE WHEN location = 'South Africa' THEN monthly_cases END) AS south_africa,
           SUM(CASE WHEN location = 'Germany' THEN monthly_cases END) AS germany
    FROM monthly
    GROUP BY month
    ORDER BY month
""", engine)

monthly['month'] = pd.to_datetime(monthly['month'])

plt.figure(figsize=(14, 6))
plt.plot(monthly['month'], monthly['kenya'], label='Kenya', linewidth=2)
plt.plot(monthly['month'], monthly['uk'], label='United Kingdom', linewidth=2)
plt.plot(monthly['month'], monthly['south_africa'], label='South Africa', linewidth=2)
plt.plot(monthly['month'], monthly['germany'], label='Germany', linewidth=2)
plt.yscale('log')
plt.title("Monthly COVID-19 Cases: Kenya vs UK vs South Africa vs Germany (log scale)")
plt.xlabel("Month")
plt.ylabel("New Cases (log scale)")
plt.legend()
plt.tight_layout()
plt.savefig("chart4_monthly_comparison.png", dpi=150)
print("Saved chart4_monthly_comparison.png")

print("Done!")
