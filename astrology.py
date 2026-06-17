"""Vedic astrology calculation engine for premium life path reports.

This module is calculation-first. It uses Swiss Ephemeris when available and
does not fabricate unavailable systems such as Ashtakavarga.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import re

try:
    import swisseph as swe
    for _attr in ("SUN", "MOON", "julday", "calc_ut", "houses_ex", "SIDM_LAHIRI"):
        if not hasattr(swe, _attr):
            raise ImportError("installed swisseph package does not expose Swiss Ephemeris API")
except Exception:  # pragma: no cover - handled at runtime
    swe = None

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
SIGN_LORDS = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]
NAKSHATRAS = [
    ("Ashwini","Ketu"),("Bharani","Venus"),("Krittika","Sun"),("Rohini","Moon"),("Mrigashira","Mars"),
    ("Ardra","Rahu"),("Punarvasu","Jupiter"),("Pushya","Saturn"),("Ashlesha","Mercury"),
    ("Magha","Ketu"),("Purva Phalguni","Venus"),("Uttara Phalguni","Sun"),("Hasta","Moon"),
    ("Chitra","Mars"),("Swati","Rahu"),("Vishakha","Jupiter"),("Anuradha","Saturn"),
    ("Jyeshtha","Mercury"),("Mula","Ketu"),("Purva Ashadha","Venus"),("Uttara Ashadha","Sun"),
    ("Shravana","Moon"),("Dhanishta","Mars"),("Shatabhisha","Rahu"),("Purva Bhadrapada","Jupiter"),
    ("Uttara Bhadrapada","Saturn"),("Revati","Mercury"),
]
DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
PLANETS = {
    "Sun": swe.SUN if swe else 0, "Moon": swe.MOON if swe else 1, "Mars": swe.MARS if swe else 4,
    "Mercury": swe.MERCURY if swe else 2, "Jupiter": swe.JUPITER if swe else 5,
    "Venus": swe.VENUS if swe else 3, "Saturn": swe.SATURN if swe else 6,
    "Rahu": swe.MEAN_NODE if swe else 10,
}
EXALTATION = {"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6,"Rahu":1,"Ketu":7}
DEBILITATION = {"Sun":6,"Moon":7,"Mars":3,"Mercury":11,"Jupiter":9,"Venus":5,"Saturn":0,"Rahu":7,"Ketu":1}
OWN_SIGNS = {
    "Sun": {4}, "Moon": {3}, "Mars": {0,7}, "Mercury": {2,5}, "Jupiter": {8,11},
    "Venus": {1,6}, "Saturn": {9,10}, "Rahu": set(), "Ketu": set(),
}
FUNCTIONAL_NATURE = {"Jupiter":"benefic","Venus":"benefic","Mercury":"conditional benefic","Moon":"conditional benefic",
                     "Sun":"mild malefic","Mars":"malefic","Saturn":"malefic","Rahu":"shadow malefic","Ketu":"shadow malefic"}
PLANET_SEQUENCE = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
ASPECT_OFFSETS = {
    "Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7], "Rahu": [5,7,9], "Ketu": [5,7,9],
    "Mars": [4,7,8], "Jupiter": [5,7,9], "Saturn": [3,7,10],
}
PLACE_DB = {
    "bhopal": (23.2599, 77.4126, "Asia/Kolkata"),
    "bhopal, madhya pradesh, india": (23.2599, 77.4126, "Asia/Kolkata"),
    "delhi": (28.6139, 77.2090, "Asia/Kolkata"),
    "mumbai": (19.0760, 72.8777, "Asia/Kolkata"),
    "kolkata": (22.5726, 88.3639, "Asia/Kolkata"),
    "chennai": (13.0827, 80.2707, "Asia/Kolkata"),
    "bangalore": (12.9716, 77.5946, "Asia/Kolkata"),
    "bengaluru": (12.9716, 77.5946, "Asia/Kolkata"),
    "ahmedabad": (23.0225, 72.5714, "Asia/Kolkata"),
    "pune": (18.5204, 73.8567, "Asia/Kolkata"),
    "hyderabad": (17.3850, 78.4867, "Asia/Kolkata"),
    "jaipur": (26.9124, 75.7873, "Asia/Kolkata"),
    "lucknow": (26.8467, 80.9462, "Asia/Kolkata"),
    "indore": (22.7196, 75.8577, "Asia/Kolkata"),
    "patna": (25.5941, 85.1376, "Asia/Kolkata"),
    "chandigarh": (30.7333, 76.7794, "Asia/Kolkata"),
    "dehradun": (30.3165, 78.0322, "Asia/Kolkata"),
    "varanasi": (25.3176, 82.9739, "Asia/Kolkata"),
}

class AstrologyUnavailable(RuntimeError):
    pass

def _require_swe():
    if swe is None:
        raise AstrologyUnavailable("Swiss Ephemeris is not installed. Install pyswisseph to generate astrology reports.")
    for attr in ("set_sid_mode", "get_ayanamsa_ut", "calc_ut", "houses_ex", "julday", "SIDM_LAHIRI"):
        if not hasattr(swe, attr):
            raise AstrologyUnavailable("The installed swisseph module is not the real Swiss Ephemeris API.")

def norm360(x): return x % 360.0
def sign_index(lon): return int(norm360(lon) // 30)
def sign_name(lon): return SIGNS[sign_index(lon)]
def sign_degree(lon): return norm360(lon) % 30
def house_from(lon, asc_lon): return int(((sign_index(lon) - sign_index(asc_lon)) % 12) + 1)
def sign_from_house(asc_lon, house): return (sign_index(asc_lon) + house - 1) % 12

def parse_place(place: str):
    txt = (place or "").strip()
    key = txt.lower()
    if key in PLACE_DB:
        lat, lon, tz = PLACE_DB[key]
        return {"input": txt, "lat": lat, "lon": lon, "timezone": tz, "source": "built-in"}
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", txt)
    if len(nums) >= 2:
        lat, lon = float(nums[0]), float(nums[1])
        return {"input": txt, "lat": lat, "lon": lon, "timezone": resolve_timezone(lat, lon), "source": "lat-lon"}
    geo = geocode_place(txt)
    if geo:
        return geo
    raise ValueError("Birth place could not be resolved. Use a known city in the local database or provide latitude, longitude.")

def resolve_timezone(lat, lon):
    try:
        from timezonefinder import TimezoneFinder
        tz = TimezoneFinder().timezone_at(lat=lat, lng=lon)
        if tz:
            return tz
    except Exception:
        pass
    if 6 <= lat <= 38 and 68 <= lon <= 98:
        return "Asia/Kolkata"
    raise ValueError("Timezone could not be resolved for this birth place. Provide a known city or install timezonefinder.")

def geocode_place(txt):
    """Optional live geocoding; returns None if geopy/network is unavailable."""
    if not txt:
        return None
    try:
        from geopy.geocoders import Nominatim
        loc = Nominatim(user_agent="veshannastro_report_generator").geocode(txt, timeout=10)
        if not loc:
            return None
        tz = resolve_timezone(loc.latitude, loc.longitude)
        return {"input": txt, "lat": float(loc.latitude), "lon": float(loc.longitude), "timezone": tz, "source": "geopy-nominatim"}
    except Exception:
        return None

def parse_birth_datetime(dob, birth_time: str, place_info):
    if isinstance(dob, str):
        d = datetime.strptime(dob.strip(), "%Y-%m-%d").date()
    elif isinstance(dob, date):
        d = dob
    else:
        raise ValueError("dob must be YYYY-MM-DD or date")
    if not birth_time:
        raise ValueError("Exact birth time is mandatory for astrology reports.")
    parts = birth_time.strip().split(":")
    if len(parts) < 2:
        raise ValueError("Birth time must be HH:MM.")
    local = datetime(d.year, d.month, d.day, int(parts[0]), int(parts[1]), tzinfo=ZoneInfo(place_info["timezone"]))
    utc = local.astimezone(ZoneInfo("UTC"))
    return local, utc

def julday(dt_utc):
    hour = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour)

def nakshatra(lon):
    span = 360 / 27
    idx = int(norm360(lon) / span)
    rem = norm360(lon) - idx * span
    pada = int(rem / (span / 4)) + 1
    name, lord = NAKSHATRAS[idx]
    return {"name": name, "lord": lord, "pada": pada}

def dignity(planet, sidx):
    if sidx == EXALTATION.get(planet):
        return "Exalted"
    if sidx == DEBILITATION.get(planet):
        return "Debilitated"
    if sidx in OWN_SIGNS.get(planet, set()):
        return "Own sign"
    return "Neutral"

def calc_planets(jd, asc_lon):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = {}
    for name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu"]:
        pid = PLANETS[name]
        data, _ = swe.calc_ut(jd, pid, flags)
        lon = norm360(data[0])
        speed = data[3]
        if name == "Rahu":
            out[name] = _planet_record(name, lon, speed, asc_lon)
            ketu_lon = norm360(lon + 180)
            out["Ketu"] = _planet_record("Ketu", ketu_lon, -speed, asc_lon)
        else:
            out[name] = _planet_record(name, lon, speed, asc_lon)
    return out

def _planet_record(name, lon, speed, asc_lon):
    sidx = sign_index(lon)
    return {
        "planet": name, "longitude": lon, "sign": SIGNS[sidx], "sign_index": sidx,
        "degree": sign_degree(lon), "house": house_from(lon, asc_lon),
        "nakshatra": nakshatra(lon), "dignity": dignity(name, sidx),
        "retrograde": bool(speed < 0), "nature": FUNCTIONAL_NATURE.get(name, "neutral"),
        "aspects_houses": [], "aspected_by": [],
    }

def house_lords(asc_lon):
    asc_sign = sign_index(asc_lon)
    return {i + 1: SIGN_LORDS[(asc_sign + i) % 12] for i in range(12)}

def divisional_sign_generic(lon, division):
    sidx = sign_index(lon)
    deg = sign_degree(lon)
    part = int(deg / (30 / division))
    return SIGNS[(sidx * division + part) % 12]

def divisional_sign(lon, division):
    sidx = sign_index(lon)
    deg = sign_degree(lon)
    if division == 9:
        part = int(deg / (30 / 9))
        start = sidx if sidx in {0,3,6,9} else (sidx + 8) % 12 if sidx in {1,4,7,10} else (sidx + 4) % 12
        return SIGNS[(start + part) % 12]
    if division == 10:
        part = int(deg / 3)
        start = sidx if sidx % 2 == 0 else (sidx + 8) % 12
        return SIGNS[(start + part) % 12]
    if division == 7:
        part = int(deg / (30 / 7))
        start = sidx if sidx % 2 == 0 else (sidx + 6) % 12
        return SIGNS[(start + part) % 12]
    if division == 12:
        part = int(deg / 2.5)
        return SIGNS[(sidx + part) % 12]
    if division == 30:
        if sidx % 2 == 0:
            segments = [(5,0),(10,10),(18,8),(25,2),(30,6)]
        else:
            segments = [(5,1),(12,5),(20,11),(25,9),(30,7)]
        for limit, out_sign in segments:
            if deg < limit:
                return SIGNS[out_sign]
    return divisional_sign_generic(lon, division)

def calc_divisional(planets):
    charts = {}
    for div, key in [(9,"D9 Navamsa"),(10,"D10 Dashamsa"),(7,"D7 Saptamsa"),(12,"D12 Dwadashamsa"),(30,"D30 Trimsamsa")]:
        charts[key] = {p: divisional_sign(v["longitude"], div) for p, v in planets.items()}
    charts["D60 Shashtiamsa"] = {"available": False, "reason": "D60 is highly birth-time sensitive and is not printed unless source time precision is verified."}
    return charts

def apply_aspects(planets):
    """Attach standard graha drishti by whole-sign houses."""
    by_house = {i: [] for i in range(1, 13)}
    for p, v in planets.items():
        houses = []
        for offset in ASPECT_OFFSETS.get(p, [7]):
            h = ((v["house"] + offset - 2) % 12) + 1
            houses.append(h)
            by_house[h].append(p)
        v["aspects_houses"] = houses
    for p, v in planets.items():
        v["aspected_by"] = by_house[v["house"]]
    return by_house

def rashi_chart(planets, asc_lon):
    signs = {s: {"sign": SIGNS[s], "house": ((s - sign_index(asc_lon)) % 12) + 1, "planets": []} for s in range(12)}
    for p in PLANET_SEQUENCE:
        if p in planets:
            signs[planets[p]["sign_index"]]["planets"].append(p)
    return signs

def vimshottari_dasha(moon_lon, birth_dt_utc, as_of=None):
    if as_of is None:
        as_of = datetime.now(ZoneInfo("UTC"))
    span = 360 / 27
    n = nakshatra(moon_lon)
    start_lord = n["lord"]
    idx = DASHA_ORDER.index(start_lord)
    elapsed_in_nak = (norm360(moon_lon) % span) / span
    balance_years = DASHA_YEARS[start_lord] * (1 - elapsed_in_nak)
    start = birth_dt_utc - timedelta(days=(DASHA_YEARS[start_lord] - balance_years) * 365.2425)
    mahadashas = []
    cursor = start
    for k in range(12):
        lord = DASHA_ORDER[(idx + k) % 9]
        end = cursor + timedelta(days=DASHA_YEARS[lord] * 365.2425)
        mahadashas.append({"lord": lord, "start": cursor, "end": end})
        cursor = end
    current_md = next((d for d in mahadashas if d["start"] <= as_of < d["end"]), mahadashas[-1])
    ants = antardashas(current_md)
    current_ad = next((a for a in ants if a["start"] <= as_of < a["end"]), ants[0])
    upcoming = [a for a in ants if a["start"] >= as_of][:4]
    if not upcoming:
        mi = mahadashas.index(current_md)
        if mi + 1 < len(mahadashas):
            upcoming = antardashas(mahadashas[mi + 1])[:4]
    praty = pratyantardashas(current_md, current_ad)
    current_pd = next((p for p in praty if p["start"] <= as_of < p["end"]), praty[0])
    upcoming_pd = [p for p in praty if p["start"] >= as_of][:5]
    return {"mahadashas": mahadashas, "current_mahadasha": current_md,
            "current_antardasha": current_ad, "current_pratyantardasha": current_pd,
            "upcoming_antardashas": upcoming, "upcoming_pratyantardashas": upcoming_pd}

def antardashas(md):
    total_years = DASHA_YEARS[md["lord"]]
    cursor = md["start"]
    out = []
    start_idx = DASHA_ORDER.index(md["lord"])
    for k in range(9):
        lord = DASHA_ORDER[(start_idx + k) % 9]
        duration_days = total_years * DASHA_YEARS[lord] / 120 * 365.2425
        end = cursor + timedelta(days=duration_days)
        out.append({"lord": lord, "start": cursor, "end": end})
        cursor = end
    return out

def pratyantardashas(md, ad):
    ad_days = (ad["end"] - ad["start"]).total_seconds() / 86400
    cursor = ad["start"]
    out = []
    start_idx = DASHA_ORDER.index(ad["lord"])
    for k in range(9):
        lord = DASHA_ORDER[(start_idx + k) % 9]
        duration_days = ad_days * DASHA_YEARS[lord] / 120
        end = cursor + timedelta(days=duration_days)
        out.append({"lord": lord, "start": cursor, "end": end, "mahadasha": md["lord"], "antardasha": ad["lord"]})
        cursor = end
    return out

def transit_snapshot(as_of, asc_lon, moon_lon):
    jd = julday(as_of.astimezone(ZoneInfo("UTC")))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    ids = {"Saturn": swe.SATURN, "Jupiter": swe.JUPITER, "Rahu": swe.MEAN_NODE}
    out = {}
    for name, pid in ids.items():
        data, _ = swe.calc_ut(jd, pid, flags)
        lon = norm360(data[0])
        out[name] = {"sign": sign_name(lon), "degree": sign_degree(lon), "from_lagna": house_from(lon, asc_lon), "from_moon": house_from(lon, moon_lon)}
    rahu = out["Rahu"]
    ketu_lon = norm360((SIGNS.index(rahu["sign"]) * 30 + rahu["degree"]) + 180)
    out["Ketu"] = {"sign": sign_name(ketu_lon), "degree": sign_degree(ketu_lon), "from_lagna": house_from(ketu_lon, asc_lon), "from_moon": house_from(ketu_lon, moon_lon)}
    return out

def five_year_transits(as_of, asc_lon, moon_lon):
    out = []
    base = as_of.astimezone(ZoneInfo("UTC"))
    for i in range(5):
        try:
            dt = base.replace(year=base.year + i)
        except ValueError:
            dt = base.replace(year=base.year + i, day=28)
        out.append({"year": dt.year, "transits": transit_snapshot(dt, asc_lon, moon_lon)})
    return out

def detect_yogas(planets, lords):
    yogas = []
    sun = planets["Sun"]; moon = planets["Moon"]; jup = planets["Jupiter"]; sat = planets["Saturn"]; ven = planets["Venus"]
    if jup["house"] in {1,4,7,10}:
        yogas.append({"name": "Jupiter Kendra Support", "basis": f"Jupiter in house {jup['house']} from Lagna", "meaning": "Wisdom, protection and guidance can become major life supports."})
    if sat["house"] in {3,6,10,11}:
        yogas.append({"name": "Saturn Upachaya Growth", "basis": f"Saturn in house {sat['house']}", "meaning": "Slow effort improves with age and can reward disciplined career growth."})
    if ven["dignity"] in {"Exalted","Own sign"}:
        yogas.append({"name": "Venus Strength", "basis": f"Venus is {ven['dignity']} in {ven['sign']}", "meaning": "Relationship, comfort, art and social grace receive support."})
    if sun["house"] == 10:
        yogas.append({"name": "Authority Emphasis", "basis": "Sun in the 10th house", "meaning": "Visibility, leadership and responsibility are central career themes."})
    for h in (1, 4, 7, 10):
        lord = lords[h]
        if planets[lord]["house"] in {1,4,7,10}:
            yogas.append({"name": f"Kendra Lord Activation H{h}", "basis": f"{h}th lord {lord} in kendra house {planets[lord]['house']}", "meaning": "A core life pillar is active and can produce visible events when dasha supports it."})
    for h in (5, 9):
        lord = lords[h]
        if planets[lord]["house"] in {1,4,5,7,9,10}:
            yogas.append({"name": f"Trikona Support H{h}", "basis": f"{h}th lord {lord} in supportive house {planets[lord]['house']}", "meaning": "Dharma, learning, fortune or creative intelligence receives support."})
    if lords[9] == lords[10] or planets[lords[9]]["house"] == planets[lords[10]]["house"]:
        yogas.append({"name": "Dharma-Karma Link", "basis": f"9th lord {lords[9]} and 10th lord {lords[10]} are linked by lordship or placement", "meaning": "Career choices work best when aligned with ethics, mentors and long-term dharma."})
    if not yogas:
        yogas.append({"name": "No major simple yoga flagged", "basis": "Basic rule scan only", "meaning": "The report relies more on house, dasha, transit and divisional synthesis."})
    return yogas

def strength_summary(planets):
    scored = []
    for p, v in planets.items():
        score = 0
        if v["dignity"] == "Exalted": score += 3
        elif v["dignity"] == "Own sign": score += 2
        elif v["dignity"] == "Debilitated": score -= 3
        if v["house"] in {1,4,7,10}: score += 1
        if v["house"] in {6,8,12}: score -= 1
        if v["retrograde"]: score -= 0.5
        benefic_aspects = [x for x in v.get("aspected_by", []) if x in {"Jupiter","Venus"}]
        malefic_aspects = [x for x in v.get("aspected_by", []) if x in {"Saturn","Mars","Rahu","Ketu"}]
        score += 0.5 * len(benefic_aspects)
        score -= 0.5 * len(malefic_aspects)
        scored.append((score, p))
    strong = [p for _, p in sorted(scored, reverse=True)[:3]]
    weak = [p for _, p in sorted(scored)[:3]]
    return {"strong_planets": strong, "challenged_planets": weak, "scores": {p: s for s, p in scored}}

def house_strengths(planets, aspects_by_house=None):
    aspects_by_house = aspects_by_house or {}
    scores = {i: 0 for i in range(1, 13)}
    for p, v in planets.items():
        delta = 1
        if v["dignity"] == "Exalted": delta += 2
        if v["dignity"] == "Own sign": delta += 1
        if v["dignity"] == "Debilitated": delta -= 2
        if p in {"Jupiter","Venus"}: delta += 1
        if p in {"Saturn","Mars","Rahu","Ketu"}: delta -= 0.5
        scores[v["house"]] += delta
    for h, aspecting in aspects_by_house.items():
        for p in aspecting:
            if p in {"Jupiter","Venus"}:
                scores[h] += 0.5
            elif p in {"Saturn","Mars","Rahu","Ketu"}:
                scores[h] -= 0.35
    strong = sorted(scores, key=scores.get, reverse=True)[:3]
    weak = sorted(scores, key=scores.get)[:3]
    return {"scores": scores, "strong_houses": strong, "weak_houses": weak}

def validate_chart(chart):
    if chart["place"]["source"] not in {"built-in", "lat-lon"}:
        raise ValueError("Birth place source is not reliable enough for astrology calculation.")
    for p in PLANET_SEQUENCE:
        if p not in chart["planets"]:
            raise ValueError(f"Missing calculated planet: {p}")
        lon = chart["planets"][p]["longitude"]
        if not (0 <= lon < 360):
            raise ValueError(f"Invalid longitude for {p}: {lon}")
    rahu = chart["planets"]["Rahu"]["longitude"]
    ketu = chart["planets"]["Ketu"]["longitude"]
    if abs(((ketu - rahu) % 360) - 180) > 0.01:
        raise ValueError("Rahu/Ketu axis failed validation.")
    md = chart["dasha"]["current_mahadasha"]["lord"]
    ad = chart["dasha"]["current_antardasha"]["lord"]
    if md not in chart["planets"] or ad not in chart["planets"]:
        raise ValueError("Dasha lord validation failed.")
    if chart["dasha"]["current_pratyantardasha"]["lord"] not in chart["planets"]:
        raise ValueError("Pratyantardasha lord validation failed.")
    return chart

def compute_chart(full_name, dob, birth_time, birth_place, gender="", focus_area="general life path", email=""):
    _require_swe()
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    place = parse_place(birth_place)
    local_dt, utc_dt = parse_birth_datetime(dob, birth_time, place)
    jd = julday(utc_dt)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    cusps, ascmc = swe.houses_ex(jd, place["lat"], place["lon"], b'W', swe.FLG_SIDEREAL)
    asc_lon = norm360(ascmc[0])
    planets = calc_planets(jd, asc_lon)
    aspects_by_house = apply_aspects(planets)
    lords = house_lords(asc_lon)
    moon = planets["Moon"]; sun = planets["Sun"]
    dasha = vimshottari_dasha(moon["longitude"], utc_dt)
    now = datetime.now(ZoneInfo(place["timezone"]))
    transits = transit_snapshot(now, asc_lon, moon["longitude"])
    yearly_transits = five_year_transits(now, asc_lon, moon["longitude"])
    divisions = calc_divisional(planets)
    strengths = strength_summary(planets)
    houses = house_strengths(planets, aspects_by_house)
    chart = {
        "name": full_name.strip(), "email": email, "gender": gender, "focus_area": focus_area or "general life path",
        "dob": dob if isinstance(dob, date) else datetime.strptime(dob, "%Y-%m-%d").date(),
        "birth_time": birth_time, "birth_place": birth_place, "place": place, "local_datetime": local_dt,
        "utc_datetime": utc_dt, "prepared_date": date.today(), "ayanamsa": ayanamsa,
        "calculation_settings": {
            "engine": "Swiss Ephemeris / pyswisseph",
            "ayanamsa": "Lahiri",
            "zodiac": "Sidereal",
            "house_system": "Whole-sign Rashi houses from Lagna",
            "node_type": "Mean Rahu/Ketu",
            "dasha": "Vimshottari Mahadasha, Antardasha and Pratyantardasha from Moon nakshatra",
            "place_source": place["source"],
        },
        "ascendant": {"longitude": asc_lon, "sign": sign_name(asc_lon), "degree": sign_degree(asc_lon), "nakshatra": nakshatra(asc_lon)},
        "moon_sign": moon["sign"], "sun_sign": sun["sign"], "moon_nakshatra": moon["nakshatra"],
        "planets": planets, "house_lords": lords, "aspects_by_house": aspects_by_house,
        "rashi_chart": rashi_chart(planets, asc_lon), "house_system": "Lahiri sidereal whole-sign houses from Lagna",
        "yogas": detect_yogas(planets, lords),
        "strengths": strengths, "houses": houses, "dasha": dasha, "divisional_charts": divisions,
        "ashtakavarga": {"available": False, "reason": "Exact Ashtakavarga scoring is not implemented in this engine, so no scores are printed."},
        "shadbala": {"available": False, "reason": "Full Shadbala requires a separate validated strength module; this report does not print fake bala values."},
        "transits": transits, "five_year_transits": yearly_transits,
    }
    return validate_chart(chart)
