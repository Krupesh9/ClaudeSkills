# Checklist — New Project

Run through this in order. Do not skip steps.

## Pre-flight
- [ ] Intake answered (project name, env ID, SP site, lists, columns, connectors, features)
- [ ] User confirmed plan (don't write files until they say "go")
- [ ] PowerShell or bash available
- [ ] `pac` CLI installed (`pac --version`)
- [ ] Node 20+ installed (`node --version`)

## Scaffold
- [ ] Create project folder (kebab-case)
- [ ] Write `package.json`, `vite.config.ts`, `tsconfig.app.json`, `tsconfig.json`
- [ ] Write `.env.example` and `.env` (with placeholders the user must fill)
- [ ] Write `power.config.json` (env ID set, appId blank)
- [ ] Write `src/config.ts`, `src/main.tsx`, `src/App.tsx`, `src/index.css`
- [ ] Write `src/services/dataService.ts` — customize spToRecord + buildPayload for the user's lists
- [ ] Write `src/types/myTypes.ts` — match the user's data model
- [ ] Write `src/store/appStore.ts`
- [ ] Write `src/components/Toast.tsx`, `src/components/BackendBadge.tsx`
- [ ] Write `src/hooks/useDebounce.ts`, `useChoiceOptions.ts`, `useFilteredData.ts`, `useMyData.ts`
- [ ] Write `scripts/setup.js`, `scripts/connect.js`, `scripts/lib/*`, `scripts/connectors/*`
- [ ] Add `.gitignore` excluding `.env`, `power.config.json`, `node_modules`, `dist`, `.power`

## Auth + setup
- [ ] `pac auth create --environment <PP_ENVIRONMENT_ID>`
- [ ] `npm install`
- [ ] `npm run setup` — verify `appId` lands in `power.config.json`
- [ ] Patch `.env` with `VITE_APP_ID=<from power.config.json>`

## Wire data sources
- [ ] `npm run connect`
- [ ] Confirm `src/generated/services/<List>Service.ts` exists for each list
- [ ] Confirm `.env` has connection IDs filled in

## Build + push
- [ ] `npm run build` — should compile without errors
- [ ] `npm run push` — app appears in `make.powerapps.com`
- [ ] Open in PA player → BackendBadge shows "SharePoint"
- [ ] Smoke-test: create record → refresh → edit → delete → verify in SharePoint list

## If verification reads warn "did not persist"
- [ ] Check `.power/schemas/sharepointonline/<list>.Schema.json` for actual field write permissions
- [ ] Confirm Choice fields are written as `{ Value: "..." }`
- [ ] Confirm Person fields contain only `@odata.type` + `Claims`
- [ ] Confirm connection account has Contribute access on the SP list
