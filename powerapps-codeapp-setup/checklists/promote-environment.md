# Checklist — Promote DEV → TEST → PROD

Each environment is a fresh setup. The app ID, connection IDs, and SP site URLs all change.

## Pre-flight
- [ ] Get target env values from IT: `PP_ENVIRONMENT_ID`, SP site URL, list names if different
- [ ] Confirm target environment has the connectors you need (SharePoint, O365 Users, O365 Outlook)
- [ ] Confirm target SharePoint lists exist with the same columns (or note any schema drift)

## Auth + reconfigure
- [ ] `pac auth create --environment <NEW_PP_ENVIRONMENT_ID>`
- [ ] `pac auth list` — confirm new env is selected
- [ ] Update `.env`:
  - `VITE_SP_SITE_URL` — new site URL
  - `VITE_SP_LISTS` — confirm names match
  - `VITE_PP_ENVIRONMENT_ID` — new env ID
  - `VITE_APP_ENV_LABEL` — TEST or PROD
  - clear `VITE_APP_ID` (will be regenerated)
  - clear all `*_CONNECTION_ID` values (will be regenerated)
- [ ] Update `power.config.json`:
  - `environmentId` — new env ID
  - `appId` — empty string (will be regenerated)

## Re-init
- [ ] `npm run setup` — generates new app ID
- [ ] Patch `.env` with new `VITE_APP_ID`
- [ ] `npm run connect` — pick new env's connections
- [ ] `npm run build && npm run push`

## Smoke test
- [ ] Open in PA player in target env
- [ ] BackendBadge shows "SharePoint"
- [ ] CRUD round-trip works
- [ ] If email/deep-link configured: deep link from email points to the new env's app URL (because `VITE_APP_ID` and `VITE_PP_ENVIRONMENT_ID` are baked in at build time)
