-- =====================================================
-- Project: Global COVID-19 Health Analytics
-- Author: Kennedy Onyango
-- Purpose: Analytical queries for SQL, Python, and Tableau
-- =====================================================

-- Query 1: Global Snapshot
-- Question: What's the overall scale of the pandemic?
SELECT
  MAX(date) AS latest_date,
  COUNT(DISTINCT location) AS countries_tracked,
  ROUND(SUM(new_cases), 0) AS total_cases,
  ROUND(SUM(new_deaths), 0) AS total_deaths,
  ROUND(100.0 * SUM(new_deaths) / NULLIF(SUM(new_cases), 0), 2) AS global_cfr_pct
FROM health_data.covid_data
WHERE continent IS NOT NULL;



-- Query 2: Kenya's Pandemic Timeline
-- Question: How did Kenya's cases and deaths evolve over time?
SELECT
  date, new_cases, new_deaths, total_cases, total_deaths
FROM health_data.covid_data
WHERE location = 'Kenya'
  AND new_cases IS NOT NULL
ORDER BY date DESC
LIMIT 30;



-- Query 3: Peak Infection Days by Country
-- Question: When did each country hit its highest single-day case count?
-- Note: China's 40M peak is a data artifact from a Dec 2022 reporting revision
SELECT
  location,
  MAX(new_cases) AS peak_daily_cases,
  MAX(total_cases) AS all_time_total
FROM health_data.covid_data
WHERE continent IS NOT NULL
GROUP BY location
ORDER BY peak_daily_cases DESC
LIMIT 15;


#Excluding China's reporting artifact, the United States recorded the highest genuine single-day COVID-19 peak at 5.65 million cases (January 2022, Omicron wave), followed by India at 2.74 million.
SELECT
  location,
  MAX(new_cases) AS peak_daily_cases
FROM health_data.covid_data
WHERE continent IS NOT NULL
  AND location <> 'China'
GROUP BY location
ORDER BY peak_daily_cases DESC
LIMIT 10;



-- Query 4: Vaccination Coverage vs GDP (Vaccine Equity Analysis)
-- Question: Do wealthier countries have higher vaccination rates?
-- Finding: Strong correlation — wealthiest nations at 70-100%+, poorest under 30%
-- Note: Qatar/UAE >100% due to counting non-residents in numerator
SELECT
  location,
  MAX(people_fully_vaccinated) AS fully_vaccinated,
  MAX(population) AS population,
  ROUND(100.0 * MAX(people_fully_vaccinated) / NULLIF(MAX(population), 0), 1) AS pct_fully_vaccinated,
  ROUND(MAX(gdp_per_capita), 0) AS gdp_per_capita
FROM health_data.covid_data
WHERE continent IS NOT NULL
GROUP BY location
HAVING fully_vaccinated IS NOT NULL
   AND gdp_per_capita IS NOT NULL
ORDER BY pct_fully_vaccinated DESC;



-- Query 5: Kenya's Vaccination Rollout Summary
-- Question: How did Kenya's vaccination campaign progress?
-- Finding: Slow start (Mar-Jul 2021), acceleration (Aug-Dec 2021), plateau at ~20% by 2023
SELECT
  MIN(date) AS first_vax_date,
  MAX(date) AS last_vax_date,
  MAX(people_vaccinated) AS peak_first_dose,
  MAX(people_fully_vaccinated) AS peak_fully_vaxed,
  ROUND(100.0 * MAX(people_vaccinated) / MAX(population), 2) AS pct_one_dose,
  ROUND(100.0 * MAX(people_fully_vaccinated) / MAX(population), 2) AS pct_full
FROM health_data.covid_data
WHERE location = 'Kenya';


-- Query 6: Continent Comparison (Per Capita)
-- Question: Which continents were hit hardest per capita?
-- Finding: Europe 29x higher case rate than Africa; CFR paradox in Africa
SELECT
  continent,
  ROUND(SUM(new_cases), 0) AS total_cases,
  ROUND(SUM(new_deaths), 0) AS total_deaths,
  ROUND(100000.0 * SUM(new_cases) / MAX(population), 0) AS cases_per_100k,
  ROUND(100000.0 * SUM(new_deaths) / MAX(population), 0) AS deaths_per_100k,
  ROUND(100.0 * SUM(new_deaths) / NULLIF(SUM(new_cases), 0), 2) AS cfr_pct
FROM health_data.covid_data
WHERE continent IS NOT NULL
GROUP BY continent
ORDER BY cases_per_100k DESC;


-- Query 7: Case Fatality Rate by Country
-- Question: Which countries had the highest CFR?
-- Finding: Peru 4.88%, Egypt 4.81%, Mexico 4.39% — driven by testing gaps + older populations
SELECT
  location,
  MAX(total_cases) AS total_cases,
  MAX(total_deaths) AS total_deaths,
  ROUND(100.0 * MAX(total_deaths) / NULLIF(MAX(total_cases), 0), 2) AS cfr_pct
FROM health_data.covid_data
WHERE continent IS NOT NULL
GROUP BY location
HAVING total_cases > 100000
ORDER BY cfr_pct DESC
LIMIT 15;


-- Query 8: Monthly Trend Comparison (Kenya vs UK vs South Africa vs Germany)
-- Question: How do pandemic waves compare across Global North and South?
-- Finding: Synchronized waves despite 120x case count difference — reflects testing capacity
WITH monthly AS (
  SELECT
    location,
    DATE_FORMAT(date, '%Y-%m') AS month,
    SUM(new_cases) AS monthly_cases
  FROM health_data.covid_data
  WHERE location IN ('Kenya', 'United Kingdom', 'South Africa', 'Germany')
  GROUP BY location, DATE_FORMAT(date, '%Y-%m')
)
SELECT
  month,
  SUM(CASE WHEN location = 'Kenya' THEN monthly_cases END) AS kenya,
  SUM(CASE WHEN location = 'United Kingdom' THEN monthly_cases END) AS uk,
  SUM(CASE WHEN location = 'South Africa' THEN monthly_cases END) AS south_africa,
  SUM(CASE WHEN location = 'Germany' THEN monthly_cases END) AS germany
FROM monthly
GROUP BY month
ORDER BY month;
