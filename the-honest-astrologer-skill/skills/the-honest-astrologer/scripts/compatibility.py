#!/usr/bin/env python3
"""
Vedic compatibility engine for The Honest Astrologer skill.

Computes:
  - Ashtakoota / Guna Milan (8-fold compatibility, 36 points total)
  - Manglik / Mangal Dosha check (from Lagna, Moon, and Venus)
  - Dasha period overlap and harmony
  - Planetary friendship between key relationship significators

Usage:
    from compatibility import analyze_compatibility
    result = analyze_compatibility(chart1, chart2)
    print(result['summary'])
"""

from typing import Literal


SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
              "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
              "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
              "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]


# ============================================================================
# ASHTAKOOTA / GUNA MILAN (36-point system)
# ============================================================================

def get_moon_nakshatra(chart: dict) -> int:
    """Return moon's nakshatra index (0-26)."""
    moon_lon = chart["planets"]["Moon"]["longitude"]
    return int(moon_lon // (360 / 27))


def get_moon_sign_idx(chart: dict) -> int:
    """Return moon's sign index (0-11)."""
    moon_sign = chart["planets"]["Moon"]["sign"]
    return SIGNS.index(moon_sign)


# --- 1. Varna (1 point) — spiritual/ego compatibility ---
VARNA_MAP = {
    # sign_idx → varna level
    0: 2, 4: 2, 8: 2,        # Aries, Leo, Sagittarius = Kshatriya (2)
    1: 1, 5: 1, 9: 1,        # Taurus, Virgo, Capricorn = Vaishya (1)
    2: 0, 6: 0, 10: 0,       # Gemini, Libra, Aquarius = Shudra (0)
    3: 3, 7: 3, 11: 3,       # Cancer, Scorpio, Pisces = Brahmin (3)
}

def varna_score(c1: dict, c2: dict) -> tuple[int, str]:
    """Bride's varna should not be higher than groom's. Score 1 or 0."""
    # In modern usage, treat symmetrically: same or compatible levels = 1.
    v1 = VARNA_MAP[get_moon_sign_idx(c1)]
    v2 = VARNA_MAP[get_moon_sign_idx(c2)]
    if v1 == v2 or abs(v1 - v2) <= 1:
        return 1, f"Varna levels are compatible ({v1} & {v2})."
    return 0, f"Varna mismatch ({v1} vs {v2}) — traditionally a small compatibility friction, but not significant in modern context."


# --- 2. Vashya (2 points) — mutual influence ---
VASHYA_GROUPS = {
    "Chatushpada": [4, 8],  # Leo, Sagittarius (last half — simplified)
    "Manava": [2, 5, 6, 10],  # Gemini, Virgo, Libra, Aquarius
    "Jalachara": [3, 11],  # Cancer, Pisces (and Cap last half — simplified)
    "Vanachara": [4],  # Leo (forest beasts — simplified)
    "Keeta": [7],  # Scorpio
}

def vashya_score(c1: dict, c2: dict) -> tuple[int, str]:
    """Simplified Vashya: same or harmonious group = 2, else 0 or 1."""
    s1 = get_moon_sign_idx(c1)
    s2 = get_moon_sign_idx(c2)
    g1 = next((k for k, v in VASHYA_GROUPS.items() if s1 in v), "Manava")
    g2 = next((k for k, v in VASHYA_GROUPS.items() if s2 in v), "Manava")
    if g1 == g2:
        return 2, f"Both belong to {g1} group — strong natural attraction."
    elif (g1, g2) in [("Manava", "Jalachara"), ("Jalachara", "Manava")]:
        return 1, "Moderate compatibility — different temperaments but workable."
    return 1, f"Mixed temperaments ({g1} & {g2}) — may take effort to understand each other."


# --- 3. Tara (3 points) — wellbeing/health ---
def tara_score(c1: dict, c2: dict) -> tuple[int, str]:
    """Tara: count nakshatras from one to the other; 1, 3, 5, 7 from start = bad."""
    n1 = get_moon_nakshatra(c1)
    n2 = get_moon_nakshatra(c2)
    # Count from groom's nakshatra to bride's
    t1 = ((n2 - n1) % 27) + 1
    t2 = ((n1 - n2) % 27) + 1
    bad_taras = {1, 3, 5, 7}
    score1_ok = (t1 % 9) not in bad_taras or (t1 % 9) == 0
    score2_ok = (t2 % 9) not in bad_taras or (t2 % 9) == 0
    score = 0
    if score1_ok: score += 1.5
    if score2_ok: score += 1.5
    if score == 3:
        return 3, "Strong wellbeing compatibility — supportive of each other's vitality."
    elif score >= 1.5:
        return int(score), "Mixed — one direction supports wellbeing more than the other."
    return 0, "Wellbeing compatibility is weak — both should pay extra attention to each other's health and stress."


# --- 4. Yoni (4 points) — physical/sexual compatibility ---
NAKSHATRA_YONI = {
    0: ("Horse", "M"), 1: ("Elephant", "M"), 2: ("Sheep", "M"), 3: ("Serpent", "M"),
    4: ("Serpent", "F"), 5: ("Dog", "M"), 6: ("Cat", "F"), 7: ("Sheep", "F"),
    8: ("Cat", "M"), 9: ("Rat", "M"), 10: ("Rat", "F"), 11: ("Cow", "M"),
    12: ("Buffalo", "F"), 13: ("Tiger", "F"), 14: ("Buffalo", "M"), 15: ("Tiger", "M"),
    16: ("Hare", "F"), 17: ("Hare", "M"), 18: ("Dog", "F"), 19: ("Monkey", "M"),
    20: ("Mongoose", "M"), 21: ("Monkey", "F"), 22: ("Lion", "F"), 23: ("Horse", "F"),
    24: ("Lion", "M"), 25: ("Cow", "F"), 26: ("Elephant", "F"),
}

YONI_FRIENDSHIP = {
    ("Horse", "Elephant"): 2, ("Sheep", "Monkey"): 1, ("Cat", "Rat"): 0,
    ("Dog", "Hare"): 1, ("Lion", "Elephant"): 0,
    # Same yoni = 4
    # Friendly = 3, neutral = 2, unfriendly = 1, enemy = 0
}

def yoni_score(c1: dict, c2: dict) -> tuple[int, str]:
    """Yoni: same yoni = 4, friendly = 3, neutral = 2, unfriendly = 1, enemy = 0."""
    n1 = get_moon_nakshatra(c1)
    n2 = get_moon_nakshatra(c2)
    y1, _ = NAKSHATRA_YONI[n1]
    y2, _ = NAKSHATRA_YONI[n2]
    if y1 == y2:
        return 4, f"Both have {y1} yoni — strong physical and instinctive compatibility."
    pair = tuple(sorted([y1, y2]))
    enemy_pairs = {("Cat", "Rat"), ("Dog", "Hare"), ("Lion", "Elephant"),
                   ("Mongoose", "Serpent"), ("Cow", "Tiger"), ("Buffalo", "Horse")}
    if pair in enemy_pairs:
        return 0, f"Yoni mismatch ({y1} vs {y2}) — physical/instinctive rhythms differ. Workable with conscious effort."
    return 2, f"Different yonis ({y1} & {y2}) — neutral compatibility, neither strongly aligned nor opposed."


# --- 5. Graha Maitri (5 points) — friendship of moon-sign lords ---
SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

PLANET_FRIENDSHIPS = {
    # Each planet's friends, neutrals, enemies
    "Sun":     {"friends": ["Moon", "Mars", "Jupiter"], "neutral": ["Mercury"], "enemies": ["Venus", "Saturn"]},
    "Moon":    {"friends": ["Sun", "Mercury"], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"], "enemies": []},
    "Mars":    {"friends": ["Sun", "Moon", "Jupiter"], "neutral": ["Venus", "Saturn"], "enemies": ["Mercury"]},
    "Mercury": {"friends": ["Sun", "Venus"], "neutral": ["Mars", "Jupiter", "Saturn"], "enemies": ["Moon"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "neutral": ["Saturn"], "enemies": ["Mercury", "Venus"]},
    "Venus":   {"friends": ["Mercury", "Saturn"], "neutral": ["Mars", "Jupiter"], "enemies": ["Sun", "Moon"]},
    "Saturn":  {"friends": ["Mercury", "Venus"], "neutral": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars"]},
}

def graha_maitri_score(c1: dict, c2: dict) -> tuple[int, str]:
    """Friendship between the lords of each person's moon sign."""
    s1 = get_moon_sign_idx(c1)
    s2 = get_moon_sign_idx(c2)
    l1 = SIGN_LORDS[s1]
    l2 = SIGN_LORDS[s2]
    if l1 == l2:
        return 5, f"Both moon signs ruled by {l1} — exceptional natural understanding."
    f1 = PLANET_FRIENDSHIPS[l1]
    f2 = PLANET_FRIENDSHIPS[l2]
    if l2 in f1["friends"] and l1 in f2["friends"]:
        return 5, "Mutual friends at planetary level — strong emotional and intellectual rapport."
    elif l2 in f1["friends"] or l1 in f2["friends"]:
        return 4, "One-sided friendship at planetary level — generally harmonious."
    elif l2 in f1["neutral"] and l1 in f2["neutral"]:
        return 3, "Neutral planetary relationship — neither pulls toward nor pushes away."
    elif l2 in f1["enemies"] or l1 in f2["enemies"]:
        return 1, f"Planetary tension between {l1} and {l2} — emotional friction may need conscious management."
    return 2, "Mixed planetary relationship — workable but requires effort."


# --- 6. Gana (6 points) — temperament/nature ---
NAKSHATRA_GANA = {
    # Deva (divine), Manushya (human), Rakshasa (intense)
    "Deva":     [0, 4, 6, 7, 12, 14, 16, 21, 26],
    "Manushya": [1, 3, 10, 11, 17, 19, 20, 24, 25],
    "Rakshasa": [2, 5, 8, 9, 13, 15, 18, 22, 23],
}

def gana_score(c1: dict, c2: dict) -> tuple[int, str]:
    """Same gana = 6, Deva-Manushya = 5, Manushya-Rakshasa = 1, Deva-Rakshasa = 0."""
    n1 = get_moon_nakshatra(c1)
    n2 = get_moon_nakshatra(c2)
    g1 = next(k for k, v in NAKSHATRA_GANA.items() if n1 in v)
    g2 = next(k for k, v in NAKSHATRA_GANA.items() if n2 in v)
    if g1 == g2:
        return 6, f"Both share {g1} temperament — natural temperament compatibility."
    pair = tuple(sorted([g1, g2]))
    if pair == ("Deva", "Manushya"):
        return 5, "Deva-Manushya pairing — generally harmonious, mild differences in approach."
    elif pair == ("Manushya", "Rakshasa"):
        return 1, "Manushya-Rakshasa pairing — temperament differences may show as conflict in stress moments."
    elif pair == ("Deva", "Rakshasa"):
        return 0, "Deva-Rakshasa pairing — significant temperament difference. Honest communication is essential."
    return 3, "Mixed temperament compatibility."


# --- 7. Bhakoot (7 points) — emotional/general life harmony ---
def bhakoot_score(c1: dict, c2: dict) -> tuple[int, str]:
    """Counted by sign-distance; 6/8, 9/5, 12/2 are bad combinations."""
    s1 = get_moon_sign_idx(c1)
    s2 = get_moon_sign_idx(c2)
    d1 = ((s2 - s1) % 12) + 1
    d2 = ((s1 - s2) % 12) + 1
    bad_pairs = [(6, 8), (9, 5), (12, 2)]
    if (d1, d2) in bad_pairs or (d2, d1) in bad_pairs:
        return 0, f"Bhakoot dosha present (sign distance {d1}/{d2}) — traditionally a sign of friction in finances or family life. Note: many couples with this score live full happy lives. Treat as a flag, not a verdict."
    return 7, "Bhakoot is favorable — natural ease in finances, family, and shared life direction."


# --- 8. Nadi (8 points) — genetic/health compatibility ---
NAKSHATRA_NADI = {
    "Adi":   [0, 5, 6, 11, 12, 17, 18, 23, 24],  # Vata
    "Madhya":[1, 4, 7, 10, 13, 16, 19, 22, 25],  # Pitta
    "Antya": [2, 3, 8, 9, 14, 15, 20, 21, 26],   # Kapha
}

def nadi_score(c1: dict, c2: dict) -> tuple[int, str]:
    """Same nadi = 0 (traditionally unfavorable), different = 8."""
    n1 = get_moon_nakshatra(c1)
    n2 = get_moon_nakshatra(c2)
    nd1 = next(k for k, v in NAKSHATRA_NADI.items() if n1 in v)
    nd2 = next(k for k, v in NAKSHATRA_NADI.items() if n2 in v)
    if nd1 == nd2:
        return 0, (f"Both share {nd1} nadi — traditionally called 'Nadi dosha'. Classical texts associated this with "
                   "health/genetic concerns for offspring, but the rationale is dated. Modern context: treat as a "
                   "reminder to be mindful of shared health patterns and to make health-related decisions consciously, "
                   "not as a reason to break a match.")
    return 8, f"Different nadis ({nd1} & {nd2}) — favorable for genetic/health compatibility per classical reasoning."


def compute_ashtakoota(c1: dict, c2: dict) -> dict:
    """Compute full Ashtakoota / Guna Milan and return structured result."""
    breakdown = {
        "Varna":        varna_score(c1, c2),
        "Vashya":       vashya_score(c1, c2),
        "Tara":         tara_score(c1, c2),
        "Yoni":         yoni_score(c1, c2),
        "Graha Maitri": graha_maitri_score(c1, c2),
        "Gana":         gana_score(c1, c2),
        "Bhakoot":      bhakoot_score(c1, c2),
        "Nadi":         nadi_score(c1, c2),
    }
    total = sum(score for score, _ in breakdown.values())
    max_total = 36

    # Honest interpretation of the total
    if total >= 30:
        verdict = "Very high traditional compatibility score. But remember: high score ≠ guaranteed happy marriage. Behavior matters more."
    elif total >= 24:
        verdict = "Good compatibility score. Most categories aligned."
    elif total >= 18:
        verdict = "Moderate score. Some areas aligned, some not. Workable with awareness."
    else:
        verdict = "Lower traditional score. This does NOT mean the relationship can't work. It means specific areas need conscious attention."

    return {
        "breakdown": {k: {"score": s, "max": m, "note": n} for k, (s, n), m in
                      zip(breakdown.keys(),
                          breakdown.values(),
                          [1, 2, 3, 4, 5, 6, 7, 8])},
        "total": total,
        "max": max_total,
        "verdict": verdict,
    }


# ============================================================================
# MANGLIK / MANGAL DOSHA CHECK
# ============================================================================

def is_manglik(chart: dict) -> dict:
    """Check Manglik status from Mars placement in 1st, 2nd, 4th, 7th, 8th, 12th houses."""
    mars_house = chart["planets"]["Mars"]["house"]
    manglik_houses = {1, 2, 4, 7, 8, 12}
    is_mglk = mars_house in manglik_houses
    severity = "low"
    if mars_house in {7, 8}:
        severity = "high"
    elif mars_house in {1, 4, 12}:
        severity = "medium"
    return {
        "is_manglik": is_mglk,
        "mars_house": mars_house,
        "severity": severity if is_mglk else "none",
        "explanation": (
            f"Mars is in house {mars_house}." +
            (" This is one of the houses traditionally classified as Manglik."
             if is_mglk else " This is NOT a Manglik placement.")
        )
    }


def manglik_compatibility(c1: dict, c2: dict) -> dict:
    """Honest Manglik comparison between two charts."""
    m1 = is_manglik(c1)
    m2 = is_manglik(c2)

    if m1["is_manglik"] and m2["is_manglik"]:
        framing = ("Both are Manglik. In traditional terms this is considered to CANCEL OUT — neither person is "
                   "harmed by the other's Mars placement. The honest reading: both of you carry the same intensity "
                   "in partnership matters, which often means you understand each other's directness rather than being "
                   "destabilized by it.")
        flag = "balanced"
    elif m1["is_manglik"] or m2["is_manglik"]:
        which = "Person 1" if m1["is_manglik"] else "Person 2"
        framing = (f"{which} is Manglik; the other is not. Traditional astrologers raise concern here; honest reading: "
                   "this is a flag to be aware of, not a curse. Practical implication: the Manglik partner may bring "
                   "more directness, intensity, or quick temper into conflict moments. The non-Manglik partner should "
                   "not take this personally; the Manglik partner should learn to pause before reacting. Most couples "
                   "with this configuration build successful marriages through awareness.")
        flag = "imbalanced"
    else:
        framing = "Neither is Manglik. No Mars-related dosha to address."
        flag = "none"

    return {
        "person1": m1,
        "person2": m2,
        "framing": framing,
        "flag": flag,
        "honest_warning": (
            "IMPORTANT: The traditional 'Manglik causes early death of spouse' framing is not supported by any "
            "honest reading of the texts and has caused enormous harm to real marriages. It should not be a basis "
            "for breaking off a match you otherwise feel good about."
        )
    }


# ============================================================================
# DASHA OVERLAP & PLANETARY FRIENDSHIP
# ============================================================================

def dasha_overlap(c1: dict, c2: dict) -> dict:
    """Compare current dasha periods of both people."""
    md1 = c1.get("current_mahadasha", {})
    md2 = c2.get("current_mahadasha", {})
    if not md1 or not md2:
        return {"summary": "Dasha data not available for comparison."}

    lord1 = md1["lord"]
    lord2 = md2["lord"]

    # Use planetary friendship to gauge harmony
    if lord1 == lord2:
        harmony = "very_high"
        note = f"Both currently in {lord1} mahadasha — strong period harmony. You're both in the same kind of life-phase right now."
    elif lord2 in PLANET_FRIENDSHIPS[lord1]["friends"]:
        harmony = "high"
        note = f"You're in {lord1} mahadasha; partner is in {lord2}. These planets are friends — your current life-phases support each other."
    elif lord2 in PLANET_FRIENDSHIPS[lord1]["enemies"]:
        harmony = "low"
        note = f"You're in {lord1} mahadasha; partner is in {lord2}. These planets are at odds — you may be wanting different things from life right now."
    else:
        harmony = "neutral"
        note = f"You're in {lord1} mahadasha; partner is in {lord2}. Neutral planetary relationship — different but not conflicting."

    return {
        "person1_md": lord1,
        "person2_md": lord2,
        "harmony": harmony,
        "note": note,
    }


def planetary_friendship(c1: dict, c2: dict) -> dict:
    """Check key relationship planets: Venus, Mars, Moon, 7th lord."""
    findings = []

    # Venus-Mars cross-check (sexual/romantic compatibility)
    v1_sign = SIGNS.index(c1["planets"]["Venus"]["sign"])
    m2_sign = SIGNS.index(c2["planets"]["Mars"]["sign"])
    diff_vm = (m2_sign - v1_sign) % 12
    if diff_vm in [0, 4, 8]:  # same, trine
        findings.append("Venus-Mars cross-aspect is harmonious — physical/romantic chemistry is naturally easy.")
    elif diff_vm in [6]:  # opposition
        findings.append("Venus-Mars are in opposition — strong attraction with potential for friction. Common in 'opposites attract' pairings.")

    # Moon-Moon (emotional compatibility)
    moon1_sign = SIGNS.index(c1["planets"]["Moon"]["sign"])
    moon2_sign = SIGNS.index(c2["planets"]["Moon"]["sign"])
    diff_mm = abs(moon1_sign - moon2_sign)
    if diff_mm in [0, 4, 8]:
        findings.append("Moon-Moon harmony — emotional rhythms naturally align. Daily mood compatibility is good.")
    elif diff_mm == 6:
        findings.append("Moon-Moon opposition — emotional rhythms differ. One may want connection when the other wants space. Workable with mutual respect.")

    # Jupiter (long-term wisdom/dharma compatibility)
    j1_sign = SIGNS.index(c1["planets"]["Jupiter"]["sign"])
    j2_sign = SIGNS.index(c2["planets"]["Jupiter"]["sign"])
    if abs(j1_sign - j2_sign) in [0, 4, 8]:
        findings.append("Jupiter compatibility is favorable — shared values, growth-orientation, long-term life direction align.")

    return {"findings": findings if findings else ["No strongly notable planetary aspects between the charts."]}


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_compatibility(c1: dict, c2: dict, c1_name: str = "Person 1", c2_name: str = "Person 2") -> dict:
    """Full compatibility analysis."""
    return {
        "names": {"person1": c1_name, "person2": c2_name},
        "ashtakoota": compute_ashtakoota(c1, c2),
        "manglik": manglik_compatibility(c1, c2),
        "dasha": dasha_overlap(c1, c2),
        "planetary_friendship": planetary_friendship(c1, c2),
    }


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser(description="Compute Vedic compatibility between two charts.")
    p.add_argument("--chart1", required=True, help="Path to first person's chart JSON")
    p.add_argument("--chart2", required=True, help="Path to second person's chart JSON")
    p.add_argument("--name1", default="Person 1")
    p.add_argument("--name2", default="Person 2")
    args = p.parse_args()

    with open(args.chart1) as f:
        chart1 = json.load(f)
    with open(args.chart2) as f:
        chart2 = json.load(f)

    result = analyze_compatibility(chart1, chart2, args.name1, args.name2)
    print(json.dumps(result, indent=2, default=str))
