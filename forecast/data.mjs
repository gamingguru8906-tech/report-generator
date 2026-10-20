// Everything the Personal Year Forecast needs about one person, as JSON on stdout.
// Input (stdin, JSON): { name, dob: "YYYY-MM-DD", year, phone?, gender? }
// Only the vendored Veshannastro brain and mobile rulebook are used: same input, same output.

import { brainReading } from './engine/brain/read.js';
import { personFacts, matchRules } from './engine/brain/match.js';
import { RULES } from './engine/brain/rules/index.js';
import * as c from './engine/brain/calc.js';
import { createEngine } from './engine/mobile-numerology/engine/core.js';
import { rulebook } from './engine/mobile-numerology/engine/rulebook.js';
import { clarity } from './engine/mobile-numerology/engine/clarity.js';
import { YEAR_WATCH } from './engine/mobile-numerology/engine/watch.js';
import relations from './engine/brain/data/relations.json' with { type: 'json' };
import watchRules from './engine/brain/rules/watch.json' with { type: 'json' };

const input = JSON.parse(await new Promise(res => {
  let s = ''; process.stdin.on('data', d => (s += d)); process.stdin.on('end', () => res(s));
}));

const dobP = c.parseDob(input.dob, new Date(Date.UTC(input.year + 1, 0, 1)));
if (!dobP.ok) { console.log(JSON.stringify({ ok: false, error: dobP.error })); process.exit(0); }
const dob = dobP.value;
const year = Number(input.year);
const name = String(input.name || '').trim();

// The reading is taken in mid-January of the forecast year; age-based rules use the age turned in that year.
const brain = brainReading({ dob, name, year, today: new Date(Date.UTC(year, 0, 15)) });
// Rules that hold only because of the age turned in the forecast year (they name an age in their condition).
const AGE_RULES = RULES.filter(r => r.status === 'approved' && r.say && JSON.stringify(r.when || {}).includes('"age"'));
const ageItems = [];
for (const day of [new Date(Date.UTC(year, 0, 1)), new Date(Date.UTC(year, 11, 31))]) {
  const f = personFacts({ dob, name, year, today: day });
  for (const r of matchRules(AGE_RULES, f)) {
    if (!ageItems.some(a => a.id === r.id && a.age === f.age)) ageItems.push({ id: r.id, say: r.say, polarity: r.polarity, areas: r.areas, set: r.set, age: f.age });
  }
}

// Timing windows with their raw periods (month lists or day ranges), for the month-by-month map.
const tFacts = personFacts({ dob, name, year, today: new Date(Date.UTC(year, 0, 15)) });
const timing = matchRules(RULES.filter(r => ['psychic', 'destiny'].includes(r.set) && r.status === 'approved' && r.say && r.period), tFacts)
  .map(r => ({ id: r.id, say: r.say, polarity: r.polarity, areas: r.areas, period: r.period }));

const psychic = c.birthNumber(dob), destiny = c.destinyNumber(dob);
const py = y => c.personalYear(dob, y);
const PY = py(year);
const pyRules = rulebook.personalYear;
const planets = Object.fromEntries(rulebook.planets.rules.map(r => [r.digit, { planet: r.planet, trait: r.story.trait, signifies: r.story.signifies }]));
const remedy = rulebook.remedies.rules.find(r => r.birth_number === psychic) || null;
const remedyDestiny = rulebook.remedies.rules.find(r => r.birth_number === destiny) || null;

// Birth-date yogas (same rule set and test the mobile engine uses on a number's grid).
const cnt = c.counts(c.gridDigits(dob));   // date of birth + destiny number, as on the Lo Shu page
const dobYogas = rulebook.yogas.rules
  .filter(r => r.present.every(d => cnt[d] > 0) && r.absent.every(d => cnt[d] === 0))
  .map(r => {
    const extra = (r.multiples ?? []).filter(m => cnt[m.digit] >= m.min).map(m => m.care);
    return { id: r.id, title: r.name, planets: r.planets, present: r.present, absent: r.absent,
      good: r.story?.good || null, care: [r.story?.care, ...extra].filter(Boolean).join(' ') || null,
      remedy: r.remedy?.text || null, areas: r.areas || [] };
  });

// Watch lines the forecast quotes: the dial colours the year names, and the wrist rules.
const approvedWatch = (watchRules.rules || watchRules).filter(r => r.status === 'approved' && r.say);
const watchSay = (attr, val) => approvedWatch.find(r => r.when?.watch && Object.keys(r.when.watch).length === 1
  && r.when.watch[attr] && r.when.watch[attr].length === 1 && r.when.watch[attr][0] === val)?.say || null;
const yw = YEAR_WATCH[PY];
const dials = (yw?.parts || []).flatMap(p => p.dialColour || []);
const watch = {
  accessories: (pyRules.years[String(PY)] || []).filter(i => i.cat === 'accessories').map(i => i.text),
  dials: dials.map(d => ({ colour: d, say: watchSay('dialColour', d) })).filter(x => x.say),
  metals: (yw?.parts || []).flatMap(p => p.caseMetal || []),
  wrist: { left: watchSay('wrist', 'left'), right: watchSay('wrist', 'right') },
  goals: approvedWatch.filter(r => r.when?.watch?.goal).map(r => ({ goal: r.when.watch.goal, say: r.say }))
    .filter(g => ['men', 'women'].some(x => g.goal.includes(x)))
};

// Mobile number (optional): the same engine and verdict the free mobile reading uses.
let mobile = null;
if (input.phone) {
  const eng = createEngine(rulebook);
  const concern = input.concern || 'money, career and family';
  const r = eng.reading({ name, mobile: input.phone, dob: dob.iso, concern, year, today: new Date(Date.UTC(year, 0, 15)) });
  if (r.ok) {
    const s = Object.fromEntries(r.sections.map(x => [x.id, x]));
    mobile = {
      number: r.input?.mobile || s.decoded.mobile, concern, concernAreas: s.concern.areas,
      pairs: s.decoded.pairs.map(p => ({ title: p.title, pair: p.pair, count: p.count, polarity: p.polarity, good: p.good || null, care: p.care || null, areas: p.areas })),
      counts: s['mobile-grid'].counts,
      yogas: s['mobile-grid'].yogas.map(y => ({ title: y.title, polarity: y.polarity, good: y.good || null, care: y.care || null, pattern: y.pattern, areas: y.areas })),
      notFor: s['not-for'], protection: s.protection, better: s['better-number'],
      ifKept: s['if-kept']?.items || [], concernItems: s.concern.items || [],
      clarity: clarity(r)
    };
  } else {
    mobile = { error: r.errors };
  }
}

const out = {
  ok: true,
  input: { name, dob: dob.iso, year, phone: input.phone || null, gender: input.gender || null },
  dob,
  psychic, destiny, master: c.masterDestiny(dob), karmic: c.karmicDebtDay(dob),
  destinyCompound: c.digitSum(`${dob.d}${dob.m}${dob.y}`),
  personalYear: PY,
  cycle: Array.from({ length: 10 }, (_, i) => ({ year: year - 1 + i, py: py(year - 1 + i) })),
  name: c.nameNumbers(name), personality: c.personalityNumber(name),
  maturity: name ? c.maturityNumber(destiny, c.nameNumbers(name).root) : null,
  ageInYear: year - dob.y,
  brain,
  ageItems,
  timing,
  relations: relations.rows,
  planets,
  chaldean: c.CHALDEAN,
  loshuLayout: c.LOSHU_GRID,
  pyRules: { year: pyRules.years[String(PY)] || [], prev: pyRules.years[String(py(year - 1))] || [],
    next: pyRules.years[String(py(year + 1))] || [], everyone: pyRules.for_everyone },
  remedy, remedyDestiny,
  bracelet: c.braceletFor(psychic), braceletShop: c.BRACELET_SHOP,
  dobYogas,
  watch,
  mobile
};
console.log(JSON.stringify(out));
