# data_logic.py
"""REALESTATE-1000 scoring logic with REAL API data for all 50 US states + DC."""

try:
    import streamlit as st
except ImportError:
    import types as _types
    st = _types.ModuleType("streamlit")
    st.cache_data = lambda **kwargs: (lambda fn: fn)
    st.secrets = {}

import pandas as pd
import numpy as np
import requests
import gzip
import io
import json
import os
import time

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

# Reverse lookup: abbreviation -> FIPS code
_ABBR_TO_FIPS = {v["abbr"]: k for k, v in STATE_FIPS.items()}

# Census state FIPS -> abbreviation mapping
_FIPS_TO_ABBR = {k: v["abbr"] for k, v in STATE_FIPS.items()}

# Redfin uses full state names; map name -> abbreviation
_NAME_TO_ABBR = {v["name"]: v["abbr"] for v in STATE_FIPS.values()}

AXES_LABELS = [
    "Affordability",
    "Market Momentum",
    "Economic Foundation",
    "Risk Profile",
    "Investment Return",
]

AXES_DESCRIPTIONS = {
    "Affordability": "Home price-to-income ratio, mortgage burden, rent-to-income ratio. More affordable = higher score.",
    "Market Momentum": "YoY price appreciation, months of inventory, days on market, sale-to-list ratio. Healthy growth = higher score.",
    "Economic Foundation": "Unemployment rate, population growth, GDP growth (if available). Stronger economy = higher score.",
    "Risk Profile": "FEMA disaster frequency (5yr). Lower risk = higher score (inverse scoring).",
    "Investment Return": "Rental yield, 5-year price appreciation. Higher returns = higher score.",
}

# Metro area definitions with coordinates and parent state
METRO_AREAS = {
    "New York, NY": {"state": "NY", "lat": 40.7128, "lng": -74.0060, "redfin_name": "New York"},
    "Los Angeles, CA": {"state": "CA", "lat": 34.0522, "lng": -118.2437, "redfin_name": "Los Angeles"},
    "Chicago, IL": {"state": "IL", "lat": 41.8781, "lng": -87.6298, "redfin_name": "Chicago"},
    "Houston, TX": {"state": "TX", "lat": 29.7604, "lng": -95.3698, "redfin_name": "Houston"},
    "Phoenix, AZ": {"state": "AZ", "lat": 33.4484, "lng": -112.0740, "redfin_name": "Phoenix"},
    "Philadelphia, PA": {"state": "PA", "lat": 39.9526, "lng": -75.1652, "redfin_name": "Philadelphia"},
    "San Antonio, TX": {"state": "TX", "lat": 29.4241, "lng": -98.4936, "redfin_name": "San Antonio"},
    "San Diego, CA": {"state": "CA", "lat": 32.7157, "lng": -117.1611, "redfin_name": "San Diego"},
    "Dallas, TX": {"state": "TX", "lat": 32.7767, "lng": -96.7970, "redfin_name": "Dallas"},
    "Austin, TX": {"state": "TX", "lat": 30.2672, "lng": -97.7431, "redfin_name": "Austin"},
    "Jacksonville, FL": {"state": "FL", "lat": 30.3322, "lng": -81.6557, "redfin_name": "Jacksonville"},
    "San Francisco, CA": {"state": "CA", "lat": 37.7749, "lng": -122.4194, "redfin_name": "San Francisco"},
    "Columbus, OH": {"state": "OH", "lat": 39.9612, "lng": -82.9988, "redfin_name": "Columbus"},
    "Charlotte, NC": {"state": "NC", "lat": 35.2271, "lng": -80.8431, "redfin_name": "Charlotte"},
    "Indianapolis, IN": {"state": "IN", "lat": 39.7684, "lng": -86.1581, "redfin_name": "Indianapolis"},
    "Seattle, WA": {"state": "WA", "lat": 47.6062, "lng": -122.3321, "redfin_name": "Seattle"},
    "Denver, CO": {"state": "CO", "lat": 39.7392, "lng": -104.9903, "redfin_name": "Denver"},
    "Nashville, TN": {"state": "TN", "lat": 36.1627, "lng": -86.7816, "redfin_name": "Nashville"},
    "Atlanta, GA": {"state": "GA", "lat": 33.7490, "lng": -84.3880, "redfin_name": "Atlanta"},
    "Portland, OR": {"state": "OR", "lat": 45.5152, "lng": -122.6784, "redfin_name": "Portland"},
    "Las Vegas, NV": {"state": "NV", "lat": 36.1699, "lng": -115.1398, "redfin_name": "Las Vegas"},
    "Miami, FL": {"state": "FL", "lat": 25.7617, "lng": -80.1918, "redfin_name": "Miami"},
    "Tampa, FL": {"state": "FL", "lat": 27.9506, "lng": -82.4572, "redfin_name": "Tampa"},
    "Raleigh, NC": {"state": "NC", "lat": 35.7796, "lng": -78.6382, "redfin_name": "Raleigh"},
    "Minneapolis, MN": {"state": "MN", "lat": 44.9778, "lng": -93.2650, "redfin_name": "Minneapolis"},
    "Salt Lake City, UT": {"state": "UT", "lat": 40.7608, "lng": -111.8910, "redfin_name": "Salt Lake City"},
    "Detroit, MI": {"state": "MI", "lat": 42.3314, "lng": -83.0458, "redfin_name": "Detroit"},
    "Boston, MA": {"state": "MA", "lat": 42.3601, "lng": -71.0589, "redfin_name": "Boston"},
    "Pittsburgh, PA": {"state": "PA", "lat": 40.4406, "lng": -79.9959, "redfin_name": "Pittsburgh"},
    "Baltimore, MD": {"state": "MD", "lat": 39.2904, "lng": -76.6122, "redfin_name": "Baltimore"},
}


# ===========================================================================
# Data Fetch Functions (all real API calls, cached 24 hours)
# ===========================================================================

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_census_data():
    """Fetch median income, home value, rent, and population from Census ACS.

    Returns dict keyed by state abbreviation with census metrics.
    Fetches both 2023 and 2021 data for population change calculation.
    """
    result = {}

    # Fetch 2023 data (latest ACS 1-year)
    url_2023 = (
        "https://api.census.gov/data/2023/acs/acs1"
        "?get=NAME,B19013_001E,B25077_001E,B25064_001E,B01003_001E"
        "&for=state:*"
    )
    # Fetch 2021 data for population change
    url_2021 = (
        "https://api.census.gov/data/2021/acs/acs1"
        "?get=NAME,B01003_001E"
        "&for=state:*"
    )

    try:
        resp_2023 = requests.get(url_2023, timeout=30)
        resp_2023.raise_for_status()
        data_2023 = resp_2023.json()
    except Exception as e:
        print(f"[REALESTATE-1000] Census 2023 API failed: {e}")
        return result

    # Parse 2021 population for YoY comparison
    pop_2021 = {}
    try:
        resp_2021 = requests.get(url_2021, timeout=30)
        resp_2021.raise_for_status()
        data_2021 = resp_2021.json()
        for row in data_2021[1:]:
            fips = row[-1]  # state FIPS
            if fips in _FIPS_TO_ABBR:
                try:
                    pop_2021[_FIPS_TO_ABBR[fips]] = int(row[1])
                except (ValueError, TypeError):
                    pass
    except Exception as e:
        print(f"[REALESTATE-1000] Census 2021 API failed: {e}")

    # Parse 2023 data
    # Header: NAME, B19013_001E, B25077_001E, B25064_001E, B01003_001E, state
    for row in data_2023[1:]:
        fips = row[-1]  # state FIPS code
        if fips not in _FIPS_TO_ABBR:
            continue
        abbr = _FIPS_TO_ABBR[fips]

        try:
            median_income = int(row[1]) if row[1] else None
            median_home_value = int(row[2]) if row[2] else None
            median_rent = int(row[3]) if row[3] else None
            population = int(row[4]) if row[4] else None
        except (ValueError, TypeError):
            continue

        pop_change = None
        if population and abbr in pop_2021 and pop_2021[abbr] > 0:
            pop_change = round(
                (population - pop_2021[abbr]) / pop_2021[abbr] * 100, 2
            )

        result[abbr] = {
            "median_income": median_income,
            "median_home_value": median_home_value,
            "median_rent": median_rent,
            "population": population,
            "pop_growth": pop_change,
        }

    return result


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_bls_unemployment():
    """Fetch state unemployment rates from BLS API.

    Returns dict keyed by state abbreviation with unemployment rate.
    BLS limits to 25 series per request, so we use 3 batches.
    """
    result = {}
    all_fips = list(STATE_FIPS.keys())

    # Build series IDs: LASST{FIPS}0000000000003
    series_map = {}
    for fips in all_fips:
        series_id = f"LASST{fips}0000000000003"
        series_map[series_id] = _FIPS_TO_ABBR[fips]

    series_list = list(series_map.keys())

    # Split into batches of 25
    batches = []
    for i in range(0, len(series_list), 25):
        batches.append(series_list[i:i + 25])

    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    for batch in batches:
        payload = {
            "seriesid": batch,
            "startyear": "2024",
            "endyear": "2026",
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "REQUEST_SUCCEEDED":
                print(f"[REALESTATE-1000] BLS batch warning: {data.get('message', '')}")

            for series in data.get("Results", {}).get("series", []):
                series_id = series["seriesID"]
                abbr = series_map.get(series_id)
                if not abbr:
                    continue

                # Get the latest data point
                series_data = series.get("data", [])
                if series_data:
                    # Data is sorted latest first
                    latest = series_data[0]
                    try:
                        result[abbr] = float(latest["value"])
                    except (ValueError, KeyError):
                        pass

        except Exception as e:
            print(f"[REALESTATE-1000] BLS batch failed: {e}")

        # Small delay between batches to be polite
        time.sleep(1)

    return result


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_redfin_data():
    """Fetch Redfin state-level market data from public S3 bucket.

    Returns dict keyed by state abbreviation with market metrics.
    Includes: median_sale_price, yoy_price_change, months_of_supply,
              days_on_market, sale_to_list_ratio, homes_sold, price_drops,
              inventory, price_5yr_ago.
    """
    result = {}
    url = "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/state_market_tracker.tsv000.gz"

    try:
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()

        # Decompress gzip
        buf = io.BytesIO(resp.content)
        with gzip.open(buf, "rt") as f:
            df = pd.read_csv(f, sep="\t", low_memory=False)

    except Exception as e:
        print(f"[REALESTATE-1000] Redfin download failed: {e}")
        return result

    # Filter for All Residential property type
    if "property_type" in df.columns:
        df = df[df["property_type"] == "All Residential"].copy()

    # Ensure period_begin is datetime
    if "period_begin" in df.columns:
        df["period_begin"] = pd.to_datetime(df["period_begin"], errors="coerce")

    # Get the latest period
    latest_period = df["period_begin"].max()
    df_latest = df[df["period_begin"] == latest_period].copy()

    # Also get data from ~5 years ago for appreciation calculation
    target_5yr = latest_period - pd.DateOffset(years=5)
    # Find closest period to 5yr ago
    all_periods = df["period_begin"].dropna().unique()
    if len(all_periods) > 0:
        diffs = [abs((pd.Timestamp(p) - target_5yr).days) for p in all_periods]
        closest_5yr_period = all_periods[np.argmin(diffs)]
        df_5yr = df[df["period_begin"] == closest_5yr_period].copy()
    else:
        df_5yr = pd.DataFrame()

    # Build 5yr price lookup by state
    price_5yr_ago = {}
    if not df_5yr.empty and "state" in df_5yr.columns:
        for _, row in df_5yr.iterrows():
            state_name = str(row.get("state", "")).strip()
            try:
                price_5yr_ago[state_name] = float(row["median_sale_price"])
            except (ValueError, TypeError, KeyError):
                pass

    # Parse latest data
    for _, row in df_latest.iterrows():
        state_name = str(row.get("state", "")).strip()
        abbr = _NAME_TO_ABBR.get(state_name)
        if not abbr:
            # Try case-insensitive match
            for n, a in _NAME_TO_ABBR.items():
                if n.lower() == state_name.lower():
                    abbr = a
                    break
        if not abbr:
            continue

        def safe_float(val):
            try:
                v = float(val)
                return v if not np.isnan(v) else None
            except (ValueError, TypeError):
                return None

        median_sale_price = safe_float(row.get("median_sale_price"))
        yoy_price = safe_float(row.get("median_sale_price_yoy"))
        if yoy_price is not None:
            yoy_price = round(yoy_price * 100, 2)  # Convert to percentage

        months_supply = safe_float(row.get("months_of_supply"))
        dom = safe_float(row.get("median_dom"))
        sale_to_list = safe_float(row.get("avg_sale_to_list"))
        homes_sold = safe_float(row.get("homes_sold"))
        price_drops_pct = safe_float(row.get("price_drops"))
        if price_drops_pct is not None:
            price_drops_pct = round(price_drops_pct * 100, 2)
        inventory = safe_float(row.get("inventory"))

        # 5yr appreciation
        appreciation_5yr = None
        old_price = price_5yr_ago.get(state_name)
        if median_sale_price and old_price and old_price > 0:
            appreciation_5yr = round(
                (median_sale_price - old_price) / old_price * 100, 1
            )

        result[abbr] = {
            "median_sale_price": median_sale_price,
            "yoy_price_change": yoy_price,
            "months_of_supply": months_supply,
            "days_on_market": dom,
            "sale_to_list_ratio": sale_to_list,
            "homes_sold": homes_sold,
            "price_drops_pct": price_drops_pct,
            "inventory": inventory,
            "price_appreciation_5yr": appreciation_5yr,
        }

    return result


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_fema_disasters():
    """Fetch FEMA disaster counts per state (last 5 years, excluding Biological).

    Returns dict keyed by state abbreviation with disaster count.
    """
    result = {}
    url = (
        "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
        "?$filter=declarationDate gt '2021-01-01T00:00:00.000Z' and incidentType ne 'Biological'"
        "&$select=state,incidentType,disasterNumber"
        "&$top=10000"
    )

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        records = data.get("DisasterDeclarationsSummaries", [])

        # Count unique disaster numbers per state
        state_disasters = {}
        for rec in records:
            st_abbr = rec.get("state", "")
            disaster_num = rec.get("disasterNumber")
            if st_abbr and disaster_num is not None:
                if st_abbr not in state_disasters:
                    state_disasters[st_abbr] = set()
                state_disasters[st_abbr].add(disaster_num)

        for abbr, disasters in state_disasters.items():
            result[abbr] = len(disasters)

    except Exception as e:
        print(f"[REALESTATE-1000] FEMA API failed: {e}")

    return result


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_mortgage_rate():
    """Fetch current 30-year fixed mortgage rate from Freddie Mac.

    Returns float (e.g. 6.85) or None.
    """
    url = "https://www.freddiemac.com/pmms/docs/PMMS_history.csv"

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()

        df = pd.read_csv(io.StringIO(resp.text))

        # The CSV has columns like: Date, 30yr FRM, ...
        # Find the 30-year column
        col_30yr = None
        for col in df.columns:
            if "30" in str(col).lower():
                col_30yr = col
                break

        if col_30yr is None:
            # Fallback: use second column
            col_30yr = df.columns[1] if len(df.columns) > 1 else None

        if col_30yr:
            # Get last valid value
            values = pd.to_numeric(df[col_30yr], errors="coerce").dropna()
            if len(values) > 0:
                rate = float(values.iloc[-1])
                if 2.0 < rate < 15.0:  # sanity check
                    return round(rate, 2)

    except Exception as e:
        print(f"[REALESTATE-1000] Freddie Mac API failed: {e}")

    return None


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_bea_gdp():
    """Fetch state GDP data from BEA API. Requires BEA_API_KEY in secrets.

    Returns dict keyed by state abbreviation with gdp_growth (%).
    Returns empty dict if API key not available.
    """
    result = {}

    # Try to get API key
    bea_key = None
    try:
        bea_key = st.secrets.get("BEA_API_KEY")
    except Exception:
        pass
    if not bea_key:
        bea_key = os.environ.get("BEA_API_KEY")
    if not bea_key:
        return result

    url = (
        f"https://apps.bea.gov/api/data/"
        f"?&UserID={bea_key}"
        f"&method=GetData&DataSetName=Regional"
        f"&TableName=SQGDP1&LineCode=1&GeoFips=STATE"
        f"&Year=LAST5&ResultFormat=json"
    )

    # BEA state FIPS names don't use abbreviations; we need a mapping
    # BEA uses GeoName like "Alabama", "Alaska", etc.
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        bea_data = data.get("BEAAPI", {}).get("Results", {}).get("Data", [])
        if not bea_data:
            return result

        # Group by state, sort by year to get growth
        state_gdp = {}
        for rec in bea_data:
            geo_name = rec.get("GeoName", "")
            year = rec.get("TimePeriod", "")
            val = rec.get("DataValue", "")

            abbr = _NAME_TO_ABBR.get(geo_name)
            if not abbr:
                continue

            try:
                gdp_val = float(str(val).replace(",", ""))
            except (ValueError, TypeError):
                continue

            if abbr not in state_gdp:
                state_gdp[abbr] = {}
            state_gdp[abbr][year] = gdp_val

        # Calculate growth from latest 2 years
        for abbr, yearly in state_gdp.items():
            years = sorted(yearly.keys())
            if len(years) >= 2:
                latest = yearly[years[-1]]
                prev = yearly[years[-2]]
                if prev > 0:
                    growth = round((latest - prev) / prev * 100, 2)
                    result[abbr] = growth

    except Exception as e:
        print(f"[REALESTATE-1000] BEA API failed: {e}")

    return result


# ===========================================================================
# Data Merging
# ===========================================================================

@st.cache_data(ttl=86400, show_spinner=False)
def load_all_data():
    """Fetch all data sources and merge into a unified state-level dataset.

    Returns dict keyed by state abbreviation, each containing all available
    metrics for scoring and display.
    """
    census = fetch_census_data()
    unemployment = fetch_bls_unemployment()
    redfin = fetch_redfin_data()
    fema = fetch_fema_disasters()
    mortgage = fetch_mortgage_rate()
    bea = fetch_bea_gdp()

    # Default mortgage rate if fetch failed
    if mortgage is None:
        mortgage = 6.5  # reasonable fallback

    merged = {}
    for fips, info in STATE_FIPS.items():
        abbr = info["abbr"]
        name = info["name"]

        d = {"abbr": abbr, "name": name, "fips": fips}

        # Census data
        c = census.get(abbr, {})
        d["median_income"] = c.get("median_income")
        d["median_home_value"] = c.get("median_home_value")
        d["median_rent"] = c.get("median_rent")
        d["population"] = c.get("population")
        d["pop_growth"] = c.get("pop_growth")

        # BLS unemployment
        d["unemployment"] = unemployment.get(abbr)

        # Redfin market data
        r = redfin.get(abbr, {})
        d["median_sale_price"] = r.get("median_sale_price")
        d["yoy_price_change"] = r.get("yoy_price_change")
        d["months_of_supply"] = r.get("months_of_supply")
        d["days_on_market"] = r.get("days_on_market")
        d["sale_to_list_ratio"] = r.get("sale_to_list_ratio")
        d["homes_sold"] = r.get("homes_sold")
        d["price_drops_pct"] = r.get("price_drops_pct")
        d["inventory"] = r.get("inventory")
        d["price_appreciation_5yr"] = r.get("price_appreciation_5yr")

        # Use Redfin sale price as primary, Census home value as fallback
        d["median_home_price"] = d["median_sale_price"] or d["median_home_value"]

        # FEMA disasters
        d["disaster_freq"] = fema.get(abbr, 0)

        # Mortgage rate (national)
        d["mortgage_rate"] = mortgage

        # BEA GDP growth (optional)
        d["gdp_growth"] = bea.get(abbr)

        # Derived metrics
        # Rental yield (cap rate proxy)
        if d["median_rent"] and d["median_home_price"] and d["median_home_price"] > 0:
            d["cap_rate"] = round(
                (d["median_rent"] * 12) / d["median_home_price"] * 100, 2
            )
        else:
            d["cap_rate"] = None

        # Rent-to-income ratio
        if d["median_rent"] and d["median_income"] and d["median_income"] > 0:
            d["rent_to_income"] = round(
                (d["median_rent"] * 12) / d["median_income"] * 100, 1
            )
        else:
            d["rent_to_income"] = None

        # Price-to-income ratio
        if d["median_home_price"] and d["median_income"] and d["median_income"] > 0:
            d["price_to_income"] = round(
                d["median_home_price"] / d["median_income"], 2
            )
        else:
            d["price_to_income"] = None

        # Mortgage burden: monthly mortgage payment as % of monthly income
        if d["median_home_price"] and d["median_income"] and d["median_income"] > 0:
            monthly_rate = mortgage / 100 / 12
            principal = d["median_home_price"] * 0.8  # 20% down
            if monthly_rate > 0:
                n = 360
                payment = (
                    principal * monthly_rate * (1 + monthly_rate) ** n
                    / ((1 + monthly_rate) ** n - 1)
                )
            else:
                payment = principal / 360
            d["mortgage_burden"] = round(
                payment / (d["median_income"] / 12) * 100, 1
            )
        else:
            d["mortgage_burden"] = None

        # Display compatibility fields (for app.py detail view)
        d["rent_median"] = d["median_rent"]
        d["months_inventory"] = d["months_of_supply"]
        d["job_growth"] = d["gdp_growth"] if d["gdp_growth"] is not None else 0.0
        d["flood_zone_pct"] = 0.0  # Not available from free APIs
        d["insurance_index"] = 100  # Not available from free APIs
        d["foreclosure_rate"] = 0.0  # Not available from free APIs
        d["vacancy_rate"] = 0.0  # Not available from free APIs
        d["rent_growth"] = 0.0  # Not available from free APIs

        merged[abbr] = d

    return merged


# ===========================================================================
# Percentile-based Scoring Helpers
# ===========================================================================

def _percentile_score(value, all_values, invert=False):
    """Convert a value to a 0-200 score based on percentile rank among all values.

    Args:
        value: The value to score.
        all_values: List of all values (None values excluded).
        invert: If True, lower values get higher scores.

    Returns:
        Integer score 0-200, or None if value is None.
    """
    if value is None:
        return None

    valid = [v for v in all_values if v is not None]
    if len(valid) == 0:
        return None

    # Count how many values are below this one
    below = sum(1 for v in valid if v < value)
    equal = sum(1 for v in valid if v == value)
    # Percentile rank (0.0 to 1.0)
    percentile = (below + equal * 0.5) / len(valid)

    if invert:
        percentile = 1.0 - percentile

    return int(round(percentile * 200))


def _clamp(score):
    """Clamp score to 0-200 range."""
    if score is None:
        return None
    return max(0, min(200, int(round(score))))


def _band_score(value, ideal_low, ideal_high, bad_low, bad_high):
    """Score where a middle range is ideal (e.g. months of supply 4-6).

    Returns 0-200 where ideal range = 200, outside bad range = 0.
    """
    if value is None:
        return None

    if ideal_low <= value <= ideal_high:
        return 200

    if value < ideal_low:
        if value <= bad_low:
            return 0
        return int(round(200 * (value - bad_low) / (ideal_low - bad_low)))
    else:
        if value >= bad_high:
            return 0
        return int(round(200 * (bad_high - value) / (bad_high - ideal_high)))


# ===========================================================================
# Axis Scoring Functions
# ===========================================================================

def score_affordability(state_data, all_states):
    """Score Affordability axis (0-200). More affordable = higher score.

    Uses: price_to_income, mortgage_burden, rent_to_income.
    All scored via inverse percentile (lower ratio = more affordable = higher score).
    """
    parts = []

    # Price to income ratio (lower = more affordable)
    pti = state_data.get("price_to_income")
    all_pti = [s.get("price_to_income") for s in all_states.values()]
    s = _percentile_score(pti, all_pti, invert=True)
    if s is not None:
        parts.append(s)

    # Mortgage burden (lower = more affordable)
    mb = state_data.get("mortgage_burden")
    all_mb = [s.get("mortgage_burden") for s in all_states.values()]
    s = _percentile_score(mb, all_mb, invert=True)
    if s is not None:
        parts.append(s)

    # Rent to income (lower = more affordable)
    rti = state_data.get("rent_to_income")
    all_rti = [s.get("rent_to_income") for s in all_states.values()]
    s = _percentile_score(rti, all_rti, invert=True)
    if s is not None:
        parts.append(s)

    if not parts:
        return None
    return _clamp(sum(parts) / len(parts))


def score_momentum(state_data, all_states):
    """Score Market Momentum axis (0-200). Healthy market = higher score.

    Uses: yoy_price_change (moderate 3-8% ideal), months_of_supply (4-6 ideal),
          days_on_market (lower better), sale_to_list_ratio (higher better).
    """
    parts = []

    # YoY price change: moderate growth (3-8%) is best
    yoy = state_data.get("yoy_price_change")
    if yoy is not None:
        s = _band_score(yoy, 3.0, 8.0, -5.0, 20.0)
        if s is not None:
            parts.append(s)

    # Months of supply: 4-6 months is balanced
    mos = state_data.get("months_of_supply")
    if mos is not None:
        s = _band_score(mos, 4.0, 6.0, 0.5, 12.0)
        if s is not None:
            parts.append(s)

    # Days on market: lower = more demand = better
    dom = state_data.get("days_on_market")
    all_dom = [s.get("days_on_market") for s in all_states.values()]
    s = _percentile_score(dom, all_dom, invert=True)
    if s is not None:
        parts.append(s)

    # Sale to list ratio: higher = stronger market
    stl = state_data.get("sale_to_list_ratio")
    all_stl = [s.get("sale_to_list_ratio") for s in all_states.values()]
    s = _percentile_score(stl, all_stl, invert=False)
    if s is not None:
        parts.append(s)

    if not parts:
        return None
    return _clamp(sum(parts) / len(parts))


def score_economic(state_data, all_states):
    """Score Economic Foundation axis (0-200). Stronger economy = higher score.

    Uses: unemployment (lower better), pop_growth (higher better),
          gdp_growth (higher better, optional).
    """
    parts = []

    # Unemployment rate: lower = better (invert)
    ue = state_data.get("unemployment")
    all_ue = [s.get("unemployment") for s in all_states.values()]
    s = _percentile_score(ue, all_ue, invert=True)
    if s is not None:
        parts.append(s)

    # Population growth: higher = better
    pg = state_data.get("pop_growth")
    all_pg = [s.get("pop_growth") for s in all_states.values()]
    s = _percentile_score(pg, all_pg, invert=False)
    if s is not None:
        parts.append(s)

    # GDP growth (optional): higher = better
    gdp = state_data.get("gdp_growth")
    all_gdp = [s.get("gdp_growth") for s in all_states.values()]
    if gdp is not None and any(v is not None for v in all_gdp):
        s = _percentile_score(gdp, all_gdp, invert=False)
        if s is not None:
            parts.append(s)

    if not parts:
        return None
    return _clamp(sum(parts) / len(parts))


def score_risk(state_data, all_states):
    """Score Risk Profile axis (0-200). Lower risk = higher score (INVERSE).

    Uses: disaster_freq (fewer FEMA disasters = higher score).
    """
    parts = []

    # FEMA disaster count: fewer = lower risk = higher score (invert)
    df = state_data.get("disaster_freq")
    all_df = [s.get("disaster_freq") for s in all_states.values()]
    s = _percentile_score(df, all_df, invert=True)
    if s is not None:
        parts.append(s)

    if not parts:
        return None
    return _clamp(sum(parts) / len(parts))


def score_investment(state_data, all_states):
    """Score Investment Return axis (0-200). Higher returns = higher score.

    Uses: cap_rate/rental_yield (higher better), price_appreciation_5yr (higher better).
    """
    parts = []

    # Rental yield / cap rate: higher = better
    cr = state_data.get("cap_rate")
    all_cr = [s.get("cap_rate") for s in all_states.values()]
    s = _percentile_score(cr, all_cr, invert=False)
    if s is not None:
        parts.append(s)

    # 5-year appreciation: higher = better
    pa = state_data.get("price_appreciation_5yr")
    all_pa = [s.get("price_appreciation_5yr") for s in all_states.values()]
    s = _percentile_score(pa, all_pa, invert=False)
    if s is not None:
        parts.append(s)

    if not parts:
        return None
    return _clamp(sum(parts) / len(parts))


# ===========================================================================
# Score a single market
# ===========================================================================

def score_market(state_data, all_states):
    """Score a single state/market. Returns dict with axis scores and total.

    Uses proportional scaling if any axis returns None.
    """
    axes_funcs = [
        ("Affordability", score_affordability),
        ("Market Momentum", score_momentum),
        ("Economic Foundation", score_economic),
        ("Risk Profile", score_risk),
        ("Investment Return", score_investment),
    ]

    axes = {}
    available_count = 0
    available_sum = 0

    for label, func in axes_funcs:
        try:
            val = func(state_data, all_states)
            axes[label] = val
            if val is not None:
                available_count += 1
                available_sum += val
        except Exception:
            axes[label] = None

    if available_count == 0:
        return None

    # Proportional scaling: fill missing axes with the average of available ones
    avg_available = int(round(available_sum / available_count))
    for label in axes:
        if axes[label] is None:
            axes[label] = avg_available

    total = sum(axes.values())

    return {
        "axes": axes,
        "total": total,
    }


# ===========================================================================
# Public API: get_state_rankings and get_metro_rankings
# ===========================================================================

def get_state_rankings():
    """Return all states sorted by total score (descending).

    Each entry is a dict with: fips, name, abbr, total, axes, data.
    """
    all_states = load_all_data()

    results = []
    for abbr, d in all_states.items():
        scored = score_market(d, all_states)
        if scored is None:
            continue
        results.append({
            "fips": d["fips"],
            "name": d["name"],
            "abbr": abbr,
            "total": scored["total"],
            "axes": scored["axes"],
            "data": d,
        })

    results.sort(key=lambda x: x["total"], reverse=True)
    return results


def get_metro_rankings():
    """Return metro areas sorted by total score (descending).

    Metro areas inherit their parent state's economic and risk data,
    but would use metro-specific Redfin data if available. Currently
    uses the parent state data as a proxy for all metrics.

    Each entry is a dict with: name, state, lat, lng, total, axes, data.
    """
    all_states = load_all_data()

    results = []
    for metro_name, meta in METRO_AREAS.items():
        parent_abbr = meta["state"]
        if parent_abbr not in all_states:
            continue

        # Copy parent state data for the metro (state-level proxy)
        d = dict(all_states[parent_abbr])
        d["name"] = metro_name
        d["metro"] = True

        scored = score_market(d, all_states)
        if scored is None:
            continue

        results.append({
            "name": metro_name,
            "state": parent_abbr,
            "lat": meta["lat"],
            "lng": meta["lng"],
            "total": scored["total"],
            "axes": scored["axes"],
            "data": d,
        })

    results.sort(key=lambda x: x["total"], reverse=True)
    return results
