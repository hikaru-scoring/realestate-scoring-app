# data_logic.py
"""REALESTATE-1000 scoring logic with realistic static data for all 50 US states + DC and top 30 metro areas."""

try:
    import streamlit as st
except ImportError:
    import types as _types
    st = _types.ModuleType("streamlit")
    st.cache_data = lambda **kwargs: (lambda fn: fn)
    st.secrets = {}

# ---------------------------------------------------------------------------
# State FIPS codes (50 states + DC)
# ---------------------------------------------------------------------------
STATE_FIPS = {
    "01": {"name": "Alabama", "abbr": "AL"},
    "02": {"name": "Alaska", "abbr": "AK"},
    "04": {"name": "Arizona", "abbr": "AZ"},
    "05": {"name": "Arkansas", "abbr": "AR"},
    "06": {"name": "California", "abbr": "CA"},
    "08": {"name": "Colorado", "abbr": "CO"},
    "09": {"name": "Connecticut", "abbr": "CT"},
    "10": {"name": "Delaware", "abbr": "DE"},
    "11": {"name": "District of Columbia", "abbr": "DC"},
    "12": {"name": "Florida", "abbr": "FL"},
    "13": {"name": "Georgia", "abbr": "GA"},
    "15": {"name": "Hawaii", "abbr": "HI"},
    "16": {"name": "Idaho", "abbr": "ID"},
    "17": {"name": "Illinois", "abbr": "IL"},
    "18": {"name": "Indiana", "abbr": "IN"},
    "19": {"name": "Iowa", "abbr": "IA"},
    "20": {"name": "Kansas", "abbr": "KS"},
    "21": {"name": "Kentucky", "abbr": "KY"},
    "22": {"name": "Louisiana", "abbr": "LA"},
    "23": {"name": "Maine", "abbr": "ME"},
    "24": {"name": "Maryland", "abbr": "MD"},
    "25": {"name": "Massachusetts", "abbr": "MA"},
    "26": {"name": "Michigan", "abbr": "MI"},
    "27": {"name": "Minnesota", "abbr": "MN"},
    "28": {"name": "Mississippi", "abbr": "MS"},
    "29": {"name": "Missouri", "abbr": "MO"},
    "30": {"name": "Montana", "abbr": "MT"},
    "31": {"name": "Nebraska", "abbr": "NE"},
    "32": {"name": "Nevada", "abbr": "NV"},
    "33": {"name": "New Hampshire", "abbr": "NH"},
    "34": {"name": "New Jersey", "abbr": "NJ"},
    "35": {"name": "New Mexico", "abbr": "NM"},
    "36": {"name": "New York", "abbr": "NY"},
    "37": {"name": "North Carolina", "abbr": "NC"},
    "38": {"name": "North Dakota", "abbr": "ND"},
    "39": {"name": "Ohio", "abbr": "OH"},
    "40": {"name": "Oklahoma", "abbr": "OK"},
    "41": {"name": "Oregon", "abbr": "OR"},
    "42": {"name": "Pennsylvania", "abbr": "PA"},
    "44": {"name": "Rhode Island", "abbr": "RI"},
    "45": {"name": "South Carolina", "abbr": "SC"},
    "46": {"name": "South Dakota", "abbr": "SD"},
    "47": {"name": "Tennessee", "abbr": "TN"},
    "48": {"name": "Texas", "abbr": "TX"},
    "49": {"name": "Utah", "abbr": "UT"},
    "50": {"name": "Vermont", "abbr": "VT"},
    "51": {"name": "Virginia", "abbr": "VA"},
    "53": {"name": "Washington", "abbr": "WA"},
    "54": {"name": "West Virginia", "abbr": "WV"},
    "55": {"name": "Wisconsin", "abbr": "WI"},
    "56": {"name": "Wyoming", "abbr": "WY"},
}

AXES_LABELS = [
    "Affordability",
    "Market Momentum",
    "Economic Foundation",
    "Risk Profile",
    "Investment Return",
]

AXES_DESCRIPTIONS = {
    "Affordability": "Home price-to-income ratio, mortgage burden, rent-to-income ratio. More affordable = higher score.",
    "Market Momentum": "YoY price appreciation, months of inventory, days on market. Healthy growth = higher score.",
    "Economic Foundation": "Unemployment rate, job growth, GDP per capita growth, population growth.",
    "Risk Profile": "Disaster frequency, flood zones, insurance costs, foreclosure rate. Lower risk = higher score.",
    "Investment Return": "Cap rate, 5-year appreciation, rent growth, vacancy rate.",
}

# ---------------------------------------------------------------------------
# Realistic state-level real estate data
# Based on Zillow, Census ACS, BLS, FEMA data (2025 approximations)
# ---------------------------------------------------------------------------
# Fields:
#   median_home_price: Median home price in USD
#   median_income: Median household income in USD
#   mortgage_rate: Current 30yr fixed rate (national ~6.8%)
#   rent_median: Median monthly rent
#   yoy_price_change: Year-over-year home price change (%)
#   months_inventory: Months of housing supply
#   days_on_market: Median days on market
#   unemployment: Unemployment rate (%)
#   job_growth: YoY job growth (%)
#   gdp_growth: GDP per capita growth (%)
#   pop_growth: Population growth (%)
#   disaster_freq: FEMA disaster declarations (5-year count)
#   flood_zone_pct: % of land in flood zone
#   insurance_index: Relative insurance cost (100 = national average)
#   foreclosure_rate: Foreclosure rate (%)
#   cap_rate: Rental cap rate (%)
#   price_appreciation_5yr: 5-year cumulative price appreciation (%)
#   rent_growth: YoY rent growth (%)
#   vacancy_rate: Rental vacancy rate (%)

STATES_DATA = {
    "AL": {
        "median_home_price": 215000, "median_income": 56950, "mortgage_rate": 6.8,
        "rent_median": 950, "yoy_price_change": 3.2, "months_inventory": 4.1,
        "days_on_market": 52, "unemployment": 3.1, "job_growth": 1.8,
        "gdp_growth": 2.1, "pop_growth": 0.3, "disaster_freq": 18,
        "flood_zone_pct": 8.5, "insurance_index": 115, "foreclosure_rate": 0.5,
        "cap_rate": 6.8, "price_appreciation_5yr": 42, "rent_growth": 3.5, "vacancy_rate": 7.2,
    },
    "AK": {
        "median_home_price": 310000, "median_income": 77790, "mortgage_rate": 6.8,
        "rent_median": 1250, "yoy_price_change": 1.5, "months_inventory": 5.8,
        "days_on_market": 78, "unemployment": 4.8, "job_growth": 0.5,
        "gdp_growth": 0.8, "pop_growth": -0.4, "disaster_freq": 12,
        "flood_zone_pct": 5.0, "insurance_index": 130, "foreclosure_rate": 0.6,
        "cap_rate": 5.2, "price_appreciation_5yr": 18, "rent_growth": 1.8, "vacancy_rate": 9.5,
    },
    "AZ": {
        "median_home_price": 395000, "median_income": 68950, "mortgage_rate": 6.8,
        "rent_median": 1450, "yoy_price_change": 2.8, "months_inventory": 4.5,
        "days_on_market": 45, "unemployment": 3.6, "job_growth": 2.8,
        "gdp_growth": 3.5, "pop_growth": 1.6, "disaster_freq": 8,
        "flood_zone_pct": 3.2, "insurance_index": 95, "foreclosure_rate": 0.4,
        "cap_rate": 5.5, "price_appreciation_5yr": 55, "rent_growth": 3.2, "vacancy_rate": 5.8,
    },
    "AR": {
        "median_home_price": 175000, "median_income": 52120, "mortgage_rate": 6.8,
        "rent_median": 810, "yoy_price_change": 4.1, "months_inventory": 3.8,
        "days_on_market": 48, "unemployment": 3.4, "job_growth": 1.5,
        "gdp_growth": 1.8, "pop_growth": 0.2, "disaster_freq": 16,
        "flood_zone_pct": 9.0, "insurance_index": 120, "foreclosure_rate": 0.5,
        "cap_rate": 7.5, "price_appreciation_5yr": 48, "rent_growth": 4.0, "vacancy_rate": 7.5,
    },
    "CA": {
        "median_home_price": 785000, "median_income": 84910, "mortgage_rate": 6.8,
        "rent_median": 2150, "yoy_price_change": 4.5, "months_inventory": 2.8,
        "days_on_market": 30, "unemployment": 4.9, "job_growth": 1.2,
        "gdp_growth": 3.2, "pop_growth": -0.1, "disaster_freq": 22,
        "flood_zone_pct": 4.5, "insurance_index": 140, "foreclosure_rate": 0.3,
        "cap_rate": 4.2, "price_appreciation_5yr": 38, "rent_growth": 4.5, "vacancy_rate": 4.2,
    },
    "CO": {
        "median_home_price": 530000, "median_income": 82250, "mortgage_rate": 6.8,
        "rent_median": 1750, "yoy_price_change": 2.1, "months_inventory": 4.2,
        "days_on_market": 38, "unemployment": 3.4, "job_growth": 2.2,
        "gdp_growth": 3.0, "pop_growth": 0.8, "disaster_freq": 10,
        "flood_zone_pct": 3.8, "insurance_index": 110, "foreclosure_rate": 0.3,
        "cap_rate": 4.8, "price_appreciation_5yr": 35, "rent_growth": 2.8, "vacancy_rate": 5.0,
    },
    "CT": {
        "median_home_price": 380000, "median_income": 83780, "mortgage_rate": 6.8,
        "rent_median": 1400, "yoy_price_change": 7.5, "months_inventory": 2.5,
        "days_on_market": 28, "unemployment": 3.8, "job_growth": 1.0,
        "gdp_growth": 2.0, "pop_growth": -0.1, "disaster_freq": 8,
        "flood_zone_pct": 6.5, "insurance_index": 115, "foreclosure_rate": 0.4,
        "cap_rate": 5.5, "price_appreciation_5yr": 52, "rent_growth": 5.0, "vacancy_rate": 5.5,
    },
    "DE": {
        "median_home_price": 340000, "median_income": 72720, "mortgage_rate": 6.8,
        "rent_median": 1250, "yoy_price_change": 5.2, "months_inventory": 3.2,
        "days_on_market": 35, "unemployment": 3.9, "job_growth": 1.3,
        "gdp_growth": 2.2, "pop_growth": 0.5, "disaster_freq": 7,
        "flood_zone_pct": 10.0, "insurance_index": 100, "foreclosure_rate": 0.5,
        "cap_rate": 5.8, "price_appreciation_5yr": 45, "rent_growth": 3.8, "vacancy_rate": 6.0,
    },
    "DC": {
        "median_home_price": 645000, "median_income": 101720, "mortgage_rate": 6.8,
        "rent_median": 2100, "yoy_price_change": 3.0, "months_inventory": 3.5,
        "days_on_market": 32, "unemployment": 4.5, "job_growth": 1.5,
        "gdp_growth": 2.8, "pop_growth": 0.1, "disaster_freq": 3,
        "flood_zone_pct": 5.0, "insurance_index": 95, "foreclosure_rate": 0.3,
        "cap_rate": 4.5, "price_appreciation_5yr": 28, "rent_growth": 2.5, "vacancy_rate": 6.8,
    },
    "FL": {
        "median_home_price": 395000, "median_income": 63420, "mortgage_rate": 6.8,
        "rent_median": 1650, "yoy_price_change": 3.5, "months_inventory": 5.2,
        "days_on_market": 55, "unemployment": 3.2, "job_growth": 2.5,
        "gdp_growth": 3.2, "pop_growth": 1.5, "disaster_freq": 28,
        "flood_zone_pct": 15.0, "insurance_index": 195, "foreclosure_rate": 0.5,
        "cap_rate": 5.8, "price_appreciation_5yr": 58, "rent_growth": 4.0, "vacancy_rate": 6.5,
    },
    "GA": {
        "median_home_price": 315000, "median_income": 65030, "mortgage_rate": 6.8,
        "rent_median": 1350, "yoy_price_change": 3.8, "months_inventory": 3.8,
        "days_on_market": 40, "unemployment": 3.3, "job_growth": 2.5,
        "gdp_growth": 3.0, "pop_growth": 0.9, "disaster_freq": 14,
        "flood_zone_pct": 6.5, "insurance_index": 110, "foreclosure_rate": 0.4,
        "cap_rate": 6.0, "price_appreciation_5yr": 50, "rent_growth": 3.5, "vacancy_rate": 6.0,
    },
    "HI": {
        "median_home_price": 835000, "median_income": 84600, "mortgage_rate": 6.8,
        "rent_median": 2200, "yoy_price_change": 4.0, "months_inventory": 3.8,
        "days_on_market": 42, "unemployment": 3.0, "job_growth": 1.8,
        "gdp_growth": 2.5, "pop_growth": -0.3, "disaster_freq": 10,
        "flood_zone_pct": 8.0, "insurance_index": 145, "foreclosure_rate": 0.2,
        "cap_rate": 4.0, "price_appreciation_5yr": 32, "rent_growth": 3.5, "vacancy_rate": 5.5,
    },
    "ID": {
        "median_home_price": 430000, "median_income": 64520, "mortgage_rate": 6.8,
        "rent_median": 1250, "yoy_price_change": 3.5, "months_inventory": 4.5,
        "days_on_market": 42, "unemployment": 3.0, "job_growth": 3.2,
        "gdp_growth": 4.0, "pop_growth": 2.2, "disaster_freq": 6,
        "flood_zone_pct": 2.5, "insurance_index": 85, "foreclosure_rate": 0.2,
        "cap_rate": 5.0, "price_appreciation_5yr": 68, "rent_growth": 4.5, "vacancy_rate": 4.0,
    },
    "IL": {
        "median_home_price": 255000, "median_income": 72200, "mortgage_rate": 6.8,
        "rent_median": 1200, "yoy_price_change": 5.0, "months_inventory": 3.0,
        "days_on_market": 30, "unemployment": 4.5, "job_growth": 0.8,
        "gdp_growth": 1.8, "pop_growth": -0.3, "disaster_freq": 14,
        "flood_zone_pct": 7.0, "insurance_index": 105, "foreclosure_rate": 0.6,
        "cap_rate": 6.5, "price_appreciation_5yr": 35, "rent_growth": 3.5, "vacancy_rate": 6.5,
    },
    "IN": {
        "median_home_price": 225000, "median_income": 61940, "mortgage_rate": 6.8,
        "rent_median": 1000, "yoy_price_change": 5.5, "months_inventory": 2.8,
        "days_on_market": 28, "unemployment": 3.3, "job_growth": 1.5,
        "gdp_growth": 2.2, "pop_growth": 0.3, "disaster_freq": 12,
        "flood_zone_pct": 7.5, "insurance_index": 100, "foreclosure_rate": 0.5,
        "cap_rate": 7.0, "price_appreciation_5yr": 52, "rent_growth": 4.5, "vacancy_rate": 6.0,
    },
    "IA": {
        "median_home_price": 195000, "median_income": 65570, "mortgage_rate": 6.8,
        "rent_median": 880, "yoy_price_change": 4.5, "months_inventory": 3.2,
        "days_on_market": 38, "unemployment": 2.8, "job_growth": 1.0,
        "gdp_growth": 1.5, "pop_growth": 0.0, "disaster_freq": 15,
        "flood_zone_pct": 10.0, "insurance_index": 95, "foreclosure_rate": 0.4,
        "cap_rate": 7.2, "price_appreciation_5yr": 38, "rent_growth": 3.0, "vacancy_rate": 6.8,
    },
    "KS": {
        "median_home_price": 205000, "median_income": 64520, "mortgage_rate": 6.8,
        "rent_median": 950, "yoy_price_change": 4.0, "months_inventory": 3.0,
        "days_on_market": 35, "unemployment": 2.9, "job_growth": 1.2,
        "gdp_growth": 1.8, "pop_growth": 0.1, "disaster_freq": 18,
        "flood_zone_pct": 6.0, "insurance_index": 115, "foreclosure_rate": 0.4,
        "cap_rate": 7.0, "price_appreciation_5yr": 40, "rent_growth": 3.2, "vacancy_rate": 7.0,
    },
    "KY": {
        "median_home_price": 195000, "median_income": 55580, "mortgage_rate": 6.8,
        "rent_median": 880, "yoy_price_change": 5.0, "months_inventory": 3.0,
        "days_on_market": 35, "unemployment": 3.8, "job_growth": 1.2,
        "gdp_growth": 1.5, "pop_growth": 0.1, "disaster_freq": 14,
        "flood_zone_pct": 8.0, "insurance_index": 105, "foreclosure_rate": 0.5,
        "cap_rate": 7.2, "price_appreciation_5yr": 45, "rent_growth": 4.0, "vacancy_rate": 6.5,
    },
    "LA": {
        "median_home_price": 195000, "median_income": 52290, "mortgage_rate": 6.8,
        "rent_median": 950, "yoy_price_change": 2.0, "months_inventory": 5.0,
        "days_on_market": 65, "unemployment": 4.2, "job_growth": 0.8,
        "gdp_growth": 1.0, "pop_growth": -0.3, "disaster_freq": 25,
        "flood_zone_pct": 18.0, "insurance_index": 180, "foreclosure_rate": 0.7,
        "cap_rate": 7.5, "price_appreciation_5yr": 22, "rent_growth": 2.0, "vacancy_rate": 8.5,
    },
    "ME": {
        "median_home_price": 355000, "median_income": 64770, "mortgage_rate": 6.8,
        "rent_median": 1250, "yoy_price_change": 7.0, "months_inventory": 2.5,
        "days_on_market": 28, "unemployment": 3.0, "job_growth": 0.8,
        "gdp_growth": 1.5, "pop_growth": 0.3, "disaster_freq": 6,
        "flood_zone_pct": 5.5, "insurance_index": 90, "foreclosure_rate": 0.3,
        "cap_rate": 5.5, "price_appreciation_5yr": 62, "rent_growth": 6.0, "vacancy_rate": 4.5,
    },
    "MD": {
        "median_home_price": 380000, "median_income": 90200, "mortgage_rate": 6.8,
        "rent_median": 1600, "yoy_price_change": 4.5, "months_inventory": 2.8,
        "days_on_market": 25, "unemployment": 3.5, "job_growth": 1.5,
        "gdp_growth": 2.5, "pop_growth": 0.2, "disaster_freq": 8,
        "flood_zone_pct": 8.0, "insurance_index": 100, "foreclosure_rate": 0.4,
        "cap_rate": 5.5, "price_appreciation_5yr": 38, "rent_growth": 3.5, "vacancy_rate": 5.5,
    },
    "MA": {
        "median_home_price": 595000, "median_income": 89640, "mortgage_rate": 6.8,
        "rent_median": 1950, "yoy_price_change": 6.5, "months_inventory": 1.8,
        "days_on_market": 22, "unemployment": 3.5, "job_growth": 1.2,
        "gdp_growth": 3.0, "pop_growth": 0.1, "disaster_freq": 7,
        "flood_zone_pct": 7.0, "insurance_index": 110, "foreclosure_rate": 0.2,
        "cap_rate": 4.5, "price_appreciation_5yr": 48, "rent_growth": 5.5, "vacancy_rate": 3.8,
    },
    "MI": {
        "median_home_price": 225000, "median_income": 63200, "mortgage_rate": 6.8,
        "rent_median": 1050, "yoy_price_change": 5.5, "months_inventory": 2.8,
        "days_on_market": 30, "unemployment": 4.0, "job_growth": 1.0,
        "gdp_growth": 1.5, "pop_growth": 0.0, "disaster_freq": 10,
        "flood_zone_pct": 5.5, "insurance_index": 105, "foreclosure_rate": 0.5,
        "cap_rate": 7.2, "price_appreciation_5yr": 48, "rent_growth": 4.5, "vacancy_rate": 6.2,
    },
    "MN": {
        "median_home_price": 325000, "median_income": 77720, "mortgage_rate": 6.8,
        "rent_median": 1250, "yoy_price_change": 3.5, "months_inventory": 2.5,
        "days_on_market": 28, "unemployment": 2.8, "job_growth": 1.5,
        "gdp_growth": 2.5, "pop_growth": 0.4, "disaster_freq": 10,
        "flood_zone_pct": 6.0, "insurance_index": 100, "foreclosure_rate": 0.3,
        "cap_rate": 5.8, "price_appreciation_5yr": 38, "rent_growth": 3.0, "vacancy_rate": 4.8,
    },
    "MS": {
        "median_home_price": 160000, "median_income": 48610, "mortgage_rate": 6.8,
        "rent_median": 800, "yoy_price_change": 3.5, "months_inventory": 4.8,
        "days_on_market": 58, "unemployment": 3.8, "job_growth": 0.8,
        "gdp_growth": 1.0, "pop_growth": -0.2, "disaster_freq": 20,
        "flood_zone_pct": 12.0, "insurance_index": 150, "foreclosure_rate": 0.6,
        "cap_rate": 8.0, "price_appreciation_5yr": 38, "rent_growth": 3.0, "vacancy_rate": 8.8,
    },
    "MO": {
        "median_home_price": 220000, "median_income": 60590, "mortgage_rate": 6.8,
        "rent_median": 1000, "yoy_price_change": 4.2, "months_inventory": 3.2,
        "days_on_market": 35, "unemployment": 3.0, "job_growth": 1.2,
        "gdp_growth": 1.8, "pop_growth": 0.1, "disaster_freq": 16,
        "flood_zone_pct": 7.5, "insurance_index": 110, "foreclosure_rate": 0.4,
        "cap_rate": 7.0, "price_appreciation_5yr": 42, "rent_growth": 3.5, "vacancy_rate": 6.5,
    },
    "MT": {
        "median_home_price": 430000, "median_income": 60560, "mortgage_rate": 6.8,
        "rent_median": 1150, "yoy_price_change": 2.0, "months_inventory": 5.5,
        "days_on_market": 62, "unemployment": 2.8, "job_growth": 1.5,
        "gdp_growth": 2.0, "pop_growth": 1.0, "disaster_freq": 8,
        "flood_zone_pct": 2.0, "insurance_index": 90, "foreclosure_rate": 0.2,
        "cap_rate": 4.8, "price_appreciation_5yr": 58, "rent_growth": 3.0, "vacancy_rate": 4.5,
    },
    "NE": {
        "median_home_price": 240000, "median_income": 66640, "mortgage_rate": 6.8,
        "rent_median": 1000, "yoy_price_change": 5.0, "months_inventory": 2.5,
        "days_on_market": 28, "unemployment": 2.5, "job_growth": 1.2,
        "gdp_growth": 2.0, "pop_growth": 0.3, "disaster_freq": 14,
        "flood_zone_pct": 6.5, "insurance_index": 105, "foreclosure_rate": 0.3,
        "cap_rate": 6.5, "price_appreciation_5yr": 42, "rent_growth": 3.5, "vacancy_rate": 5.5,
    },
    "NV": {
        "median_home_price": 420000, "median_income": 66830, "mortgage_rate": 6.8,
        "rent_median": 1500, "yoy_price_change": 4.0, "months_inventory": 4.0,
        "days_on_market": 42, "unemployment": 5.2, "job_growth": 2.5,
        "gdp_growth": 3.5, "pop_growth": 1.2, "disaster_freq": 4,
        "flood_zone_pct": 1.5, "insurance_index": 85, "foreclosure_rate": 0.5,
        "cap_rate": 5.5, "price_appreciation_5yr": 48, "rent_growth": 4.0, "vacancy_rate": 6.0,
    },
    "NH": {
        "median_home_price": 440000, "median_income": 83450, "mortgage_rate": 6.8,
        "rent_median": 1550, "yoy_price_change": 8.0, "months_inventory": 1.5,
        "days_on_market": 20, "unemployment": 2.5, "job_growth": 1.5,
        "gdp_growth": 2.5, "pop_growth": 0.5, "disaster_freq": 5,
        "flood_zone_pct": 4.0, "insurance_index": 90, "foreclosure_rate": 0.2,
        "cap_rate": 5.0, "price_appreciation_5yr": 58, "rent_growth": 6.0, "vacancy_rate": 3.5,
    },
    "NJ": {
        "median_home_price": 480000, "median_income": 89290, "mortgage_rate": 6.8,
        "rent_median": 1650, "yoy_price_change": 7.0, "months_inventory": 2.2,
        "days_on_market": 28, "unemployment": 4.0, "job_growth": 1.2,
        "gdp_growth": 2.2, "pop_growth": 0.1, "disaster_freq": 10,
        "flood_zone_pct": 9.0, "insurance_index": 120, "foreclosure_rate": 0.5,
        "cap_rate": 5.2, "price_appreciation_5yr": 48, "rent_growth": 5.0, "vacancy_rate": 4.8,
    },
    "NM": {
        "median_home_price": 275000, "median_income": 53980, "mortgage_rate": 6.8,
        "rent_median": 1050, "yoy_price_change": 3.0, "months_inventory": 4.5,
        "days_on_market": 52, "unemployment": 4.0, "job_growth": 1.5,
        "gdp_growth": 2.0, "pop_growth": 0.2, "disaster_freq": 8,
        "flood_zone_pct": 2.0, "insurance_index": 90, "foreclosure_rate": 0.4,
        "cap_rate": 6.0, "price_appreciation_5yr": 40, "rent_growth": 3.0, "vacancy_rate": 7.0,
    },
    "NY": {
        "median_home_price": 420000, "median_income": 74310, "mortgage_rate": 6.8,
        "rent_median": 1650, "yoy_price_change": 5.5, "months_inventory": 3.5,
        "days_on_market": 55, "unemployment": 4.2, "job_growth": 1.0,
        "gdp_growth": 2.5, "pop_growth": -0.5, "disaster_freq": 12,
        "flood_zone_pct": 7.0, "insurance_index": 115, "foreclosure_rate": 0.5,
        "cap_rate": 5.2, "price_appreciation_5yr": 35, "rent_growth": 4.0, "vacancy_rate": 5.5,
    },
    "NC": {
        "median_home_price": 325000, "median_income": 63770, "mortgage_rate": 6.8,
        "rent_median": 1300, "yoy_price_change": 5.0, "months_inventory": 3.0,
        "days_on_market": 32, "unemployment": 3.5, "job_growth": 2.5,
        "gdp_growth": 3.0, "pop_growth": 1.0, "disaster_freq": 12,
        "flood_zone_pct": 7.0, "insurance_index": 105, "foreclosure_rate": 0.3,
        "cap_rate": 5.8, "price_appreciation_5yr": 52, "rent_growth": 4.0, "vacancy_rate": 5.2,
    },
    "ND": {
        "median_home_price": 240000, "median_income": 68120, "mortgage_rate": 6.8,
        "rent_median": 900, "yoy_price_change": 2.0, "months_inventory": 5.0,
        "days_on_market": 65, "unemployment": 2.2, "job_growth": 0.5,
        "gdp_growth": 1.0, "pop_growth": -0.2, "disaster_freq": 12,
        "flood_zone_pct": 8.0, "insurance_index": 100, "foreclosure_rate": 0.3,
        "cap_rate": 6.5, "price_appreciation_5yr": 18, "rent_growth": 1.5, "vacancy_rate": 8.0,
    },
    "OH": {
        "median_home_price": 210000, "median_income": 60110, "mortgage_rate": 6.8,
        "rent_median": 950, "yoy_price_change": 5.5, "months_inventory": 2.5,
        "days_on_market": 25, "unemployment": 3.8, "job_growth": 0.8,
        "gdp_growth": 1.5, "pop_growth": -0.1, "disaster_freq": 12,
        "flood_zone_pct": 6.0, "insurance_index": 95, "foreclosure_rate": 0.5,
        "cap_rate": 7.5, "price_appreciation_5yr": 48, "rent_growth": 4.5, "vacancy_rate": 5.8,
    },
    "OK": {
        "median_home_price": 195000, "median_income": 56950, "mortgage_rate": 6.8,
        "rent_median": 900, "yoy_price_change": 3.0, "months_inventory": 3.8,
        "days_on_market": 42, "unemployment": 3.2, "job_growth": 1.5,
        "gdp_growth": 2.0, "pop_growth": 0.3, "disaster_freq": 22,
        "flood_zone_pct": 5.5, "insurance_index": 135, "foreclosure_rate": 0.5,
        "cap_rate": 7.5, "price_appreciation_5yr": 38, "rent_growth": 3.0, "vacancy_rate": 7.5,
    },
    "OR": {
        "median_home_price": 480000, "median_income": 71430, "mortgage_rate": 6.8,
        "rent_median": 1500, "yoy_price_change": 1.5, "months_inventory": 4.5,
        "days_on_market": 48, "unemployment": 4.0, "job_growth": 1.2,
        "gdp_growth": 2.5, "pop_growth": 0.5, "disaster_freq": 8,
        "flood_zone_pct": 4.0, "insurance_index": 90, "foreclosure_rate": 0.3,
        "cap_rate": 4.8, "price_appreciation_5yr": 32, "rent_growth": 2.5, "vacancy_rate": 4.5,
    },
    "PA": {
        "median_home_price": 260000, "median_income": 67580, "mortgage_rate": 6.8,
        "rent_median": 1150, "yoy_price_change": 5.5, "months_inventory": 2.5,
        "days_on_market": 28, "unemployment": 3.8, "job_growth": 0.8,
        "gdp_growth": 1.8, "pop_growth": 0.0, "disaster_freq": 10,
        "flood_zone_pct": 5.5, "insurance_index": 95, "foreclosure_rate": 0.4,
        "cap_rate": 6.5, "price_appreciation_5yr": 42, "rent_growth": 4.0, "vacancy_rate": 5.5,
    },
    "RI": {
        "median_home_price": 410000, "median_income": 71160, "mortgage_rate": 6.8,
        "rent_median": 1400, "yoy_price_change": 8.5, "months_inventory": 1.8,
        "days_on_market": 22, "unemployment": 3.5, "job_growth": 1.0,
        "gdp_growth": 1.8, "pop_growth": 0.0, "disaster_freq": 6,
        "flood_zone_pct": 8.0, "insurance_index": 110, "foreclosure_rate": 0.3,
        "cap_rate": 5.5, "price_appreciation_5yr": 62, "rent_growth": 6.5, "vacancy_rate": 4.0,
    },
    "SC": {
        "median_home_price": 290000, "median_income": 59320, "mortgage_rate": 6.8,
        "rent_median": 1200, "yoy_price_change": 5.5, "months_inventory": 3.5,
        "days_on_market": 38, "unemployment": 3.2, "job_growth": 2.2,
        "gdp_growth": 2.8, "pop_growth": 1.2, "disaster_freq": 14,
        "flood_zone_pct": 8.0, "insurance_index": 120, "foreclosure_rate": 0.4,
        "cap_rate": 6.2, "price_appreciation_5yr": 55, "rent_growth": 4.5, "vacancy_rate": 5.5,
    },
    "SD": {
        "median_home_price": 285000, "median_income": 63920, "mortgage_rate": 6.8,
        "rent_median": 950, "yoy_price_change": 4.0, "months_inventory": 3.5,
        "days_on_market": 42, "unemployment": 2.2, "job_growth": 1.0,
        "gdp_growth": 1.8, "pop_growth": 0.5, "disaster_freq": 12,
        "flood_zone_pct": 5.0, "insurance_index": 105, "foreclosure_rate": 0.2,
        "cap_rate": 6.0, "price_appreciation_5yr": 42, "rent_growth": 3.5, "vacancy_rate": 5.8,
    },
    "TN": {
        "median_home_price": 310000, "median_income": 59700, "mortgage_rate": 6.8,
        "rent_median": 1250, "yoy_price_change": 3.8, "months_inventory": 3.5,
        "days_on_market": 38, "unemployment": 3.2, "job_growth": 2.2,
        "gdp_growth": 2.8, "pop_growth": 0.8, "disaster_freq": 14,
        "flood_zone_pct": 6.5, "insurance_index": 110, "foreclosure_rate": 0.4,
        "cap_rate": 6.0, "price_appreciation_5yr": 55, "rent_growth": 4.0, "vacancy_rate": 5.8,
    },
    "TX": {
        "median_home_price": 295000, "median_income": 67680, "mortgage_rate": 6.8,
        "rent_median": 1350, "yoy_price_change": 1.5, "months_inventory": 4.8,
        "days_on_market": 52, "unemployment": 3.8, "job_growth": 2.8,
        "gdp_growth": 3.5, "pop_growth": 1.5, "disaster_freq": 20,
        "flood_zone_pct": 8.0, "insurance_index": 140, "foreclosure_rate": 0.4,
        "cap_rate": 6.0, "price_appreciation_5yr": 35, "rent_growth": 2.0, "vacancy_rate": 7.0,
    },
    "UT": {
        "median_home_price": 480000, "median_income": 78530, "mortgage_rate": 6.8,
        "rent_median": 1450, "yoy_price_change": 3.0, "months_inventory": 4.0,
        "days_on_market": 38, "unemployment": 2.8, "job_growth": 3.5,
        "gdp_growth": 4.2, "pop_growth": 1.8, "disaster_freq": 5,
        "flood_zone_pct": 1.5, "insurance_index": 80, "foreclosure_rate": 0.2,
        "cap_rate": 4.8, "price_appreciation_5yr": 48, "rent_growth": 3.0, "vacancy_rate": 4.0,
    },
    "VT": {
        "median_home_price": 350000, "median_income": 65440, "mortgage_rate": 6.8,
        "rent_median": 1300, "yoy_price_change": 8.0, "months_inventory": 1.5,
        "days_on_market": 20, "unemployment": 2.2, "job_growth": 0.5,
        "gdp_growth": 1.2, "pop_growth": 0.2, "disaster_freq": 5,
        "flood_zone_pct": 4.0, "insurance_index": 85, "foreclosure_rate": 0.2,
        "cap_rate": 5.5, "price_appreciation_5yr": 58, "rent_growth": 6.0, "vacancy_rate": 3.5,
    },
    "VA": {
        "median_home_price": 380000, "median_income": 80590, "mortgage_rate": 6.8,
        "rent_median": 1500, "yoy_price_change": 4.5, "months_inventory": 2.5,
        "days_on_market": 28, "unemployment": 2.8, "job_growth": 1.8,
        "gdp_growth": 2.8, "pop_growth": 0.5, "disaster_freq": 10,
        "flood_zone_pct": 6.0, "insurance_index": 95, "foreclosure_rate": 0.3,
        "cap_rate": 5.5, "price_appreciation_5yr": 40, "rent_growth": 3.5, "vacancy_rate": 5.0,
    },
    "WA": {
        "median_home_price": 575000, "median_income": 84250, "mortgage_rate": 6.8,
        "rent_median": 1800, "yoy_price_change": 3.0, "months_inventory": 3.2,
        "days_on_market": 25, "unemployment": 3.8, "job_growth": 2.0,
        "gdp_growth": 3.5, "pop_growth": 0.8, "disaster_freq": 8,
        "flood_zone_pct": 4.5, "insurance_index": 90, "foreclosure_rate": 0.2,
        "cap_rate": 4.5, "price_appreciation_5yr": 35, "rent_growth": 3.5, "vacancy_rate": 4.5,
    },
    "WV": {
        "median_home_price": 130000, "median_income": 48040, "mortgage_rate": 6.8,
        "rent_median": 750, "yoy_price_change": 5.0, "months_inventory": 5.5,
        "days_on_market": 72, "unemployment": 4.5, "job_growth": -0.2,
        "gdp_growth": 0.5, "pop_growth": -0.6, "disaster_freq": 12,
        "flood_zone_pct": 6.0, "insurance_index": 95, "foreclosure_rate": 0.6,
        "cap_rate": 9.0, "price_appreciation_5yr": 42, "rent_growth": 3.0, "vacancy_rate": 9.5,
    },
    "WI": {
        "median_home_price": 270000, "median_income": 67080, "mortgage_rate": 6.8,
        "rent_median": 1050, "yoy_price_change": 5.5, "months_inventory": 2.2,
        "days_on_market": 25, "unemployment": 2.8, "job_growth": 1.2,
        "gdp_growth": 2.0, "pop_growth": 0.2, "disaster_freq": 10,
        "flood_zone_pct": 5.5, "insurance_index": 95, "foreclosure_rate": 0.3,
        "cap_rate": 6.5, "price_appreciation_5yr": 48, "rent_growth": 4.0, "vacancy_rate": 5.0,
    },
    "WY": {
        "median_home_price": 310000, "median_income": 67060, "mortgage_rate": 6.8,
        "rent_median": 1000, "yoy_price_change": 2.5, "months_inventory": 5.5,
        "days_on_market": 68, "unemployment": 3.2, "job_growth": 0.8,
        "gdp_growth": 1.5, "pop_growth": 0.0, "disaster_freq": 6,
        "flood_zone_pct": 2.0, "insurance_index": 90, "foreclosure_rate": 0.3,
        "cap_rate": 5.8, "price_appreciation_5yr": 28, "rent_growth": 2.5, "vacancy_rate": 7.5,
    },
}

# ---------------------------------------------------------------------------
# Top 30 Metro Areas - Realistic data
# ---------------------------------------------------------------------------
METRO_DATA = {
    "New York": {
        "state": "NY", "lat": 40.7128, "lng": -74.0060,
        "median_home_price": 620000, "median_income": 78100, "mortgage_rate": 6.8,
        "rent_median": 2400, "yoy_price_change": 5.0, "months_inventory": 3.8,
        "days_on_market": 52, "unemployment": 4.5, "job_growth": 1.2,
        "gdp_growth": 2.8, "pop_growth": -0.3, "disaster_freq": 8,
        "flood_zone_pct": 12.0, "insurance_index": 135, "foreclosure_rate": 0.5,
        "cap_rate": 4.2, "price_appreciation_5yr": 30, "rent_growth": 4.5, "vacancy_rate": 4.8,
    },
    "Los Angeles": {
        "state": "CA", "lat": 34.0522, "lng": -118.2437,
        "median_home_price": 920000, "median_income": 76500, "mortgage_rate": 6.8,
        "rent_median": 2500, "yoy_price_change": 5.5, "months_inventory": 2.8,
        "days_on_market": 35, "unemployment": 5.2, "job_growth": 1.0,
        "gdp_growth": 3.0, "pop_growth": -0.3, "disaster_freq": 15,
        "flood_zone_pct": 3.5, "insurance_index": 155, "foreclosure_rate": 0.3,
        "cap_rate": 3.8, "price_appreciation_5yr": 35, "rent_growth": 5.0, "vacancy_rate": 4.0,
    },
    "Chicago": {
        "state": "IL", "lat": 41.8781, "lng": -87.6298,
        "median_home_price": 315000, "median_income": 72000, "mortgage_rate": 6.8,
        "rent_median": 1550, "yoy_price_change": 5.5, "months_inventory": 2.5,
        "days_on_market": 28, "unemployment": 4.8, "job_growth": 0.8,
        "gdp_growth": 2.0, "pop_growth": -0.5, "disaster_freq": 10,
        "flood_zone_pct": 6.0, "insurance_index": 110, "foreclosure_rate": 0.6,
        "cap_rate": 6.5, "price_appreciation_5yr": 32, "rent_growth": 3.5, "vacancy_rate": 6.0,
    },
    "Houston": {
        "state": "TX", "lat": 29.7604, "lng": -95.3698,
        "median_home_price": 310000, "median_income": 68500, "mortgage_rate": 6.8,
        "rent_median": 1350, "yoy_price_change": 1.8, "months_inventory": 4.5,
        "days_on_market": 48, "unemployment": 4.0, "job_growth": 3.0,
        "gdp_growth": 3.8, "pop_growth": 1.8, "disaster_freq": 22,
        "flood_zone_pct": 18.0, "insurance_index": 165, "foreclosure_rate": 0.4,
        "cap_rate": 6.2, "price_appreciation_5yr": 32, "rent_growth": 2.5, "vacancy_rate": 7.5,
    },
    "Phoenix": {
        "state": "AZ", "lat": 33.4484, "lng": -112.0740,
        "median_home_price": 420000, "median_income": 70200, "mortgage_rate": 6.8,
        "rent_median": 1550, "yoy_price_change": 3.2, "months_inventory": 4.2,
        "days_on_market": 42, "unemployment": 3.5, "job_growth": 3.0,
        "gdp_growth": 3.8, "pop_growth": 2.0, "disaster_freq": 6,
        "flood_zone_pct": 2.5, "insurance_index": 90, "foreclosure_rate": 0.4,
        "cap_rate": 5.5, "price_appreciation_5yr": 55, "rent_growth": 3.5, "vacancy_rate": 5.5,
    },
    "Philadelphia": {
        "state": "PA", "lat": 39.9526, "lng": -75.1652,
        "median_home_price": 310000, "median_income": 68000, "mortgage_rate": 6.8,
        "rent_median": 1400, "yoy_price_change": 6.0, "months_inventory": 2.2,
        "days_on_market": 25, "unemployment": 4.2, "job_growth": 0.8,
        "gdp_growth": 2.0, "pop_growth": -0.2, "disaster_freq": 8,
        "flood_zone_pct": 6.5, "insurance_index": 100, "foreclosure_rate": 0.5,
        "cap_rate": 6.5, "price_appreciation_5yr": 42, "rent_growth": 4.0, "vacancy_rate": 5.5,
    },
    "San Antonio": {
        "state": "TX", "lat": 29.4241, "lng": -98.4936,
        "median_home_price": 275000, "median_income": 60500, "mortgage_rate": 6.8,
        "rent_median": 1250, "yoy_price_change": 1.5, "months_inventory": 5.0,
        "days_on_market": 55, "unemployment": 3.5, "job_growth": 2.2,
        "gdp_growth": 2.8, "pop_growth": 1.5, "disaster_freq": 12,
        "flood_zone_pct": 6.0, "insurance_index": 120, "foreclosure_rate": 0.4,
        "cap_rate": 6.0, "price_appreciation_5yr": 35, "rent_growth": 2.5, "vacancy_rate": 7.0,
    },
    "San Diego": {
        "state": "CA", "lat": 32.7157, "lng": -117.1611,
        "median_home_price": 850000, "median_income": 83500, "mortgage_rate": 6.8,
        "rent_median": 2300, "yoy_price_change": 5.0, "months_inventory": 2.5,
        "days_on_market": 28, "unemployment": 3.8, "job_growth": 1.5,
        "gdp_growth": 3.2, "pop_growth": 0.2, "disaster_freq": 8,
        "flood_zone_pct": 3.0, "insurance_index": 120, "foreclosure_rate": 0.2,
        "cap_rate": 3.8, "price_appreciation_5yr": 42, "rent_growth": 5.0, "vacancy_rate": 3.5,
    },
    "Dallas": {
        "state": "TX", "lat": 32.7767, "lng": -96.7970,
        "median_home_price": 370000, "median_income": 72000, "mortgage_rate": 6.8,
        "rent_median": 1500, "yoy_price_change": 2.0, "months_inventory": 4.0,
        "days_on_market": 42, "unemployment": 3.5, "job_growth": 3.2,
        "gdp_growth": 4.0, "pop_growth": 1.8, "disaster_freq": 14,
        "flood_zone_pct": 5.0, "insurance_index": 130, "foreclosure_rate": 0.3,
        "cap_rate": 5.5, "price_appreciation_5yr": 38, "rent_growth": 2.5, "vacancy_rate": 6.5,
    },
    "San Jose": {
        "state": "CA", "lat": 37.3382, "lng": -121.8863,
        "median_home_price": 1350000, "median_income": 128500, "mortgage_rate": 6.8,
        "rent_median": 3000, "yoy_price_change": 6.0, "months_inventory": 2.0,
        "days_on_market": 22, "unemployment": 3.5, "job_growth": 2.0,
        "gdp_growth": 4.5, "pop_growth": 0.3, "disaster_freq": 10,
        "flood_zone_pct": 3.0, "insurance_index": 130, "foreclosure_rate": 0.2,
        "cap_rate": 3.5, "price_appreciation_5yr": 35, "rent_growth": 5.5, "vacancy_rate": 3.0,
    },
    "Austin": {
        "state": "TX", "lat": 30.2672, "lng": -97.7431,
        "median_home_price": 440000, "median_income": 80000, "mortgage_rate": 6.8,
        "rent_median": 1600, "yoy_price_change": 0.5, "months_inventory": 5.5,
        "days_on_market": 58, "unemployment": 3.2, "job_growth": 3.5,
        "gdp_growth": 4.5, "pop_growth": 2.5, "disaster_freq": 10,
        "flood_zone_pct": 5.0, "insurance_index": 115, "foreclosure_rate": 0.3,
        "cap_rate": 4.8, "price_appreciation_5yr": 42, "rent_growth": 1.5, "vacancy_rate": 7.5,
    },
    "Jacksonville": {
        "state": "FL", "lat": 30.3322, "lng": -81.6557,
        "median_home_price": 340000, "median_income": 62000, "mortgage_rate": 6.8,
        "rent_median": 1400, "yoy_price_change": 3.5, "months_inventory": 4.2,
        "days_on_market": 45, "unemployment": 3.0, "job_growth": 2.8,
        "gdp_growth": 3.2, "pop_growth": 1.8, "disaster_freq": 18,
        "flood_zone_pct": 12.0, "insurance_index": 170, "foreclosure_rate": 0.4,
        "cap_rate": 5.8, "price_appreciation_5yr": 55, "rent_growth": 4.0, "vacancy_rate": 6.0,
    },
    "Fort Worth": {
        "state": "TX", "lat": 32.7555, "lng": -97.3308,
        "median_home_price": 330000, "median_income": 68000, "mortgage_rate": 6.8,
        "rent_median": 1400, "yoy_price_change": 1.8, "months_inventory": 4.2,
        "days_on_market": 45, "unemployment": 3.2, "job_growth": 3.0,
        "gdp_growth": 3.8, "pop_growth": 2.0, "disaster_freq": 14,
        "flood_zone_pct": 5.0, "insurance_index": 125, "foreclosure_rate": 0.3,
        "cap_rate": 5.8, "price_appreciation_5yr": 38, "rent_growth": 2.5, "vacancy_rate": 6.2,
    },
    "Columbus": {
        "state": "OH", "lat": 39.9612, "lng": -82.9988,
        "median_home_price": 275000, "median_income": 62500, "mortgage_rate": 6.8,
        "rent_median": 1200, "yoy_price_change": 6.0, "months_inventory": 2.2,
        "days_on_market": 22, "unemployment": 3.2, "job_growth": 2.0,
        "gdp_growth": 2.8, "pop_growth": 0.8, "disaster_freq": 8,
        "flood_zone_pct": 4.5, "insurance_index": 90, "foreclosure_rate": 0.4,
        "cap_rate": 6.5, "price_appreciation_5yr": 52, "rent_growth": 4.5, "vacancy_rate": 5.0,
    },
    "Charlotte": {
        "state": "NC", "lat": 35.2271, "lng": -80.8431,
        "median_home_price": 380000, "median_income": 68500, "mortgage_rate": 6.8,
        "rent_median": 1450, "yoy_price_change": 5.5, "months_inventory": 2.8,
        "days_on_market": 28, "unemployment": 3.0, "job_growth": 3.0,
        "gdp_growth": 3.5, "pop_growth": 1.8, "disaster_freq": 8,
        "flood_zone_pct": 5.0, "insurance_index": 100, "foreclosure_rate": 0.3,
        "cap_rate": 5.5, "price_appreciation_5yr": 55, "rent_growth": 4.5, "vacancy_rate": 4.8,
    },
    "Indianapolis": {
        "state": "IN", "lat": 39.7684, "lng": -86.1581,
        "median_home_price": 260000, "median_income": 58000, "mortgage_rate": 6.8,
        "rent_median": 1150, "yoy_price_change": 6.0, "months_inventory": 2.5,
        "days_on_market": 25, "unemployment": 3.2, "job_growth": 1.8,
        "gdp_growth": 2.5, "pop_growth": 0.5, "disaster_freq": 10,
        "flood_zone_pct": 6.0, "insurance_index": 95, "foreclosure_rate": 0.5,
        "cap_rate": 7.0, "price_appreciation_5yr": 52, "rent_growth": 4.5, "vacancy_rate": 5.5,
    },
    "San Francisco": {
        "state": "CA", "lat": 37.7749, "lng": -122.4194,
        "median_home_price": 1250000, "median_income": 121500, "mortgage_rate": 6.8,
        "rent_median": 3200, "yoy_price_change": 3.5, "months_inventory": 3.0,
        "days_on_market": 28, "unemployment": 3.8, "job_growth": 1.5,
        "gdp_growth": 4.0, "pop_growth": -0.5, "disaster_freq": 12,
        "flood_zone_pct": 5.0, "insurance_index": 140, "foreclosure_rate": 0.2,
        "cap_rate": 3.5, "price_appreciation_5yr": 25, "rent_growth": 4.0, "vacancy_rate": 5.0,
    },
    "Seattle": {
        "state": "WA", "lat": 47.6062, "lng": -122.3321,
        "median_home_price": 780000, "median_income": 105000, "mortgage_rate": 6.8,
        "rent_median": 2200, "yoy_price_change": 4.0, "months_inventory": 2.5,
        "days_on_market": 22, "unemployment": 3.5, "job_growth": 2.5,
        "gdp_growth": 4.0, "pop_growth": 0.5, "disaster_freq": 6,
        "flood_zone_pct": 3.5, "insurance_index": 95, "foreclosure_rate": 0.2,
        "cap_rate": 4.0, "price_appreciation_5yr": 35, "rent_growth": 4.5, "vacancy_rate": 4.0,
    },
    "Denver": {
        "state": "CO", "lat": 39.7392, "lng": -104.9903,
        "median_home_price": 560000, "median_income": 82000, "mortgage_rate": 6.8,
        "rent_median": 1800, "yoy_price_change": 1.8, "months_inventory": 4.5,
        "days_on_market": 38, "unemployment": 3.2, "job_growth": 2.5,
        "gdp_growth": 3.2, "pop_growth": 0.8, "disaster_freq": 8,
        "flood_zone_pct": 3.0, "insurance_index": 105, "foreclosure_rate": 0.3,
        "cap_rate": 4.5, "price_appreciation_5yr": 30, "rent_growth": 2.5, "vacancy_rate": 5.5,
    },
    "Nashville": {
        "state": "TN", "lat": 36.1627, "lng": -86.7816,
        "median_home_price": 420000, "median_income": 68000, "mortgage_rate": 6.8,
        "rent_median": 1600, "yoy_price_change": 3.5, "months_inventory": 3.5,
        "days_on_market": 35, "unemployment": 2.8, "job_growth": 2.8,
        "gdp_growth": 3.5, "pop_growth": 1.2, "disaster_freq": 10,
        "flood_zone_pct": 5.5, "insurance_index": 105, "foreclosure_rate": 0.3,
        "cap_rate": 5.2, "price_appreciation_5yr": 52, "rent_growth": 3.5, "vacancy_rate": 5.0,
    },
    "Oklahoma City": {
        "state": "OK", "lat": 35.4676, "lng": -97.5164,
        "median_home_price": 220000, "median_income": 58500, "mortgage_rate": 6.8,
        "rent_median": 1000, "yoy_price_change": 3.0, "months_inventory": 3.5,
        "days_on_market": 38, "unemployment": 3.0, "job_growth": 1.8,
        "gdp_growth": 2.5, "pop_growth": 0.5, "disaster_freq": 20,
        "flood_zone_pct": 5.0, "insurance_index": 140, "foreclosure_rate": 0.5,
        "cap_rate": 7.0, "price_appreciation_5yr": 35, "rent_growth": 3.0, "vacancy_rate": 7.0,
    },
    "El Paso": {
        "state": "TX", "lat": 31.7619, "lng": -106.4850,
        "median_home_price": 210000, "median_income": 50000, "mortgage_rate": 6.8,
        "rent_median": 950, "yoy_price_change": 2.5, "months_inventory": 4.0,
        "days_on_market": 48, "unemployment": 4.0, "job_growth": 1.5,
        "gdp_growth": 2.0, "pop_growth": 0.5, "disaster_freq": 4,
        "flood_zone_pct": 2.0, "insurance_index": 85, "foreclosure_rate": 0.3,
        "cap_rate": 6.5, "price_appreciation_5yr": 38, "rent_growth": 3.0, "vacancy_rate": 6.5,
    },
    "Las Vegas": {
        "state": "NV", "lat": 36.1699, "lng": -115.1398,
        "median_home_price": 410000, "median_income": 62500, "mortgage_rate": 6.8,
        "rent_median": 1500, "yoy_price_change": 4.5, "months_inventory": 3.8,
        "days_on_market": 38, "unemployment": 5.5, "job_growth": 2.8,
        "gdp_growth": 3.5, "pop_growth": 1.5, "disaster_freq": 3,
        "flood_zone_pct": 1.5, "insurance_index": 80, "foreclosure_rate": 0.5,
        "cap_rate": 5.5, "price_appreciation_5yr": 48, "rent_growth": 4.5, "vacancy_rate": 6.0,
    },
    "Memphis": {
        "state": "TN", "lat": 35.1495, "lng": -90.0490,
        "median_home_price": 195000, "median_income": 48000, "mortgage_rate": 6.8,
        "rent_median": 1050, "yoy_price_change": 3.0, "months_inventory": 3.8,
        "days_on_market": 42, "unemployment": 4.5, "job_growth": 1.0,
        "gdp_growth": 1.5, "pop_growth": -0.2, "disaster_freq": 12,
        "flood_zone_pct": 10.0, "insurance_index": 115, "foreclosure_rate": 0.6,
        "cap_rate": 8.5, "price_appreciation_5yr": 42, "rent_growth": 3.5, "vacancy_rate": 8.0,
    },
    "Louisville": {
        "state": "KY", "lat": 38.2527, "lng": -85.7585,
        "median_home_price": 245000, "median_income": 58500, "mortgage_rate": 6.8,
        "rent_median": 1050, "yoy_price_change": 5.0, "months_inventory": 2.8,
        "days_on_market": 28, "unemployment": 3.5, "job_growth": 1.5,
        "gdp_growth": 2.0, "pop_growth": 0.2, "disaster_freq": 10,
        "flood_zone_pct": 8.0, "insurance_index": 100, "foreclosure_rate": 0.4,
        "cap_rate": 7.0, "price_appreciation_5yr": 45, "rent_growth": 4.0, "vacancy_rate": 5.8,
    },
    "Baltimore": {
        "state": "MD", "lat": 39.2904, "lng": -76.6122,
        "median_home_price": 280000, "median_income": 55000, "mortgage_rate": 6.8,
        "rent_median": 1350, "yoy_price_change": 5.5, "months_inventory": 2.5,
        "days_on_market": 25, "unemployment": 4.8, "job_growth": 0.8,
        "gdp_growth": 1.8, "pop_growth": -0.5, "disaster_freq": 8,
        "flood_zone_pct": 7.0, "insurance_index": 100, "foreclosure_rate": 0.6,
        "cap_rate": 7.5, "price_appreciation_5yr": 38, "rent_growth": 3.5, "vacancy_rate": 7.0,
    },
    "Milwaukee": {
        "state": "WI", "lat": 43.0389, "lng": -87.9065,
        "median_home_price": 230000, "median_income": 52000, "mortgage_rate": 6.8,
        "rent_median": 1050, "yoy_price_change": 7.0, "months_inventory": 2.0,
        "days_on_market": 22, "unemployment": 3.5, "job_growth": 1.0,
        "gdp_growth": 1.8, "pop_growth": -0.2, "disaster_freq": 6,
        "flood_zone_pct": 5.0, "insurance_index": 95, "foreclosure_rate": 0.5,
        "cap_rate": 7.5, "price_appreciation_5yr": 52, "rent_growth": 5.0, "vacancy_rate": 5.5,
    },
    "Albuquerque": {
        "state": "NM", "lat": 35.0844, "lng": -106.6504,
        "median_home_price": 310000, "median_income": 55000, "mortgage_rate": 6.8,
        "rent_median": 1150, "yoy_price_change": 3.5, "months_inventory": 4.0,
        "days_on_market": 45, "unemployment": 4.2, "job_growth": 1.5,
        "gdp_growth": 2.0, "pop_growth": 0.3, "disaster_freq": 5,
        "flood_zone_pct": 2.0, "insurance_index": 85, "foreclosure_rate": 0.4,
        "cap_rate": 6.0, "price_appreciation_5yr": 42, "rent_growth": 3.5, "vacancy_rate": 6.5,
    },
    "Tucson": {
        "state": "AZ", "lat": 32.2226, "lng": -110.9747,
        "median_home_price": 320000, "median_income": 52000, "mortgage_rate": 6.8,
        "rent_median": 1200, "yoy_price_change": 3.0, "months_inventory": 4.5,
        "days_on_market": 48, "unemployment": 3.8, "job_growth": 2.0,
        "gdp_growth": 2.5, "pop_growth": 0.8, "disaster_freq": 5,
        "flood_zone_pct": 2.5, "insurance_index": 85, "foreclosure_rate": 0.3,
        "cap_rate": 6.0, "price_appreciation_5yr": 52, "rent_growth": 3.5, "vacancy_rate": 6.0,
    },
    "Raleigh": {
        "state": "NC", "lat": 35.7796, "lng": -78.6382,
        "median_home_price": 410000, "median_income": 78000, "mortgage_rate": 6.8,
        "rent_median": 1500, "yoy_price_change": 4.5, "months_inventory": 2.8,
        "days_on_market": 25, "unemployment": 2.8, "job_growth": 3.2,
        "gdp_growth": 3.8, "pop_growth": 2.0, "disaster_freq": 6,
        "flood_zone_pct": 4.0, "insurance_index": 95, "foreclosure_rate": 0.2,
        "cap_rate": 5.2, "price_appreciation_5yr": 48, "rent_growth": 4.0, "vacancy_rate": 4.5,
    },
}


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def _clamp(value, lo=0, hi=200):
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, int(round(value))))


def _score_affordability(d):
    """Score affordability (0-200). More affordable = higher score."""
    score_parts = []

    # Price-to-income ratio (ideal: 2.5-3.5, bad: >8)
    pti = d["median_home_price"] / max(d["median_income"], 1)
    if pti <= 2.5:
        s = 200
    elif pti >= 10:
        s = 10
    else:
        s = 200 - (pti - 2.5) * (190 / 7.5)
    score_parts.append(s)

    # Monthly mortgage payment as % of income
    # Monthly payment formula: P * r(1+r)^n / ((1+r)^n - 1)
    monthly_rate = d["mortgage_rate"] / 100 / 12
    n = 360  # 30 years
    principal = d["median_home_price"] * 0.8  # 20% down
    if monthly_rate > 0:
        payment = principal * monthly_rate * (1 + monthly_rate)**n / ((1 + monthly_rate)**n - 1)
    else:
        payment = principal / n
    pmt_pct = (payment * 12) / max(d["median_income"], 1) * 100
    if pmt_pct <= 20:
        s = 200
    elif pmt_pct >= 60:
        s = 10
    else:
        s = 200 - (pmt_pct - 20) * (190 / 40)
    score_parts.append(s)

    # Rent-to-income ratio (ideal: <25%, bad: >50%)
    rti = d["rent_median"] * 12 / max(d["median_income"], 1) * 100
    if rti <= 20:
        s = 200
    elif rti >= 50:
        s = 10
    else:
        s = 200 - (rti - 20) * (190 / 30)
    score_parts.append(s)

    return _clamp(sum(score_parts) / len(score_parts))


def _score_momentum(d):
    """Score market momentum (0-200). Healthy growth + low inventory = higher."""
    score_parts = []

    # YoY price change: ideal 3-6%, overheated >10%, declining <0%
    yoy = d["yoy_price_change"]
    if 3 <= yoy <= 6:
        s = 200
    elif yoy < 0:
        s = max(10, 80 + yoy * 20)
    elif yoy < 3:
        s = 80 + yoy * (120 / 3)
    else:  # > 6
        s = max(10, 200 - (yoy - 6) * 30)
    score_parts.append(s)

    # Months of inventory: ideal 2-4, too much >8, too little <1
    inv = d["months_inventory"]
    if 2 <= inv <= 4:
        s = 200
    elif inv < 1:
        s = 100
    elif inv < 2:
        s = 100 + (inv - 1) * 100
    else:  # > 4
        s = max(10, 200 - (inv - 4) * 35)
    score_parts.append(s)

    # Days on market: ideal <30, bad >90
    dom = d["days_on_market"]
    if dom <= 20:
        s = 200
    elif dom >= 90:
        s = 20
    else:
        s = 200 - (dom - 20) * (180 / 70)
    score_parts.append(s)

    return _clamp(sum(score_parts) / len(score_parts))


def _score_economic(d):
    """Score economic foundation (0-200). Strong economy = higher."""
    score_parts = []

    # Unemployment rate: ideal <3%, bad >8%
    unemp = d["unemployment"]
    if unemp <= 2.5:
        s = 200
    elif unemp >= 8:
        s = 10
    else:
        s = 200 - (unemp - 2.5) * (190 / 5.5)
    score_parts.append(s)

    # Job growth: ideal >2.5%, bad <-1%
    jg = d["job_growth"]
    if jg >= 3:
        s = 200
    elif jg <= -1:
        s = 10
    else:
        s = 10 + (jg + 1) * (190 / 4)
    score_parts.append(s)

    # GDP per capita growth: ideal >3%, bad <0%
    gdp = d["gdp_growth"]
    if gdp >= 4:
        s = 200
    elif gdp <= 0:
        s = 10
    else:
        s = 10 + gdp * (190 / 4)
    score_parts.append(s)

    # Population growth: ideal >1.5%, bad <-0.5%
    pg = d["pop_growth"]
    if pg >= 2:
        s = 200
    elif pg <= -0.5:
        s = 10
    else:
        s = 10 + (pg + 0.5) * (190 / 2.5)
    score_parts.append(s)

    return _clamp(sum(score_parts) / len(score_parts))


def _score_risk(d):
    """Score risk profile (0-200). LOWER risk = HIGHER score (inverse)."""
    score_parts = []

    # FEMA disaster frequency (5yr): ideal <5, bad >25
    df = d["disaster_freq"]
    if df <= 3:
        s = 200
    elif df >= 25:
        s = 10
    else:
        s = 200 - (df - 3) * (190 / 22)
    score_parts.append(s)

    # Flood zone %: ideal <2%, bad >15%
    fz = d["flood_zone_pct"]
    if fz <= 1:
        s = 200
    elif fz >= 15:
        s = 10
    else:
        s = 200 - (fz - 1) * (190 / 14)
    score_parts.append(s)

    # Insurance cost index: ideal <80, bad >180
    ins = d["insurance_index"]
    if ins <= 80:
        s = 200
    elif ins >= 180:
        s = 10
    else:
        s = 200 - (ins - 80) * (190 / 100)
    score_parts.append(s)

    # Foreclosure rate: ideal <0.2%, bad >1%
    fc = d["foreclosure_rate"]
    if fc <= 0.1:
        s = 200
    elif fc >= 1.0:
        s = 10
    else:
        s = 200 - (fc - 0.1) * (190 / 0.9)
    score_parts.append(s)

    return _clamp(sum(score_parts) / len(score_parts))


def _score_investment(d):
    """Score investment return (0-200). Better returns = higher."""
    score_parts = []

    # Cap rate: ideal >7%, bad <3%
    cr = d["cap_rate"]
    if cr >= 8:
        s = 200
    elif cr <= 3:
        s = 10
    else:
        s = 10 + (cr - 3) * (190 / 5)
    score_parts.append(s)

    # 5-year price appreciation: ideal >50%, bad <10%
    pa = d["price_appreciation_5yr"]
    if pa >= 60:
        s = 200
    elif pa <= 10:
        s = 10
    else:
        s = 10 + (pa - 10) * (190 / 50)
    score_parts.append(s)

    # Rent growth: ideal >5%, bad <0%
    rg = d["rent_growth"]
    if rg >= 6:
        s = 200
    elif rg <= 0:
        s = 10
    else:
        s = 10 + rg * (190 / 6)
    score_parts.append(s)

    # Vacancy rate (inverse): ideal <3%, bad >10%
    vr = d["vacancy_rate"]
    if vr <= 3:
        s = 200
    elif vr >= 10:
        s = 10
    else:
        s = 200 - (vr - 3) * (190 / 7)
    score_parts.append(s)

    return _clamp(sum(score_parts) / len(score_parts))


def score_market(market_data):
    """Score a single market (state or metro).
    Returns dict with axis scores (each 0-200) and total (0-1000).
    Uses proportional scaling if any axis returns None.
    """
    axes_funcs = [
        ("Affordability", _score_affordability),
        ("Market Momentum", _score_momentum),
        ("Economic Foundation", _score_economic),
        ("Risk Profile", _score_risk),
        ("Investment Return", _score_investment),
    ]

    axes = {}
    available_count = 0
    available_sum = 0

    for label, func in axes_funcs:
        try:
            val = func(market_data)
            axes[label] = val
            available_count += 1
            available_sum += val
        except Exception:
            axes[label] = None

    # Proportional scaling for missing data
    if available_count == 0:
        return None

    for label in axes:
        if axes[label] is None:
            axes[label] = int(round(available_sum / available_count))

    total = sum(axes.values())

    return {
        "axes": axes,
        "total": total,
    }


def load_state_data():
    """Load and score all states. Returns list of dicts."""
    results = []
    for fips, info in STATE_FIPS.items():
        abbr = info["abbr"]
        if abbr not in STATES_DATA:
            continue
        d = STATES_DATA[abbr]
        scored = score_market(d)
        if scored is None:
            continue
        results.append({
            "fips": fips,
            "name": info["name"],
            "abbr": abbr,
            "total": scored["total"],
            "axes": scored["axes"],
            "data": d,
        })
    return results


def load_metro_data():
    """Load and score all metro areas. Returns list of dicts."""
    results = []
    for name, d in METRO_DATA.items():
        scored = score_market(d)
        if scored is None:
            continue
        results.append({
            "name": name,
            "state": d["state"],
            "lat": d["lat"],
            "lng": d["lng"],
            "total": scored["total"],
            "axes": scored["axes"],
            "data": d,
        })
    return results


def get_state_rankings():
    """Return states sorted by total score (descending)."""
    data = load_state_data()
    data.sort(key=lambda x: x["total"], reverse=True)
    return data


def get_metro_rankings():
    """Return metros sorted by total score (descending)."""
    data = load_metro_data()
    data.sort(key=lambda x: x["total"], reverse=True)
    return data
