# Veshann Astro — Interpretation Library (Chaldean / Vedic blend)
# Edit freely: every string here flows straight into the PDF.

CORE = {
1: dict(planet="Sun (Surya)", archetype="The Sovereign Leader", element="Fire", gem="Ruby (Manik)", day="Sunday", colour="Gold, Orange, Copper",
  essence="The vibration of 1 carries the raw authority of the Sun — the karaka of soul, father, government and self-identity in Vedic astrology. People touched by this number are built to initiate, to lead from the front, and to stand visible. They dislike taking orders, learn fastest through independent action, and radiate a natural confidence that others instinctively follow.",
  strengths=["Natural leadership and command presence","Originality — starts what others only discuss","Strong willpower and self-belief","Quick decision-making under pressure","Magnetic, dignified personality"],
  shadow=["Ego flare-ups and difficulty accepting criticism","Impatience with slower people","Tendency to dominate rather than delegate","Loneliness at the top if humility is ignored"],
  remedy="Offer water to the rising Sun (Surya Arghya) and recite the Aditya Hridaya Stotra or 'Om Suryaya Namah' on Sundays. Respect your father and father-figures — the Sun strengthens when they are honoured."),
2: dict(planet="Moon (Chandra)", archetype="The Intuitive Diplomat", element="Water", gem="Pearl (Moti)", day="Monday", colour="White, Cream, Silver",
  essence="2 vibrates with the Moon — mind, emotion, mother and public connection. This is the number of the peacemaker: sensitive, imaginative, deeply intuitive and able to read a room before a word is spoken. Where 1 commands, 2 persuades. Partnerships, not solo battles, are where this energy wins.",
  strengths=["Powerful intuition and emotional intelligence","Diplomacy — resolves conflict gracefully","Creative imagination and artistic taste","Loyal, nurturing, deeply caring nature","Excellent in partnership-driven work"],
  shadow=["Mood swings tied to environment and people","Over-sensitivity to criticism","Indecisiveness; depends on others' approval","Tendency to absorb others' stress"],
  remedy="Wear white on Mondays, keep silver close to the body, and offer milk or white flowers to Shiva. Chant 'Om Chandraya Namah'. Caring for your mother and for water bodies steadies the Moon."),
3: dict(planet="Jupiter (Guru)", archetype="The Wise Teacher", element="Ether", gem="Yellow Sapphire (Pukhraj)", day="Thursday", colour="Yellow, Saffron",
  essence="3 belongs to Jupiter — the Guru of the gods, the karaka of wisdom, wealth, dharma and expansion. This vibration produces teachers, advisors, communicators and natural optimists. Knowledge flows toward them and through them; growth follows wherever they place sincere effort.",
  strengths=["Wisdom, ethics and big-picture vision","Gifted communicator, teacher and guide","Natural optimism that lifts everyone around","Luck and divine protection in crises","Creative self-expression — writing, speaking, performing"],
  shadow=["Over-confidence; promising more than is delivered","Preachiness — giving advice nobody asked for","Scattering energy across too many interests","Extravagance with money"],
  remedy="Chant 'Om Brihaspataye Namah' on Thursdays, donate yellow items (chana dal, turmeric, books) and respect teachers and elders. Feeding cows and teaching others for free amplifies Jupiter's grace."),
4: dict(planet="Rahu", archetype="The Unconventional Builder", element="Air (shadow)", gem="Hessonite (Gomed)", day="Saturday", colour="Grey, Electric Blue",
  essence="4 carries Rahu's electric, rule-breaking intelligence. It builds systems, questions tradition and thinks in ways the crowd cannot. Life under this vibration is rarely smooth — sudden ups and downs are its signature — but the same turbulence produces revolutionary success in technology, research, media and foreign connections.",
  strengths=["Out-of-the-box, futuristic thinking","Methodical, disciplined system-builder","Fearless in breaking outdated rules","Thrives in technology, media, foreign lands","Sharp analytical and investigative mind"],
  shadow=["Sudden reversals; unpredictable phases","Rebelliousness that creates unnecessary enemies","Obsessive thinking and restlessness","Feeling misunderstood or isolated"],
  remedy="Recite the Rahu Beej Mantra 'Om Bhram Bhreem Bhroum Sah Rahave Namah' on Saturdays, donate to sweepers and the underprivileged, and keep your home clutter-free. Discipline and routine convert Rahu's chaos into genius."),
5: dict(planet="Mercury (Budh)", archetype="The Versatile Communicator", element="Earth", gem="Emerald (Panna)", day="Wednesday", colour="Green",
  essence="5 vibrates with Mercury — intellect, speech, commerce and adaptability. It is the businessman's number, the most balanced digit, sitting at the centre of the Lo Shu grid. Quick wit, persuasive speech and the ability to profit from change define this energy. Money, travel and networks come naturally.",
  strengths=["Sharp intellect and lightning-fast learning","Persuasive speech — born negotiator and seller","Adaptability; comfortable with constant change","Strong business and money instincts","Youthful energy and humour at any age"],
  shadow=["Restlessness; boredom kills commitment","Scattered focus across too many ventures","Speculative risk-taking (trading, gambling)","Nervous energy and overthinking"],
  remedy="Chant 'Om Budhaya Namah' on Wednesdays, donate green moong dal, and feed green fodder to cows. Keeping promises and speaking truth strengthens Mercury more than any gemstone."),
6: dict(planet="Venus (Shukra)", archetype="The Magnetic Creator", element="Water", gem="Diamond / Opal", day="Friday", colour="White, Pink, Pastels",
  essence="6 belongs to Venus — luxury, love, beauty, art and material comfort. This vibration attracts wealth, refinement and devoted relationships. People under 6 are natural hosts, healers of the heart, and creators of beauty; family and aesthetics sit at the centre of their life purpose.",
  strengths=["Magnetic charm and refined taste","Attracts luxury, comfort and resources","Deep sense of responsibility toward family","Artistic and creative brilliance","Natural counsellor in matters of the heart"],
  shadow=["Over-indulgence in comfort and pleasure","Possessiveness in relationships","Avoiding hard conversations to keep harmony","Vanity or excessive concern with image"],
  remedy="Chant 'Om Shukraya Namah' on Fridays, donate white sweets or rice to young girls, and keep your living space beautiful and fragrant. Respecting your spouse/partner is the fastest Venus remedy."),
7: dict(planet="Ketu", archetype="The Mystic Seeker", element="Spirit", gem="Cat's Eye (Lehsunia)", day="Tuesday", colour="Smoky Grey, Violet",
  essence="7 carries Ketu's other-worldly vibration — the headless shadow planet of moksha, intuition and detachment. This number produces researchers, healers, occultists and spiritual seekers. It gives flashes of knowing that bypass logic, but it also detaches its native from purely material ambition.",
  strengths=["Penetrating intuition; truth-detector","Research depth — goes where others stop","Spiritual inclination and healing ability","Original, philosophical intelligence","Comfort with solitude; inner self-sufficiency"],
  shadow=["Detachment that reads as coldness","Escapism and unexplained restlessness","Difficulty with worldly routines and paperwork","Doubt and over-analysis of close relationships"],
  remedy="Chant 'Om Ketave Namah', serve dogs and feed multi-grain to birds, and worship Lord Ganesha — the remover of Ketu's confusion. Meditation is not optional for a 7; it is fuel."),
8: dict(planet="Saturn (Shani)", archetype="The Karmic Powerhouse", element="Air", gem="Blue Sapphire (Neelam)", day="Saturday", colour="Dark Blue, Black",
  essence="8 vibrates with Saturn — justice, discipline, delay and ultimate reward. This is the number of late but lasting success. Saturn tests its natives early, often through struggle, responsibility or restriction, then repays every drop of honest effort with authority, wealth and legacy that others cannot shake.",
  strengths=["Iron discipline and endurance","Executive ability — manages people, money, institutions","Deep sense of justice and fairness","Success that compounds and lasts","Capacity to rise from any setback"],
  shadow=["Delays and obstacles in early life","Workaholism; neglecting joy and health","Pessimism or emotional suppression","Karma returns fast — shortcuts backfire"],
  remedy="Offer mustard oil to Shani on Saturdays, serve labourers, the elderly and the disabled, and chant 'Om Shanaischaraya Namah'. For an 8, seva (selfless service) is the master key to fortune."),
9: dict(planet="Mars (Mangal)", archetype="The Courageous Humanitarian", element="Fire", gem="Red Coral (Moonga)", day="Tuesday", colour="Red",
  essence="9 carries the warrior fire of Mars — courage, energy, protection and completion. As the final digit, it holds a little of every number within it, giving broad compassion alongside fierce drive. These are the fighters, protectors, engineers and humanitarians who finish what others abandon.",
  strengths=["Courage — physical, moral and emotional","Tireless energy and fighting spirit","Compassion for the underdog","Leadership in crisis","Completes long, difficult missions"],
  shadow=["Short temper and impulsive reactions","Aggression when patience is needed","Taking on everyone's battles","Accident-proneness from haste"],
  remedy="Chant the Hanuman Chalisa on Tuesdays, donate red lentils (masoor dal), and channel Mars through sport or physical discipline. Hanuman bhakti is the single most powerful shield for a 9."),
11: dict(planet="Higher Moon (Master)", archetype="The Inspired Illuminator", element="Ether", gem="Pearl + Meditation", day="Monday", colour="White, Silver",
  essence="11 is a Master Number — the higher octave of 2. It carries intense intuition bordering on the psychic, and a life purpose tied to inspiring, healing or awakening others. The voltage is high: when grounded it produces visionaries; when ungrounded, anxiety. An 11 must learn to be a lighthouse, not a lightning rod.",
  strengths=["Visionary intuition and spiritual sensitivity","Inspires and uplifts at scale","Charisma rooted in authenticity","Bridge between material and spiritual worlds"],
  shadow=["Nervous tension and overstimulation","Self-doubt despite obvious gifts","Perfectionism and inner pressure","Can retreat to ordinary '2' living and feel unfulfilled"],
  remedy="All remedies of 2 (Moon) apply, plus daily meditation and pranayama — an 11 without a stillness practice burns its own wiring. Teach, write or guide: sharing the vision releases the pressure."),
22: dict(planet="Higher Rahu (Master)", archetype="The Master Builder", element="Earth", gem="Hessonite + Service", day="Saturday", colour="Earth tones",
  essence="22 is the Master Builder — the higher octave of 4. It combines the visionary reach of 11 with the practical engineering of 4, giving the rare capacity to turn massive dreams into physical reality: institutions, companies, movements. The duty is equally massive: this energy is meant for work that outlives its owner.",
  strengths=["Builds large, lasting structures","Vision + practicality in one mind","Magnetism for resources and teams","Global, legacy-level thinking"],
  shadow=["Crushing self-imposed pressure","Frustration when reality moves slowly","Risk of settling for small '4' life and feeling hollow"],
  remedy="All remedies of 4 (Rahu) apply. Anchor the vision in disciplined daily systems, and dedicate the work to something larger than yourself — 22 collapses under personal ambition but soars under mission."),
33: dict(planet="Higher Jupiter (Master)", archetype="The Master Teacher", element="Ether", gem="Yellow Sapphire + Seva", day="Thursday", colour="Saffron, Gold",
  essence="33 is the Master Teacher — the higher octave of 6, blending Venus's love with Jupiter's wisdom. It is the rarest vibration: a life purpose of selfless upliftment, healing and teaching through compassion. Its natives often carry responsibility for many and find joy only in giving.",
  strengths=["Unconditional compassion in action","Healing presence; people open up instantly","Teaching that transforms lives","Harmonises families, teams, communities"],
  shadow=["Martyrdom — giving until empty","Carrying burdens that aren't yours","Idealism wounded by an imperfect world"],
  remedy="All remedies of 6 (Venus) and 3 (Jupiter) apply. Learn sacred selfishness: rest and boundaries are part of your service, not a betrayal of it."),
}

LIFE_PATH_INTRO = ("Your Life Path Number is the single most important number in your chart. Calculated from your complete "
"date of birth, it reveals the central highway of this lifetime — the lessons your soul signed up for, the talents packed "
"in your karmic luggage, and the direction in which effort multiplies fastest. You can take detours, but fulfilment always "
"returns to this road.")

DESTINY_INTRO = ("Your Destiny (Expression) Number is calculated from the Chaldean value of your full name — the sound "
"vibration the universe hears every time you are called. While the Life Path shows the road, the Destiny Number shows the "
"vehicle: the talents, style and public mission through which you travel it. In the Chaldean system used at Veshann Astro, "
"each letter carries the live frequency of a planet, which is why name vibration can be tuned like an instrument.")

SOUL_INTRO = ("Your Soul Urge (Heart's Desire) Number comes from the vowels of your name — the breath inside the sound. "
"It reveals what you secretly long for beneath every public role: the private engine of your motivation. When your outer "
"life feeds this number, you feel deeply content; when it starves, success itself feels empty.")

PERSONALITY_INTRO = ("Your Personality Number comes from the consonants of your name — the structure around the breath. "
"It is the first impression you broadcast, the filter through which strangers, interviewers and in-laws first read you, "
"before they ever meet the real soul inside.")

BIRTHDAY_INTRO = ("Your Birthday Number (Mulank or Driver) is the day of the month you were born. In Vedic numerology it "
"is the engine of your daily nature — how you act, react and drive through ordinary life. It pairs with your Life Path "
"(Conductor): the Driver is the vehicle's engine, the Conductor decides the route.")

MATURITY_INTRO = ("Your Maturity Number is the sum of your Life Path and Destiny numbers. Around age 35–40 its vibration "
"begins to surface, revealing the harvest of your life's first half and the theme of your second. Knowing it early is like "
"reading the final chapter first — you can build toward it instead of stumbling into it.")

PERSONAL_YEAR = {
1:"A seed year. Everything you launch now echoes for nine years. Start the venture, send the proposal, change the city — bold beginnings are cosmically funded in a 1 year. Avoid clinging to the old; the universe is clearing your desk for a reason.",
2:"A patience year. After last year's planting, growth happens underground. Focus on partnerships, negotiation and emotional bonds. Progress feels slow — it is not; it is consolidating. Forcing outcomes this year breaks them.",
3:"An expression year. Communication, creativity, visibility and social luck expand. Publish, perform, market, network. Joy is the strategy. Guard only against scattering energy and over-spending in celebration.",
4:"A foundation year. The cosmos asks for systems, paperwork, health discipline and honest hard work. It feels heavier — but everything you structure now becomes the platform for next year's breakout. No shortcuts; they will be audited.",
5:"A change year. Travel, new opportunities, sudden pivots and freedom. Say yes to movement, marketing and new audiences. The risk is recklessness — change is favoured, chaos is not.",
6:"A responsibility year. Family, home, marriage, service and beautification take centre stage. Duties increase, but so does love and material comfort. Repair relationships now; the cosmic interest rate on harmony is at its peak.",
7:"An inward year. Study, research, spirituality and rest are rewarded; aggressive material pushing is not. Perfect for certifications, deep skill-building and health reset. Trust intuition over noise.",
8:"A power year. Saturn audits and rewards. Money, authority, property and recognition flow to disciplined past effort — and debts (karmic and financial) come due. Be scrupulously ethical; the leverage this year is enormous in both directions.",
9:"A completion year. Finish, forgive, release, donate. Old chapters close to clear space for the new nine-year cycle. Losses this year are almost always disguised liberations. Serve generously — 9 multiplies whatever is given.",
}

CAREER = {
1:"You are built for the front seat: founder, director, department head, government authority, politics, defence, or any role where the final call is yours. Working under a micromanager will slowly poison you. Best growth: entrepreneurship, leadership tracks, personal branding. Sun-ruled fields — administration, gold, energy, medicine — carry extra grace.",
2:"You shine where empathy is the skill: counselling, HR, hospitality, healing, public relations, arts, import-export, and anything connected to liquids, food, or the public mood. Partnership businesses suit you better than solo grind. Moon-ruled fields — dairy, water, shipping, nursing, psychology — amplify your luck.",
3:"Teaching, training, law, banking, finance, writing, religious or motivational work — wherever wisdom is transmitted, you rise. You are the natural advisor in any room. Jupiter-ruled fields — education, consultancy, publishing, finance, dharma-related work — bring both money and meaning.",
4:"Technology, engineering, research, aviation, media, photography, data, occult sciences and foreign-linked work reward your unconventional mind. Government and rigid corporate hierarchies frustrate you unless you run the system. Rahu-ruled fields — IT, electronics, speculation-adjacent analytics, innovation — are your goldmine.",
5:"Business is your birthright: sales, marketing, trading, brokerage, communication, travel, banking, accountancy, writing and digital commerce. You can sell anything because you genuinely understand people. Mercury-ruled fields — commerce, media, telecom, astrology itself — multiply your money fastest.",
6:"Luxury, beauty, design, fashion, interior, hospitality, entertainment, jewellery, food, healing arts and family business suit your Venusian polish. People pay you for taste. Venus-ruled fields — art, cosmetics, hotels, event design, counselling — bring wealth wrapped in comfort.",
7:"Research, spirituality, occult sciences, healing, psychology, pharmacy, forensics, archaeology, writing and deep technical specialisation are your zones. You need depth, not breadth — and autonomy, not supervision. Ketu-ruled fields — astrology, alternative medicine, investigation, moksha-marga work — feel like home.",
8:"Law, real estate, mining, construction, finance, large institutions, politics, oil, machinery and any long-game empire suit Saturn's children. Your career graph starts slow and ends towering — never compare your chapter 2 with someone's chapter 8. Saturn-ruled fields — judiciary, infrastructure, labour-intensive industry — pay late but pay forever.",
9:"Defence, police, sports, surgery, engineering, fire services, real estate, activism and leadership in crisis suit your Mars engine. You perform best with a mission, worst with monotony. Mars-ruled fields — protection, energy, land, athletics, emergency response — convert your fire into rank and respect.",
}

WEALTH = {
1:"Money follows your authority. Income jumps each time your designation, visibility or ownership rises — salary alone will always feel small. Build assets in your own name, invest in gold and blue-chip leadership stocks, and avoid lending to friends (your generosity is read as obligation). Wealth peak: after you stop working *for* someone.",
2:"Your money flows in waves, like your ruling Moon — strong months, lean months. The remedy is structure: automatic SIPs, fixed savings on salary day, and a partner or advisor who balances your emotional spending. Silver, dairy/food businesses, and public-facing ventures are your natural wealth channels.",
3:"Jupiter natives rarely stay poor — wisdom monetises. Your wealth grows through knowledge products, advisory roles, royalties and ethical investments. The leak is extravagance and over-generosity. Tithe deliberately (donate a fixed %, not impulse amounts) and Jupiter multiplies the rest.",
4:"Rahu gives sudden gains — and sudden drains. Windfalls, foreign income and tech-linked profits are real for you, but so are shock expenses. Rule: park every windfall in boring assets within 48 hours. Avoid gambling-style speculation; your edge is innovation, not luck.",
5:"You have the best raw money-mind of all numbers — Mercury is the banker of the zodiac. Multiple income streams are not a strategy for you, they are a necessity; one source bores you into sabotage. Trade, commissions, digital products and business scale beautifully. Watch only speculative excess.",
6:"Venus attracts money through beauty, comfort and relationships — clients pay premiums for your taste. Wealth grows via luxury-adjacent ventures, property, and family enterprises. The leak: lifestyle inflation. Buy assets that look beautiful AND appreciate (property, jewellery, art) so indulgence becomes investment.",
7:"Ketu detaches you from money — you can earn well yet feel oddly uninterested in chasing it. Monetise depth: specialised consulting, research, healing and royalties from intellectual property. Automate savings completely, because you will forget. Avoid partnerships where you handle accounts; delegate the worldly paperwork.",
8:"Saturn's wealth is compound interest incarnate: slow, then unstoppable. Real estate, infrastructure, long-term equity and institutional positions build your empire. Early-life money struggles are tuition, not verdict. Never take unethical shortcuts — Saturn audits 8s personally, and also rewards their honesty disproportionately.",
9:"Mars earns through courage — performance bonuses, ownership stakes, land and ventures where boldness is priced in. Money comes fast but exits fast through impulsive generosity and anger-driven decisions. Cooling-off rule: 72 hours before any purchase or investment above a set limit. Land is your most loyal asset.",
}

LOVE = {
1:"In love you protect, provide and lead — but the throne can get lonely if your partner feels like staff. Your lesson: vulnerability is not weakness. Most harmonious with 1, 2, 3, 5, 6 and 9 vibrations. Let your partner win some battles; the relationship is the kingdom, not you.",
2:"You love deeply, intuitively, and sometimes anxiously — you feel your partner's mood before they speak. Your need for reassurance is real; choose someone emotionally generous, not emotionally lazy. Harmonious with 1, 2, 3 and 5. Guard against losing yourself in the relationship: half of every 'we' must remain 'me'.",
3:"You need a partner you can talk to — mental connection precedes physical for Jupiter natives. You teach and uplift in love but can slip into lecturing. Harmonious with 1, 2, 3, 6 and 9. Keep the friendship alive inside the marriage; the day conversation dies, so does your interest.",
4:"You love unconventionally — deeply loyal underneath, yet allergic to clichéd romance and suffocating routine. Partners may misread your independence as coldness. Harmonious with 1, 5, 6 and 7. Communicate your love in words occasionally; not everyone reads devotion through actions alone.",
5:"You need freedom inside commitment — a partner who is also your travel buddy, business sounding-board and best friend. Boredom, not conflict, is your relationship's only real enemy. Harmonious with 1, 2, 3 and 6. Keep novelty alive deliberately: new places, new projects, new conversations.",
6:"You are the most romantic vibration — devoted, generous, family-centred, the one who remembers anniversaries and builds the beautiful home. The shadow is possessiveness and over-sacrifice followed by resentment. Harmonious with 1, 3, 4, 5 and 9. Love them, but keep one room of your life that is only yours.",
7:"You love quietly and selectively — few are allowed in, and those few are kept for life. You need a partner who respects silence and doesn't interrogate your inner world. Harmonious with 1, 4, 5 and 6. Remember to translate your inner ocean into spoken words sometimes; partners cannot read meditation.",
8:"You show love through duty, stability and sacrifice — the partner who quietly pays the bills and stands in every storm. Words of affection come hard; this is your growth edge. Harmonious with 3, 4, 5, 6 and 7 (avoid pairing 8 with 8 unless both are evolved). Schedule joy: romance for an 8 must be planned or it never happens.",
9:"You love with the full fire of Mars — passionate, protective, all-in. The same fire becomes temper in conflict; your sharpest weapon in love is the apology you offer first. Harmonious with 1, 3, 5 and 6. Channel excess intensity into shared missions: couples who build together keep your flame purposeful.",
}

KARMIC_DEBT = {
13:"Karmic Debt 13 — the Debt of Labour. In a past cycle, work was avoided or others carried your share; in this one, shortcuts are sealed off. Tasks take longer for you than for others — not as punishment, but as repayment with interest. The transformation: once you embrace systematic, honest effort, 13 becomes one of the most powerful success numbers, building achievements that lazy talent can never touch. Discipline is your debt — and your superpower.",
14:"Karmic Debt 14 — the Debt of Freedom Misused. A past cycle of overindulgence or broken commitments returns as a life that tests moderation: sudden changes, temptations, and the constant pull of excess. The repayment is self-control — in food, habits, promises and pleasures. Master moderation and 14 grants the very freedom it once revoked: adaptability, magnetism and a life rich in experience without the crash.",
16:"Karmic Debt 16 — the Debt of the Fallen Tower. Past misuse of love, trust or position returns as cycles where carefully built structures (relationships, status, plans) suddenly collapse — always when ego has crept in. Each fall is a renovation, not a demolition: what rises afterwards is truer. The repayment is humility and authenticity. Live transparently, hold position lightly, and the tower stops falling — it becomes a lighthouse.",
19:"Karmic Debt 19 — the Debt of Misused Power. Authority was once used selfishly; now life ensures you must achieve alone, with help arriving only after you no longer need it. People may take credit for your work or abandon you at key moments — the curriculum is self-reliance without bitterness, and power used in service. Repay it, and 19 resolves into the radiant leadership of the Sun: respected, self-made, and finally surrounded by genuine allies.",
}

MISSING = {
1:"Missing 1 — the Sun's voice is absent from your grid. Expressing yourself confidently, asserting your needs and 'selling yourself' (interviews, negotiations) may feel unnatural. Remedy: daily Surya Namaskar or sun-gazing at dawn, speaking up once in every meeting as practice, and keeping a gold/copper element on the body.",
2:"Missing 2 — the Moon's sensitivity is absent. You may struggle to read others' emotions, appear blunt, or find intuition unreliable. Remedy: keep water in a silver glass overnight and drink it in the morning, practice listening without solving, and strengthen the Moon through Monday fasting or white-food donation.",
3:"Missing 3 — Jupiter's expansive imagination is absent. Long-term visualisation, planning beyond the immediate, and self-belief in knowledge may feel weak. Remedy: read or teach something daily (teaching activates Jupiter fastest), wear yellow on Thursdays, and write goals by hand every morning.",
4:"Missing 4 — Rahu's structure is absent. Organisation, patience with details and practical follow-through can be lifelong friction points. Remedy: externalise discipline — checklists, fixed routines, automated systems. A tidy work-desk is literally a remedy for you, not a cliché.",
5:"Missing 5 — Mercury's balance is absent from the very centre of your grid. Emotional balance, adaptability and drive may wobble; motivation arrives in bursts. Remedy: daily walking (Mercury rules movement), green vegetables, pranayama, and keeping commitments small but unbroken to rebuild Mercury's trust.",
6:"Missing 6 — Venus's warmth is absent. Family bonds, domestic harmony or comfort with luxury may feel complicated; you may under-prioritise relationships for work. Remedy: weekly family rituals (one meal, phones away), keeping fresh flowers at home, and consciously celebrating small joys — Venus grows through enjoyed beauty.",
7:"Missing 7 — Ketu's faith is absent. Spiritual scepticism, fear of loss, or difficulty trusting the unseen process may follow you. Remedy: a small daily stillness practice (even 5 minutes), time in nature, and one act of letting go each week — donate, forgive, or delete. Faith is built like muscle.",
8:"Missing 8 — Saturn's money-wisdom is absent. Financial management, long-term saving and respect for systems may be weak points; money slips through unnoticed. Remedy: written budgets, automatic savings on income day, respecting elders and serving the underprivileged on Saturdays — Saturn rewards visible humility with invisible protection.",
9:"Missing 9 — Mars's drive is absent. Physical energy, competitive fire or humanitarian breadth may run low; you may avoid confrontation even when it is needed. Remedy: regular physical exercise (non-negotiable), Hanuman Chalisa on Tuesdays, and one small brave act weekly — Mars grows through used courage.",
}

REPEATED = {
1:"Repeated 1s strengthen self-expression — but 111+ can tip confidence into dominance or talkativeness. Channel the Sun surplus into leadership and public speaking.",
2:"Repeated 2s deepen intuition to near-psychic levels — and amplify sensitivity. Protect your emotional bandwidth; you absorb rooms.",
3:"Repeated 3s multiply imagination and optimism — guard against living in plans instead of actions.",
4:"Repeated 4s intensify discipline and method — soften the rigidity; not everything needs a system.",
5:"Repeated 5s supercharge drive and persuasion — but excess 5 creates restlessness and burnout. Schedule stillness.",
6:"Repeated 6s magnify love of family and beauty — watch for over-attachment and worry about loved ones.",
7:"Repeated 7s deepen spiritual and research gifts — but can detach you from practical life. Stay anchored in one worldly responsibility.",
8:"Repeated 8s multiply Saturn's seriousness — immense capacity for wealth and order, with a duty to consciously practice lightness and joy.",
9:"Repeated 9s amplify courage and humanitarian fire — and temper. Physical outlets are mandatory, not optional.",
}

PLANE_MEANING = {
'Mind Plane (4-9-2)':"Complete Mind Plane — excellent memory, intellect and analytical thinking. You process, plan and remember better than most rooms you sit in.",
'Emotional Plane (3-5-7)':"Complete Emotional Plane — deep emotional intelligence, spiritual sensitivity and artistic feeling. You understand hearts, including your own.",
'Practical Plane (8-1-6)':"Complete Practical Plane — strong grounding in the material world: money sense, physical skill and the ability to execute. Ideas become things in your hands.",
'Thought Plane (4-3-8)':"Complete Thought Plane (Arrow of the Planner) — you naturally generate ideas AND the method to realise them. Born strategist.",
'Will Plane (9-5-1)':"Complete Will Plane (Arrow of Determination) — once you decide, the universe should simply cooperate; persistence is your signature weapon.",
'Action Plane (2-7-6)':"Complete Action Plane (Arrow of Action) — you convert thought into motion fast; execution is instinctive.",
'Golden Plane / Raj Yog (4-5-6)':"GOLDEN PLANE / Raj Yog combination (4-5-6) — one of the most auspicious patterns in Lo Shu numerology, indicating name, fame and wealth potential through balanced effort. Treasure and activate it.",
'Silver Plane (2-5-8)':"Silver Plane (2-5-8) — strong property, finance and emotional-practical balance axis. Wealth through real estate and steady management is indicated.",
}

KARMIC_LESSON = {
1:"Lesson of 1: learning to stand alone, decide independently and value your own voice. Life will repeatedly place you where no one else can choose for you.",
2:"Lesson of 2: learning patience, cooperation and emotional attunement. Situations will demand diplomacy where force fails.",
3:"Lesson of 3: learning joyful self-expression and optimism. Life pushes you onto stages — speak, write, share — until hiding stops being an option.",
4:"Lesson of 4: learning order, persistence and respect for process. Shortcuts will quietly stop working until systems are honoured.",
5:"Lesson of 5: learning healthy adaptability and the right use of freedom. Change will keep visiting until you stop resisting it.",
6:"Lesson of 6: learning responsibility in love and family. Duties of the heart will find you; embracing them unlocks your warmth.",
7:"Lesson of 7: learning faith, depth and inner stillness. Surface living will feel hollow until you go inward.",
8:"Lesson of 8: learning material mastery — money, authority, organisation. Finances will demand attention until managed consciously.",
}

CHALLENGE = {
0:"Challenge 0 — the 'choice' challenge: no single forced lesson, but the responsibility to act rightly without external pressure. The test of the free will.",
1:"Challenge 1 — asserting yourself without aggression; building confidence against forces that dismiss you.",
2:"Challenge 2 — managing sensitivity; not letting others' opinions and moods govern your decisions.",
3:"Challenge 3 — expressing instead of suppressing; overcoming self-criticism that silences your creativity.",
4:"Challenge 4 — embracing discipline and patience; resisting the urge to abandon structures midway.",
5:"Challenge 5 — using freedom constructively; avoiding excess, impulsiveness and constant escape.",
6:"Challenge 6 — balancing service with self; perfectionism and over-responsibility toward others must be tamed.",
7:"Challenge 7 — keeping faith through isolation phases; not letting scepticism wall off your heart.",
8:"Challenge 8 — relating to money and power cleanly; neither worshipping them nor fearing them.",
}

PINNACLE_NOTE = {
1:"a cycle of independence, new beginnings and self-made progress — leadership opportunities arrive and reward initiative.",
2:"a cycle of partnership, patience and emotional growth — progress comes through cooperation, marriage/alliances and quiet diplomacy.",
3:"a cycle of expression, creativity and social expansion — visibility, communication skills and joyful opportunities flourish.",
4:"a cycle of building, discipline and steady work — the years that lay your life's concrete foundation; effort compounds.",
5:"a cycle of change, travel and freedom — expect movement, pivots and exposure to new worlds; adaptability is rewarded.",
6:"a cycle of family, responsibility and harmony — marriage, home, children and community duties dominate and enrich.",
7:"a cycle of introspection, study and spiritual deepening — expertise, research and inner growth define these years.",
8:"a cycle of power, money and recognition — material harvest years; ambition backed by ethics yields authority.",
9:"a cycle of completion, service and broad horizons — humanitarian reach, endings that liberate, and wisdom shared.",
11:"a master cycle of illumination — intuition, inspiration and spiritual influence peak; high voltage, high purpose.",
22:"a master cycle of large-scale building — the rare years when grand visions can be made physically real.",
}

HOW_TO_READ = [
 ("Read in order, then return often","This report is sequenced like a Vedic chart reading: identity first (who you are), karma next (what you carry), timing after (when things ripen), and remedies last (what to do). Read it fully once, then keep it as a reference manual for decisions — naming a child, switching careers, choosing a wedding date, starting a venture."),
 ("The Chaldean difference","Veshann Astro uses the ancient Chaldean system — the original Babylonian-Vedic letter values based on sound vibration, not alphabetical order. Most free apps use the modern Pythagorean shortcut. Chaldean values are why our name analysis often differs from generic websites — and why it matches lived reality more closely."),
 ("Numbers are tendencies, not prison sentences","A number shows the default current of energy. Free will, effort and remedies redirect every current. Where this report names a weakness, read it as a workout plan, not a verdict."),
 ("Remedies are dosage, not decoration","Each remedy is mapped to the ruling planet (Graha) of the number involved. They work through consistency — a small practice done daily outperforms a grand ritual done once."),
 ("Your numbers work as a team","No number acts alone. Your Driver acts, your Conductor steers, your Destiny shapes the public mission, your Soul Urge fuels it. The Snapshot page shows the full team at a glance."),
]

USP_POINTS = [
 ("Authentic Chaldean–Vedic system","We compute with the original Chaldean sound values integrated with Vedic Graha (planetary) wisdom — the same framework used in our published book, not a western app template."),
 ("Remedy-first philosophy","Every analysis ends in an actionable remedy — mantra, donation, habit — because diagnosis without prescription is entertainment, not guidance."),
 ("Human verification","Every Veshann Astro report framework is designed and verified by our practising numerologist, blending classical texts with thousands of real consultations."),
 ("Beyond the report","This PDF is a doorway, not a destination — live voice consultations, palmistry, and full Kundli analysis are available whenever you want to go deeper."),
]

# ---- 90-Day Career & Luck Roadmap ----
ROADMAP_INTRO = ("Numerology's most practical gift is timing. The next ninety days carry a precise sequence of monthly "
"energies — each one opening a different door for your career and your luck. Work with the current instead of against it, "
"and ordinary effort starts producing extraordinary results. Here is your personalised quarter, month by month.")

PERSONAL_MONTH = {
1: ("Initiate & Lead",
    "Career: your strongest 30 days to begin — pitch the idea, send the application, launch the offer, ask for the role. First movers win now.",
    "Luck: act on a Sunday, keep gold, copper or red on you, and put your name forward visibly. Fortune follows initiative this month."),
2: ("Align & Partner",
    "Career: a slower, relational stretch — nurture partnerships, follow up on what you started, negotiate gently, build trust before you push.",
    "Luck: collaborate rather than compete, favour Mondays, keep white or silver close, and let things ripen — forcing outcomes breaks them now."),
3: ("Express & Network",
    "Career: a visibility window — publish, present, post content, attend events, speak up. Your words attract exactly the right people.",
    "Luck: Thursdays are golden, wear yellow, and say yes to social invitations. Luck arrives this month through people and conversation."),
4: ("Build & Systemise",
    "Career: a foundation month — finish paperwork, fix your systems, upskill, show discipline. Unspectacular work now becomes next quarter's launchpad.",
    "Luck: Saturdays reward honest effort, keep routines tight, and avoid shortcuts — they get audited this month."),
5: ("Pivot & Promote",
    "Career: a momentum month — sales, marketing, new leads, travel and bold pivots all flow. Push your reach and visibility hard.",
    "Luck: Wednesdays favour deals, wear green, and embrace change — just channel the restlessness instead of scattering it."),
6: ("Serve & Harmonise",
    "Career: a relationship month — tend to clients, teams and responsibilities; reliability and service quietly raise your standing.",
    "Luck: Fridays bring favour, keep harmony at work and home, and beautify your space. Venus rewards care and warmth now."),
7: ("Study & Refine",
    "Career: an inward month — research, certifications, deep skill-building and strategy beat aggressive pushing. Sharpen the blade.",
    "Luck: protect quiet time, trust intuition over noise, and avoid forcing big launches — let this be preparation, not performance."),
8: ("Negotiate & Claim",
    "Career: a power month — ask for the raise, close the deal, sign the contract, step into authority. Disciplined past effort pays out now.",
    "Luck: Saturdays carry weight, stay scrupulously ethical, and act decisively on money and property. Leverage runs high in both directions."),
9: ("Complete & Clear",
    "Career: a closing month — finish projects, tie loose ends, release what is done, and prepare the ground for a fresh cycle.",
    "Luck: give generously, forgive quickly, and avoid starting anything brand-new. Clearing space is this month's real fortune."),
}


# ── Baby-name pool (bucketed by Chaldean root at runtime via numerology.names_by_root) ──
# A broad pool of pleasant, common Indian names across genders. The engine computes each
# name's Chaldean root and only ever shows names that actually harmonise with the child.
BABY_NAME_POOL = [
    "Aarav","Aanya","Advait","Aditi","Ahaan","Aisha","Akshara","Amara","Ananya","Anika",
    "Arjun","Arnav","Aryan","Avni","Ayaan","Bhavya","Chirag","Daksh","Darsh","Devansh",
    "Dhruv","Diya","Eshan","Gauri","Hriday","Ira","Ishaan","Ishita","Jiya","Kabir",
    "Kavya","Kiara","Krish","Laksh","Lavanya","Madhav","Mahika","Manan","Meera","Mira",
    "Mohit","Myra","Naina","Navya","Neel","Nikhil","Nira","Ojas","Pari","Prisha",
    "Reyansh","Riya","Rohan","Rudra","Saanvi","Sahil","Samar","Sara","Shaurya","Shreya",
    "Siya","Tara","Tanvi","Tej","Vaani","Vedant","Vihaan","Vivaan","Yash","Zoya",
    "Anvi","Kiaan","Nitya","Parth","Ridhi","Veer","Tisha","Hitesh","Lakshya","Inaya",
]


# ---- Closing / Conclusion (editable copy) ----
# Used by report.sec_conclusion(). The strongest-themes, growth-edge and next-step
# lines are assembled PER PERSON from their own numbers in report.py; the strings
# below are only the surrounding framing, so you can re-voice the close freely.
CONCLUSION = {
 "kicker": "In Closing",
 "title": "Where You Stand — And What Comes Next",
 "lead_tail": ("Read together, these numbers describe one person with a clear direction. Here is the "
   "essence of everything above, in a few lines you can keep."),
 "themes_title": "Your Strongest Themes",
 "growth_title": "Your Growth Edge",
 "growth_tail": ("This is not a flaw — it is your curriculum. Each time you choose the truer response "
   "over the familiar one, the energy behind it turns from friction into strength."),
 "step_title": "Your One Next Step",
 "consult_heading": "Going One Layer Deeper",
 "consult_invite": ("A written report hands you the map. What it cannot do is sit with the one question "
   "you are carrying right now — a decision, a relationship, a turning point — and read your chart against "
   "that exact moment. That is what a personal consultation is for: the same numbers, applied precisely to "
   "your situation, with room for your own questions. Whenever you would like that deeper layer of clarity, "
   "it is here for you."),
 "signoff": ("May you walk your path with clarity, courage, and the quiet confidence of someone "
   "who has seen the design beneath their own life."),
}
