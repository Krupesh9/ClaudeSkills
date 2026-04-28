# ClaudeSkills

A collection of [Claude Skills](https://docs.claude.com/en/docs/claude-code/skills) for use with Claude Code, the Claude Agent SDK, and other Claude-powered environments.

## What are Skills?

Skills are reusable, self-contained instructions that give Claude specialized capabilities. They package domain knowledge, workflows, and conventions into a format Claude can load on demand — letting you extend Claude's behavior without modifying the underlying model.

---

## Skills in this repository

### powerapps-codeapp-setup

Scaffold a complete, deployable Power Apps Code App from a short interactive intake. Generates the full React + TypeScript + Vite + Tailwind skeleton, wires up SharePoint / Office 365 Users / Outlook connectors, and walks you through `pac auth → npm run setup → npm run connect → npm run push`. Encodes the silent-failure gotchas around SharePoint Choice and Person field writes that cost real engineering hours to discover.

> **Drop screenshots here:** add preview images to [powerapps-codeapp-setup/examples/](powerapps-codeapp-setup/examples/) to show the kind of apps this skill produces (App Inventory Tracker, Approval Tracker, etc.).

[→ Open the skill](powerapps-codeapp-setup/)

**Triggers on:** `/setup`, "build me a code app", "scaffold a Power Apps code app", "wire up SharePoint", "connect to Dataverse / Office 365".

---

### the-honest-astrologer

Acts as a senior Vedic astrologer with 50+ years of experience giving grounded, plain-language readings on career, wealth, love, marriage, family, health, and education. Generates production-quality birth chart visuals in four styles (Western circular, North Indian diamond, South Indian square, Chinese zodiac), supports compatibility checking between two people, and exports readings as PDF reports.

![The Honest Astrologer preview](the-honest-astrologer-skill/the-honest-astrologer-preview.png)

**Sample chart outputs:**

- [Western circular](the-honest-astrologer-skill/examples/sample-chart-western.png)
- [North Indian diamond](the-honest-astrologer-skill/examples/sample-chart-north-indian.png)
- [South Indian square](the-honest-astrologer-skill/examples/sample-chart-south-indian.png)
- [Chinese zodiac](the-honest-astrologer-skill/examples/sample-chart-chinese-zodiac.png)

[→ Open the skill](the-honest-astrologer-skill/)

**Triggers on:** astrology reading, kundali analysis, birth chart, horoscope, marriage compatibility, kundali matching, Chinese zodiac.

---

## Repository Structure

Each skill lives in its own folder at the root of this repository. A typical skill folder contains:

- `SKILL.md` — the skill definition (YAML frontmatter + instructions Claude follows)
- `README.md` — human-facing overview and usage notes
- `templates/` — optional drop-in files for projects the skill scaffolds
- `scripts/` — optional helper scripts the skill may invoke
- `examples/` — optional reference material or sample outputs (screenshots, PDFs)
- `checklists/` — optional phase-by-phase checklists for multi-step skills

## Usage

To use a skill from this repository with Claude Code, copy or symlink the skill folder into one of:

- `~/.claude/skills/` — available across all projects
- `<project>/.claude/skills/` — scoped to a single project

Claude will discover the skill automatically and may invoke it when its description matches the task at hand. You can also invoke a skill explicitly by name.

## Contributing

Skills in this repository are works in progress. Feel free to fork, adapt, or open issues with suggestions.

## License

Released under the [MIT License](LICENSE).
