# powerapps-codeapp-setup

A Claude skill that scaffolds a complete, deployable Power Apps Code App from a short interactive intake.

## What it does

When you invoke `/setup` (or ask Claude to "build me a Power Apps code app", "scaffold a code app", "wire up SharePoint", etc.), Claude will:

1. Walk you through a structured intake — project name, environment, SharePoint lists, columns, connectors, features.
2. Confirm the plan back to you in plain language.
3. Generate the full project skeleton: `package.json`, Vite + Tailwind config, `src/config.ts`, `dataService.ts`, hooks, store, components, scripts.
4. Walk you through the CLI commands: `pac auth create`, `npm run setup`, `npm run connect`, `npm run build && npm run push`.
5. Offer add-on recipes: People Picker, email notifications, deep linking, parent-child lists, environment promotion.

The skill is opinionated. It encodes the patterns from real production Code Apps (App Inventory Tracker, Approval Tracker) and the silent-failure gotchas around SharePoint Choice and Person field writes that cost real engineering hours to discover.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The skill itself — workflow, intake, key patterns |
| `BLUEPRINT.md` | Deep reference: SP field types, write gotchas, multi-list patterns |
| `templates/` | Drop-in project files (config, services, hooks, components, scripts) |
| `checklists/` | Phase checklists (new project, people picker, notifications, deep linking, parent-child, env promotion) |

## Installation

Copy or symlink this folder into your skills directory:

```bash
# Project-scoped
cp -r powerapps-codeapp-setup /path/to/your-project/.claude/skills/

# User-scoped (all projects)
cp -r powerapps-codeapp-setup ~/.claude/skills/
```

Claude will discover it automatically by description match. You can also invoke it explicitly with `/setup` once it's installed.

## Conventions enforced

- React 18 + TypeScript strict mode + Vite 6
- Tailwind CSS only (no CSS modules, no MUI/Ant Design)
- TanStack Query for SP data
- Zustand for client UI state
- `npx power-apps` (not `pac code`) for all code-app commands
- Choice fields written as `{ Value: "..." }` on UPDATE
- Person fields written with only `@odata.type` + `Claims`
- Verification reads after every write
- `import.meta.env` only in `src/config.ts`
- Connection IDs in `.env` only — never hardcoded
- Fire-and-forget notifications with `.catch(() => {})`

## License

Released under the [MIT License](../LICENSE).
