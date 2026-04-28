# Checklist — Add Deep Linking

Lets emails / shared URLs open the app directly to a specific record.

## Pre-flight
- [ ] `VITE_APP_ID` filled in `.env` (from `power.config.json` after `npm run setup`)
- [ ] `VITE_PP_ENVIRONMENT_ID` filled in `.env`

## Code
- [ ] In `App.tsx`, the `useEffect` deep-link handler is already wired in the base scaffold. Confirm it logs `[DeepLink] recordId: <id>` when you visit `/?recordId=abc`.
- [ ] Replace the `console.log('[DeepLink] recordId:', recordId)` with your store/router call to navigate to detail view, e.g.:
  ```typescript
  if (recordId) {
    useAppStore.getState().setSelectedId(recordId);
  }
  ```
- [ ] In email templates, `buildDeepLink(record.id)` produces:
  ```
  https://apps.powerapps.com/play/e/{envId}/a/{appId}?recordId={id}
  ```

## Test
- [ ] Locally: open `http://localhost:3000/?recordId=<known-id>` → app navigates to that record's detail
- [ ] In PA player: paste the full deep-link URL into a new browser tab → confirm it opens detail view
