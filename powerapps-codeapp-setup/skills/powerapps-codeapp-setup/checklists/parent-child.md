# Checklist — Parent-Child Lists (e.g., Requests + Actions)

For approval flows, comment threads, audit trails. The pattern: parent list holds the record, child list holds the actions/comments scoped by `RequestId` (text column matching parent's ID).

## SharePoint setup
- [ ] Parent list exists (e.g., `Requests`)
- [ ] Child list exists (e.g., `RequestActions`) with these columns:
  - `Title` — short label of the action
  - `RequestId` — text, holds the parent record ID
  - `Action` — Choice (Submitted, Approved, Rejected, Commented, Reassigned)
  - `ActionBy` — text (display name)
  - `ActionByEmail` — text (email)
  - `Comment` — multi-line plain text
- [ ] Add child list to `VITE_SP_LISTS=Requests,RequestActions` in `.env`
- [ ] `npm run connect` — confirm `src/generated/services/RequestActionsService.ts` exists

## Code
- [ ] In `types/myTypes.ts`, add an `Action` interface
- [ ] In `dataService.ts`, add:
  - `spActionToRecord()` — Choice fields extract `.Value`
  - `getActions(requestId)` — filter `RequestId eq '<id>'`, sort by `Created desc`
  - `createAction(record)` — also cascades parent status update on Approved/Rejected
- [ ] After creating a cascading action, fire-and-forget the appropriate email notification
- [ ] Add `<ActionTimeline actions={actions} />` to your detail view (template already provided)

## Cascade gotchas
- [ ] SharePoint has **no cascade delete** — when deleting a parent, also delete child records (or accept orphans)
- [ ] When the cascade status update fails, do not roll back the action — log and surface a warning toast
