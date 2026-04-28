#!/usr/bin/env python3
"""
Vedic chart computation helper for The Honest Astrologer skill.

Computes planetary positions, house placements, and Vimshottari Dasha periods
using Swiss Ephemeris with Lahiri ayanamsa (sidereal) and whole-sign houses.

Usage:
    python compute_chart.py --date 1987-02-09 --time 21:00 --lat 22.75 --lon 72.68 --tz 5.5

Requires:
    pip install pyswisseph
"""

import argparse
import json
from datetime import datetime, timedelta

try:
    import swisseph as swe
except ImportError:
    print("Missing dependency. Install with: pip install pyswisseph")
    raise SystemExit(1)


SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
              "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
              "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
              "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]

NAK_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"] * 3

DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]


def sign_of(longitude: float) -> tuple[int, float]:
    """Return (sign_index, degrees_in_sign)."""
    longitude = longitude % 360
    return int(longitude // 30), longitude % 30


def nakshatra_of(longitude: float) -> tuple[int, int]:
    """Return (nakshatra_index, pada)."""
    longitude = longitude % 360
    nak_idx = int(longitude // (360 / 27))
    pada = int((longitude % (360 / 27)) // (360 / 108)) + 1
    return nak_idx, pada


def compute_chart(date_str: str, time_str: str, lat: float, lon: float, tz_offset: float) -> dict:
    """Compute a Vedic chart with Lahiri ayanamsa and whole-sign houses."""
    birth_local = datetime.fromisoformat(f"{date_str}T{time_str}")
    birth_utc = birth_local - timedelta(hours=tz_offset)
    jd = swe.julday(birth_utc.year, birth_utc.month, birth_utc.day,
                    birth_utc.hour + birth_utc.minute / 60 + birth_utc.second / 3600)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    sid_flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
        "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }

    positions = {}
    for name, pid in planets.items():
        result, _ = swe.calc_ut(jd, pid, sid_flag)
        lon_p, speed = result[0], result[3]
        si, deg = sign_of(lon_p)
        nk, pd = nakshatra_of(lon_p)
        positions[name] = {
            "longitude": lon_p, "sign": SIGNS[si], "degree": round(deg, 2),
            "nakshatra": NAKSHATRAS[nk], "pada": pd,
            "retrograde": speed < 0 and name not in ("Sun", "Moon", "Rahu")
        }

    # Ketu = Rahu + 180
    ketu_lon = (positions["Rahu"]["longitude"] + 180) % 360
    si, deg = sign_of(ketu_lon)
    nk, pd = nakshatra_of(ketu_lon)
    positions["Ketu"] = {
        "longitude": ketu_lon, "sign": SIGNS[si], "degree": round(deg, 2),
        "nakshatra": NAKSHATRAS[nk], "pada": pd, "retrograde": False
    }

    # Ascendant
    _, ascmc = swe.houses_ex(jd, lat, lon, b'P', sid_flag)
    asc_lon = ascmc[0]
    asc_si, asc_deg = sign_of(asc_lon)
    asc_nk, asc_pd = nakshatra_of(asc_lon)

    # Whole-sign houses
    for name, p in positions.items():
        planet_si = SIGNS.index(p["sign"])
        p["house"] = ((planet_si - asc_si) % 12) + 1

    # Vimshottari Dasha
    moon_lon = positions["Moon"]["longitude"]
    moon_nak_idx = int(moon_lon // (360 / 27))
    moon_lord = NAK_LORDS[moon_nak_idx]
    frac_done = (moon_lon % (360 / 27)) / (360 / 27)
    balance_years = DASHA_YEARS[moon_lord] * (1 - frac_done)

    start_idx = DASHA_ORDER.index(moon_lord)
    cur = birth_local
    sequence = []
    end = cur + timedelta(days=balance_years * 365.2425)
    sequence.append({"lord": moon_lord, "start": cur.date().isoformat(), "end": end.date().isoformat()})
    cur = end
    for i in range(1, 9):
        lord = DASHA_ORDER[(start_idx + i) % 9]
        end = cur + timedelta(days=DASHA_YEARS[lord] * 365.2425)
        sequence.append({"lord": lord, "start": cur.date().isoformat(), "end": end.date().isoformat()})
        cur = end

    today = datetime.now()
    current_md = next((md for md in sequence
                       if datetime.fromisoformat(md["start"]) <= today
                       <= datetime.fromisoformat(md["end"])), None)

    # House lords
    house_lords = []
    for h in range(1, 13):
        si = (asc_si + h - 1) % 12
        lord = SIGN_LORDS[si]
        house_lords.append({
            "house": h, "sign": SIGNS[si], "lord": lord,
            "lord_in_house": positions[lord]["house"],
            "lord_in_sign": positions[lord]["sign"]
        })

    return {
        "ascendant": {"sign": SIGNS[asc_si], "degree": round(asc_deg, 2),
                      "nakshatra": NAKSHATRAS[asc_nk], "pada": asc_pd},
        "moon_sign": positions["Moon"]["sign"],
        "sun_sign": positions["Sun"]["sign"],
        "planets": positions,
        "house_lords": house_lords,
        "dasha_sequence": sequence,
        "current_mahadasha": current_md,
    }


def main():
    p = argparse.ArgumentParser(description="Compute a Vedic chart (Parashara/Lahiri).")
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument("--time", required=True, help="HH:MM (24-hour, local time)")
    p.add_argument("--lat", type=float, required=True, help="Latitude (decimal)")
    p.add_argument("--lon", type=float, required=True, help="Longitude (decimal)")
    p.add_argument("--tz", type=float, required=True, help="Timezone offset from UTC (e.g. 5.5 for IST)")
    args = p.parse_args()

    chart = compute_chart(args.date, args.time, args.lat, args.lon, args.tz)
    print(json.dumps(chart, indent=2, default=str))


if __name__ == "__main__":
    main()
