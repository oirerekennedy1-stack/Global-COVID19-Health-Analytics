"""Export key analysis tables as CSVs for Tableau Public."""
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://analyst:analyst123@localhost/health_data")

print("Exporting CSVs for Tableau...")

# 1. Country-level vaccination vs GDP
pd.read_sql("""
    SELECT location, continent,
           MAX(people_fully_vaccinated) AS fully_vaxed,
           MAX(population) AS population,
           ROUND(100.0 * MAX(people_fully_vaccinated) / NULLIF(MAX(population),0), 2) AS pct_fully_vaccinated,
           ROUND(MAX(gdp_per_capita), 0) AS gdp_per_capita,
           MAX(total_cases) AS total_cases,
           MAX(total_deaths) AS total_deaths
    FROM covid_data
    WHERE continent IS NOT NULL
    GROUP BY location, continent
""", engine).to_csv("tableau_vaccination.csv", index=False)

# 2. Monthly cases for 4 countries
pd.read_sql("""
    SELECT location,
           DATE_FORMAT(date, '%%Y-%%m') AS month,
           SUM(new_cases) AS monthly_cases,
           SUM(new_deaths) AS monthly_deaths
    FROM covid_data
    WHERE location IN ('Kenya', 'United Kingdom', 'South Africa', 'Germany')
    GROUP BY location, DATE_FORMAT(date, '%%Y-%%m')
    ORDER BY month
""", engine).to_csv("tableau_monthly.csv", index=False)

# 3. Continent summary
pd.read_sql("""
    SELECT continent,
           ROUND(100000.0 * SUM(new_cases) / MAX(population), 0) AS cases_per_100k,
           ROUND(100000.0 * SUM(new_deaths) / MAX(population), 0) AS deaths_per_100k,
           ROUND(100.0 * SUM(new_deaths) / NULLIF(SUM(new_cases),0), 2) AS cfr_pct
    FROM covid_data
    WHERE continent IS NOT NULL
    GROUP BY continent
""", engine).to_csv("tableau_continents.csv", index=False)

# 4. Kenya vaccination timeline
pd.read_sql("""
    SELECT date, people_vaccinated, people_fully_vaccinated, population
    FROM covid_data
    WHERE location = 'Kenya' AND people_vaccinated IS NOT NULL
    ORDER BY date
""", engine).to_csv("tableau_kenya_vax.csv", index=False)

print("Done! 4 CSVs created.")
