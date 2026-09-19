import getpass
import pandas as pd
from sqlalchemy import create_engine

cols = [
    "iso_code", "continent", "location", "date",
    "total_cases", "new_cases", "total_deaths", "new_deaths",
    "reproduction_rate", "icu_patients", "hosp_patients",
    "total_tests", "positive_rate",
    "total_vaccinations", "people_vaccinated",
    "people_fully_vaccinated", "total_boosters",
    "stringency_index", "population_density", "median_age",
    "aged_65_older", "gdp_per_capita", "diabetes_prevalence",
    "hospital_beds_per_thousand", "life_expectancy",
    "human_development_index", "population", "excess_mortality"
]

print("Reading CSV...")
df = pd.read_csv("owid-covid-data.csv", usecols=cols, parse_dates=["date"])
print(f"  Loaded {len(df):,} rows")

df = df.dropna(subset=["location", "date"])
print(f"  After cleaning: {len(df):,} rows")

engine = create_engine("mysql+pymysql://analyst:analyst123@localhost/health_data")

print("Writing to MySQL (1-3 min)...")
df.to_sql("covid_data", engine, if_exists="replace",
          index=False, chunksize=10000)
print("Done! Data loaded.")

