# The Honest Astrologer 🔭

A Vedic astrology skill for Claude — built on the Parashara framework with strict realism guardrails, production-quality chart visuals, full kundali-matching support, and an optional Chinese zodiac lens for cross-cultural readings.

> Not flattery. Not fear-mongering. Not gemstone-selling. Just an honest reading of what your chart suggests and what to do about it.

## What's New in v3

- 🎨 **Production-quality chart visuals** designed by treating each chart as a print-ready deliverable: refined modern aesthetic, generous canvas, element-based color system (Fire = warm coral, Earth = sage green, Air = soft gold, Water = cool blue), classical zodiac glyphs, multi-language labels (English + Devanagari Sanskrit + element name), self-explanatory bottom legend
- 🐉 **Chinese zodiac year-sign card** as an optional cultural lens — large hanzi character, animal name, element + Yin/Yang, plain-English strengths and watchouts, 12-animal grid
- 💞 **Compatibility / Kundali Matching** — full Ashtakoota (36-point Guna Milan), Manglik check, Dasha overlap, planetary friendship, practical commentary, optional Chinese zodiac compatibility for cross-cultural pairings
- 📄 **PDF export** for readings + charts (printable, professional, nothing cut off)
- 📊 **D1, D9 (Navamsa), and Moon (Chandra) charts** all generated
- ✅ **Reality-check section** at the end of every reading — testable predictions, not vague claims
- 🛡️ Honest Manglik framing that actively counters the harm the traditional "Manglik causes early death" narrative has done to real marriages

## What It Does

Acts as a senior Vedic astrologer with 50+ years of experience who:
- Asks for birth details (date, time, place) and what's on your mind
- Asks 2-4 clarifying questions before reading
- Delivers a plain-language reading on career, wealth, love, marriage, family, health, or education
- For compatibility: takes both partners' details and gives full Vedic matching analysis (with Chinese zodiac add-on for cross-cultural pairings)
- Generates beautiful, printable birth chart visuals — Western circular wheel (default), North Indian diamond, or South Indian square
- Optionally adds a Chinese zodiac year-sign card
- Gives a 3-5 year outlook + a clear short-term action plan
- Ends every reading with a "how to test this in your real life" section
- Refuses medical, legal, crisis, and harm-related questions and redirects you to real professionals
- Defaults to chat conversation; offers PDF export at the end

## What It Won't Do

- Predict exact dates of marriage, death, or illness
- Recommend gemstones or expensive remedies as magic fixes
- Replace your doctor, lawyer, therapist, or financial advisor
- Tell you your fate is fixed (it isn't — astrology is a mirror, not a map)
- Give a binary "compatible / not compatible" verdict on a kundali match

## Installation

### As a Claude.ai Skill
1. Download `SKILL.md`
2. Go to Claude.ai → Settings → Capabilities → Skills → Upload
3. Activate "The Honest Astrologer"
4. Start a conversation: *"I want a reading from The Honest Astrologer."*

### As a Claude Code Skill
1. Clone this repo into your skills directory:
   ```bash
   git clone https://github.com/<your-username>/the-honest-astrologer.git ~/.claude/skills/the-honest-astrologer
   ```
2. Install Python dependencies:
   ```bash
   pip install pyswisseph cairosvg
   ```
3. Install fonts for proper multi-script rendering:
   ```bash
   # Debian/Ubuntu
   sudo apt-get install fonts-noto-cjk fonts-noto-cjk-extra fonts-noto-color-emoji \
                        fonts-noto fonts-lohit-deva fonts-dejavu

   # macOS
   brew install --cask font-noto-sans-cjk font-noto-serif-cjk font-noto-sans-devanagari font-dejavu
   ```
4. The skill auto-loads in Claude Code sessions and uses the included scripts for chart computation, rendering, and compatibility analysis.

## What's Inside

```
the-honest-astrologer/
├── SKILL.md                      # Core skill definition (Claude.ai + Claude Code)
├── README.md                     # This file
├── examples/                     # Sample chart outputs in all four styles
│   ├── sample-chart-western.pdf
│   ├── sample-chart-western.png
│   ├── sample-chart-north-indian.pdf
│   ├── sample-chart-north-indian.png
│   ├── sample-chart-south-indian.pdf
│   ├── sample-chart-south-indian.png
│   ├── sample-chart-chinese-zodiac.pdf
│   └── sample-chart-chinese-zodiac.png
└── scripts/
    ├── compute_chart.py          # Vedic chart computation (Lahiri ayanamsa)
    ├── chart_renderer.py         # SVG/PNG/PDF rendering — refined modern, 4 styles
    └── compatibility.py          # Ashtakoota + Manglik + Dasha + friendship
```

## Example Questions It's Built For

**Single-person:**
- "Should I stay at my job or start a business?"
- "When will I get married?"
- "I'm thinking of moving abroad — does my chart support it?"
- "My child is choosing between engineering and design. Any insight?"
- "I've been restless at work. Is it time for a change?"

**Compatibility:**
- "Can you check kundali matching with this person?"
- "We're considering an arranged match — give me an honest read."
- "I'm Indian, my fiancée is Chinese-American — can you read both systems?"
- "What's the long-term compatibility look like for us?"
- "Is the Manglik issue something we should worry about?"

## Example Questions It Will Refuse

- Medical predictions ("Will I get cancer?")
- Crisis questions ("Should I end my life?")
- Legal outcomes ("Will I win this lawsuit?")
- Predictions about another person's death
- Black magic, curses, possession
- Anything seeking to harm someone else
- Compatibility readings where the user is in clear danger

In each case, it kindly explains why and points you to the right professional.

## Design Philosophy

Most public astrology is either *flattery* ("You're a special star-child!") or *fear* ("Saturn is destroying your life — buy this gemstone for $499!"). Both are dishonest.

This skill is built on a different premise: **a chart shows tendencies, not destinies.** A good astrologer is closer to a thoughtful family elder than a fortune-teller. The honest reading often is: *"Here's the pattern. Here's what usually happens with this pattern. Here's what you can do about it. The rest is up to your effort and choices."*

For compatibility, the same principle applies. Traditional kundali matching has caused real harm — broken marriages, families pressured by Manglik fears, couples judged by a 36-point score that was never meant to be a verdict. This skill uses the same classical framework, but tells you the truth about what each part actually means and what it doesn't.

The visual design follows the same philosophy: classical glyphs (♈♉♊...) treated typographically, an element-based color palette that's *meaningful* rather than decorative (Fire/Earth/Air/Water is the actual underlying structure of the zodiac), generous whitespace, and a bottom legend that teaches the user something true about the system. Charts are designed to be saved, printed, and shared — they should look at home in a LinkedIn post, a family WhatsApp group, or framed on a wall.

## Try It on a Test Chart

Once installed, you can test with sample data:
```bash
# Vedic chart (Western style)
python scripts/compute_chart.py --date 1987-02-09 --time 21:00 --lat 22.75 --lon 72.68 --tz 5.5 > /tmp/chart.json
python scripts/chart_renderer.py --chart-json /tmp/chart.json --style western --output /tmp/chart.pdf

# Same chart, North Indian style
python scripts/chart_renderer.py --chart-json /tmp/chart.json --style north --output /tmp/chart_north.pdf

# Chinese zodiac year-sign
python scripts/chart_renderer.py --year 1987 --month 2 --day 9 --style chinese --output /tmp/chinese.pdf

# Compatibility
python scripts/compute_chart.py --date 1990-06-15 --time 14:30 --lat 23.0 --lon 72.6 --tz 5.5 > /tmp/partner.json
python scripts/compatibility.py --chart1 /tmp/chart.json --chart2 /tmp/partner.json --name1 "Person A" --name2 "Person B"
```

## Credits

Astronomical calculations via [pyswisseph](https://github.com/astrorigin/pyswisseph).
SVG-to-PDF/PNG rendering via [cairosvg](https://cairosvg.org/).
Multi-script font support via Google's [Noto](https://fonts.google.com/noto) family and [DejaVu Fonts](https://dejavu-fonts.github.io/).
Built using Anthropic's Claude.

## License

MIT — use freely. Attribution appreciated, not required. Forks for genuine improvement (better Sanskrit translations, full Bazi/Four Pillars Chinese system, additional chart divisional types, regional variants) are very welcome.

## Roadmap

- v4 candidates: full Bazi (Four Pillars) Chinese system as a separate flow, divisional charts beyond D1/D9 (D10 for career, D7 for children, etc.), Western tropical zodiac as an alternative to sidereal Vedic, transit reports

---

*This skill is for thoughtful astrological reflection. It is not a substitute for professional medical, legal, financial, or psychological advice in any domain.*
