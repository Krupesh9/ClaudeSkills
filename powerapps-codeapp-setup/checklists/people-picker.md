# Checklist — Add People Picker (Office 365 Users)

Use when any list has a Person column.

## Pre-flight
- [ ] Office 365 Users connection exists in target environment (create in `make.powerapps.com` → Connections if not)

## Wire connector
- [ ] Set `VITE_O365U_ENABLED=true` in `.env`
- [ ] `npm run connect` — script will pick up the new connector
- [ ] Confirm `src/generated/services/Office365UsersService.ts` exists
- [ ] Confirm `.env` has `VITE_O365U_CONNECTION_ID=<id>`

## Code
- [ ] Confirm `src/services/userService.ts` is present (it's in base scaffold)
- [ ] Confirm `src/components/PeoplePicker.tsx` is present
- [ ] In your form component, use `<PeoplePicker value={...} onChange={...} />`
- [ ] On save, pass `value.email` into `buildPayload()` so Person field gets `Claims: 'i:0#.f|membership|<email>'`
- [ ] Test: search for a colleague by name → select → save → reload → confirm Person field populates correctly in SP

## Local dev
- [ ] Add your team members to `SAMPLE_USERS` in `userService.ts` so the search works without the connector live
