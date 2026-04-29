# ClaudeSkills

A Claude Code [plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces) of opinionated, production-tested skills.

Each plugin packages a Claude [skill](https://docs.claude.com/en/docs/claude-code/skills) — domain knowledge, workflows, and templates Claude loads on demand to extend its behavior without modifying the model.

---

## Install the marketplace

> ⚠ **`/plugin ...` is a Claude Code slash command — it only works INSIDE Claude Code, not in PowerShell, bash, cmd, or zsh.**

### Where to type the slash command

| You're using...                     | What to do                                                                                                  |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **VS Code extension**               | Just type the command **as a chat message** to Claude in the Claude Code panel. No terminal needed.         |
| **Standalone Claude Code CLI**      | Run `claude` in your terminal first to open the REPL, then type the command at the Claude Code prompt.      |
| **Claude Code in JetBrains / web**  | Same as VS Code — type the command in the chat panel.                                                       |

### Don't have the CLI installed?

If `claude` isn't recognized in your terminal, you don't have the standalone CLI. **You don't need it if you're using the VS Code extension** — just chat with Claude in the panel. To install the CLI anyway:

```powershell
# Cross-platform via npm (requires Node.js — install from nodejs.org first if needed)
npm install -g @anthropic-ai/claude-code
```

Or download the official installer from [claude.com/download](https://claude.com/download).

### The two slash commands

```text
/plugin marketplace add Krupesh9/ClaudeSkills
/plugin install powerapps-codeapp-setup@claudeskills
```

> **About the URL form:** Use the org/repo shorthand `Krupesh9/ClaudeSkills` — **not** the GitHub web URL `https://github.com/Krupesh9/ClaudeSkills/tree/main/...`. The `tree/main` path is a browser view, not a Git endpoint, and `/plugin marketplace add` will fail with "repository not found".

---

## Plugins in this marketplace

### powerapps-codeapp-setup

Scaffold a complete, deployable Power Apps Code App from a short interactive intake. Generates the full React + TypeScript + Vite + Tailwind skeleton, wires up SharePoint / Office 365 Users / Outlook connectors, and walks you through `pac auth → npm run setup → npm run connect → npm run push`. Encodes the silent-failure gotchas around SharePoint Choice and Person field writes that cost real engineering hours to discover.

**Reference apps built with these patterns:**

![App Inventory dashboard](powerapps-codeapp-setup/skills/powerapps-codeapp-setup/examples/PowerApp-AppInventory.png)

![Approval Tracker dashboard](powerapps-codeapp-setup/skills/powerapps-codeapp-setup/examples/ApprovalApp-Dashboard.png)

> **Reference repo:** [github.com/Krupesh9/CodeApps](https://github.com/Krupesh9/CodeApps) — source for App Inventory Tracker and Approval Tracker.

```bash
/plugin install powerapps-codeapp-setup@claudeskills
```

[→ Open the plugin](powerapps-codeapp-setup/)

**Triggers on:** `/setup`, "build me a code app", "scaffold a Power Apps code app", "wire up SharePoint", "connect to Dataverse / Office 365".

---

### the-honest-astrologer

A senior Vedic astrologer with 50+ years of grounded, plain-language wisdom. Generates birth chart visuals in four styles (Western circular, North Indian diamond, South Indian square, Chinese zodiac), runs full kundali matching (Ashtakoota + Manglik + Dasha + planetary friendship), and ends every reading with a reality-check section so you can verify it against your real life. Refuses medical, legal, crisis, and harm-related questions.

![The Honest Astrologer preview](the-honest-astrologer-skill/skills/the-honest-astrologer/the-honest-astrologer-preview.png)

**Sample chart outputs:**

- [Western circular](the-honest-astrologer-skill/skills/the-honest-astrologer/examples/sample-chart-western.png)
- [North Indian diamond](the-honest-astrologer-skill/skills/the-honest-astrologer/examples/sample-chart-north-indian.png)
- [South Indian square](the-honest-astrologer-skill/skills/the-honest-astrologer/examples/sample-chart-south-indian.png)
- [Chinese zodiac](the-honest-astrologer-skill/skills/the-honest-astrologer/examples/sample-chart-chinese-zodiac.png)

**Two ways to use it:**

```bash
# Option A — Install as a plugin (full chart computation + PNG/PDF rendering)
/plugin install the-honest-astrologer@claudeskills

# Option B — Just paste a prompt (zero install, works in Gemini Gem / Claude Project / ChatGPT / any LLM)
```

→ [PROMPT.md](the-honest-astrologer-skill/PROMPT.md) has copy-paste prompts for Gemini Gem, Claude Project, ChatGPT Custom GPT, Claude Code, and generic LLMs.

[→ Open the plugin](the-honest-astrologer-skill/)

**Triggers on:** astrology reading, kundali analysis, birth chart, horoscope, marriage compatibility, kundali matching, Chinese zodiac.

---

## Repository structure

```text
ClaudeSkills/
├── .claude-plugin/
│   └── marketplace.json              # Marketplace listing (one entry per plugin)
├── powerapps-codeapp-setup/          # Plugin folder
│   ├── .claude-plugin/
│   │   └── plugin.json               # Plugin manifest
│   ├── README.md                     # Plugin-level docs (install + overview)
│   └── skills/
│       └── powerapps-codeapp-setup/
│           ├── SKILL.md
│           ├── BLUEPRINT.md          # Quick reference
│           ├── blueprint/
│           │   └── POWERAPP-CODE-APP-BLUEPRINT.md   # Canonical full blueprint
│           ├── templates/
│           ├── checklists/
│           └── examples/
├── the-honest-astrologer-skill/      # Plugin folder
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── README.md                     # Install + overview
│   ├── PROMPT.md                     # Copy-paste prompts (no install required)
│   └── skills/
│       └── the-honest-astrologer/
│           ├── SKILL.md
│           ├── examples/             # Sample chart outputs
│           └── scripts/              # Python: compute_chart, chart_renderer, compatibility
├── README.md                         # This file
└── LICENSE
```

## Manual install (without `/plugin`)

For environments without the plugin manager, copy any skill folder into your skills directory:

```bash
git clone https://github.com/Krupesh9/ClaudeSkills.git

# Both plugins follow the same nested skills/ layout
cp -r ClaudeSkills/powerapps-codeapp-setup/skills/powerapps-codeapp-setup ~/.claude/skills/
cp -r ClaudeSkills/the-honest-astrologer-skill/skills/the-honest-astrologer ~/.claude/skills/
```

## No-install option (the-honest-astrologer only)

Some skills are pure persona / instructions and have no scripts to run — those work great as paste-in prompts for any LLM. The astrologer skill ships [PROMPT.md](the-honest-astrologer-skill/PROMPT.md) with ready-to-go versions for **Gemini Gem**, **Claude Project**, **ChatGPT Custom GPT**, **Claude Code one-shot**, and **generic LLMs**. Open the file, copy the block, paste into your tool's instructions field.

The PowerApps plugin needs the install path — its templates and scripts can't be copy-pasted into a chat.

## Contributing

Skills and plugins in this repository are works in progress. Open an issue or PR with suggestions.

## License

Released under the [MIT License](LICENSE).
