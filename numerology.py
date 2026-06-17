"""Veshann Astro — Numerology Calculation Engine
Chaldean name system + standard Vedic date reduction (matches the Veshannastro e-book)."""
from datetime import date
import calendar

CHALDEAN = {
    'A':1,'I':1,'J':1,'Q':1,'Y':1,
    'B':2,'K':2,'R':2,
    'C':3,'G':3,'L':3,'S':3,
    'D':4,'M':4,'T':4,
    'E':5,'H':5,'N':5,'X':5,
    'U':6,'V':6,'W':6,
    'O':7,'Z':7,
    'F':8,'P':8,
}
VOWELS = set('AEIOU')
MASTERS = {11, 22, 33}
KARMIC_DEBTS = {13, 14, 16, 19}
PLANETS = {1:'Sun (Surya)',2:'Moon (Chandra)',3:'Jupiter (Guru)',4:'Rahu',5:'Mercury (Budh)',
           6:'Venus (Shukra)',7:'Ketu',8:'Saturn (Shani)',9:'Mars (Mangal)'}

def digits(n): return [int(d) for d in str(n)]

def reduce_num(n, keep_masters=True):
    while n > 9:
        if keep_masters and n in MASTERS: return n
        n = sum(digits(n))
    return n

def reduce_track_debt(n):
    """Reduce while noting if a karmic-debt total appears."""
    debt = n if n in KARMIC_DEBTS else None
    while n > 9 and n not in MASTERS:
        n = sum(digits(n))
        if debt is None and n in KARMIC_DEBTS: debt = n
    return n, debt

def name_letters(name):
    return [c for c in name.upper() if c in CHALDEAN]

def name_value(name, subset=None):
    total = 0
    for c in name_letters(name):
        if subset == 'vowels' and c not in VOWELS: continue
        if subset == 'consonants' and c in VOWELS: continue
        total += CHALDEAN[c]
    return total

def names_by_root(names):
    """Bucket candidate names by their reduced Chaldean root."""
    buckets = {}
    for name in names:
        root = reduce_num(name_value(name), keep_masters=False)
        buckets.setdefault(root, []).append(name)
    return buckets

def lo_shu_digits(d: date, driver, conductor):
    ds = digits(d.day) + digits(d.month) + digits(d.year)
    ds = [x for x in ds if x != 0]
    # Vedic practice: include driver & conductor in the grid
    ds += [driver, reduce_num(conductor, keep_masters=False) if conductor in MASTERS else conductor]
    return ds

LO_SHU_POS = {4:(0,0),9:(0,1),2:(0,2),3:(1,0),5:(1,1),7:(1,2),8:(2,0),1:(2,1),6:(2,2)}
PLANES = {
    'Mind Plane (4-9-2)': [4,9,2], 'Emotional Plane (3-5-7)': [3,5,7], 'Practical Plane (8-1-6)': [8,1,6],
    'Thought Plane (4-3-8)': [4,3,8], 'Will Plane (9-5-1)': [9,5,1], 'Action Plane (2-7-6)': [2,7,6],
    'Golden Plane / Raj Yog (4-5-6)': [4,5,6], 'Silver Plane (2-5-8)': [2,5,8],
}

def compute(full_name: str, dob: date, gender: str = ''):
    r = {}
    r['name'] = full_name.strip()
    r['dob'] = dob
    r['gender'] = gender

    # Core date numbers
    r['driver'] = reduce_num(dob.day, keep_masters=False)          # Birthday/Mulank
    r['birthday_raw'] = dob.day
    lp_total = sum(digits(dob.day)) + sum(digits(dob.month)) + sum(digits(dob.year))
    r['life_path'], r['lp_debt'] = reduce_track_debt(lp_total)
    r['life_path_total'] = lp_total

    # Name numbers (Chaldean)
    dest_total = name_value(full_name)
    r['destiny_total'] = dest_total
    r['destiny'], r['destiny_debt'] = reduce_track_debt(dest_total)
    su_total = name_value(full_name, 'vowels')
    r['soul_urge_total'] = su_total
    r['soul_urge'], r['soul_debt'] = reduce_track_debt(su_total)
    pe_total = name_value(full_name, 'consonants')
    r['personality_total'] = pe_total
    r['personality'], _ = reduce_track_debt(pe_total)
    r['maturity'] = reduce_num(reduce_num(r['life_path'], False) + reduce_num(r['destiny'], False))

    # Karmic debts found anywhere
    debts = set()
    for k in ('lp_debt','destiny_debt','soul_debt'):
        if r[k]: debts.add(r[k])
    if dob.day in KARMIC_DEBTS: debts.add(dob.day)
    r['karmic_debts'] = sorted(debts)

    # Lo Shu grid
    ds = lo_shu_digits(dob, r['driver'], r['life_path'])
    counts = {i: ds.count(i) for i in range(1,10)}
    r['grid_counts'] = counts
    r['missing'] = [i for i in range(1,10) if counts[i]==0]
    r['repeated'] = {i:c for i,c in counts.items() if c>=2}
    r['complete_planes'] = [p for p,nums in PLANES.items() if all(counts[n]>0 for n in nums)]

    # Hidden passion: most frequent Chaldean value(s) in name
    letter_vals = [CHALDEAN[c] for c in name_letters(full_name)]
    freq = {i: letter_vals.count(i) for i in range(1,10) if letter_vals.count(i)>0}
    mx = max(freq.values())
    r['hidden_passion'] = sorted([i for i,c in freq.items() if c==mx])
    r['name_freq'] = freq

    # Karmic lessons: values 1-8 absent from name (Chaldean has no 9)
    r['karmic_lessons'] = [i for i in range(1,9) if freq.get(i,0)==0]

    # Pinnacles & challenges (standard formulas, single-digit month/day/year)
    m, d, y = reduce_num(dob.month, False), reduce_num(dob.day, False), reduce_num(sum(digits(dob.year)), False)
    p1 = reduce_num(m + d); p2 = reduce_num(d + y); p3 = reduce_num(reduce_num(p1,False)+reduce_num(p2,False)); p4 = reduce_num(m + y)
    lp9 = reduce_num(r['life_path'], False)
    a1 = 36 - lp9
    r['pinnacles'] = [
        {'num': p1, 'span': f"Birth – age {a1}"},
        {'num': p2, 'span': f"Age {a1+1} – {a1+9}"},
        {'num': p3, 'span': f"Age {a1+10} – {a1+18}"},
        {'num': p4, 'span': f"Age {a1+19} onwards"},
    ]
    c1 = abs(m - d); c2 = abs(d - y); c3 = abs(c1 - c2); c4 = abs(m - y)
    r['challenges'] = [c1, c2, c3, c4]

    # Personal year (current year)
    today = date.today()
    py = reduce_num(sum(digits(dob.day)) + sum(digits(dob.month)) + sum(digits(today.year)), False)
    r['personal_year'] = py
    r['personal_year_for'] = today.year

    # Name vibration check: is destiny number friendly to driver/life path?
    FRIENDS = {1:{1,2,3,5,6,9},2:{1,2,3,5},3:{1,2,3,5,6,9},4:{1,4,5,6,7},5:{1,2,3,5,6},
               6:{1,3,4,5,6,9},7:{1,4,5,6,7},8:{3,4,5,6,7,8},9:{1,3,5,6,9}}
    d9 = r['driver']; dest9 = reduce_num(r['destiny'], False)
    r['name_friendly'] = dest9 in FRIENDS.get(d9, set())
    r['lucky_numbers'] = sorted(FRIENDS.get(d9,set()) & FRIENDS.get(lp9,set())) or sorted(FRIENDS.get(d9,set()))

    # 90-day career & luck roadmap (3 personal months from today)
    r['roadmap'] = compute_roadmap(dob, r['driver'], r['lucky_numbers'])
    return r

def _personal_year_for(dob, year):
    return reduce_num(sum(digits(dob.day)) + sum(digits(dob.month)) + sum(digits(year)), False)

def compute_roadmap(dob, driver, lucky_numbers, from_date=None):
    """Three consecutive personal months + their auspicious 'power dates'."""
    if from_date is None:
        from_date = date.today()
    targets = set([driver]) | set(lucky_numbers[:4])
    phases = []
    y, m = from_date.year, from_date.month
    for k in range(3):
        mm, yy = m + k, y
        while mm > 12: mm -= 12; yy += 1
        py = _personal_year_for(dob, yy)
        pm = reduce_num(reduce_num(py, False) + reduce_num(mm, False), False)
        ndays = calendar.monthrange(yy, mm)[1]
        start = from_date.day if k == 0 else 1
        power = [d for d in range(start, ndays + 1) if reduce_num(d, False) in targets][:6]
        phases.append(dict(year=yy, month=mm, pm=pm, power_dates=power,
                           day_range=f"Days {k*30+1}\u2013{k*30+30}"))
    return phases
