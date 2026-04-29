# Checklist — SharePoint Schema Design (Phase 1.5)

Run this BEFORE Phase 2 (plan confirmation) and BEFORE Phase 3 (scaffolding). The schema is the contract — get it right first.

## Identify the entities

- [ ] List every "thing" the app tracks (e.g., Requests, Apps, Projects, Tickets) — these become parent SP lists
- [ ] List every "log of something that happens to a thing" (e.g., RequestActions, Comments, ApprovalSteps) — these become child SP lists
- [ ] List every "list of options" (Status, Priority, Category, BusinessUnit, Department, ActionType) — these go into a single Config table

## Always include the Config table

- [ ] Recommend a Config table with columns: `Title`, `Value`, `Category`, `IsActive`, `SortOrder`, `Description`
- [ ] Pre-seed the Config table with the user's known values (admin will populate in SP after `npm run connect`)
- [ ] Each parent/child list's "list of options" columns become Lookup → Config (not Choice)
- [ ] Confirm with user: "Any reason NOT to use Config table for [Status/Priority/Category]? Default is yes."

## For each parent list — design the columns

- [ ] `Title` (always — required by SP)
- [ ] Identify lookup-style fields → make them Lookup → Config
- [ ] Identify free-text fields → Single line or Multi-line
- [ ] Identify Person fields → flag for People Picker requirement (needs O365 Users connector)
- [ ] Identify Date fields → ISO format
- [ ] Identify Number/Currency fields
- [ ] Identify Yes/No flags
- [ ] Identify Hyperlink fields
- [ ] Reserve `Created` / `Modified` (auto by SP)

## For each child list — design the link to parent

- [ ] Add a `<Parent>Id` text column to manually link to parent.ID (SP has no relational FK)
- [ ] Add an `Action` / `Type` column as Lookup → Config
- [ ] Add `ActionBy` / `ActionByEmail` Person + Text pair (avoids needing the People Picker for purely audit fields)
- [ ] Add `Comment` multi-line text
- [ ] No cascade delete — note that child rows survive parent deletion unless explicitly cleaned up

## Process flow

- [ ] Sketch state transitions for each parent entity (e.g., Submitted → Approved/Rejected)
- [ ] For each transition, note: which list gets written, what action type, what status update cascades
- [ ] Identify trigger points for email notifications (if Outlook connector enabled)
- [ ] Identify trigger points for deep links in those emails

## Present the schema to the user

- [ ] Render every list as a markdown table (Internal Name / Display Name / SP Type / Required / Sample / Notes)
- [ ] Render the process flow as ASCII or text diagram
- [ ] Flag any silent-failure-prone columns (Choice updates, Person writes, Lookup ID pattern)
- [ ] Ask for explicit approval ("Approved" / "Change X" / "Add another list")

## After approval

- [ ] Save the schema as `docs/SCHEMA.md` in the project for the user to share with admins
- [ ] Make sure `dataService.ts` `spToRecord` and `buildPayload` match the approved schema exactly
- [ ] Make sure `configService.ts` is wired in
- [ ] Make sure all Lookup writes use `<FieldName>Id`, not `<FieldName>`
- [ ] Make sure the Config table is the FIRST list added in `VITE_SP_LISTS=Config,...`

## Common mistakes to avoid

- ❌ Using Choice columns for evolving enums (Status, Priority, Category) — use Lookup → Config
- ❌ Forgetting the Config table on small apps ("we'll add it later") — add it now, even if only one category
- ❌ Hardcoding Lookup IDs in code — always look them up by `value` in Config rows
- ❌ Writing Lookup fields with `<Field>: 42` — must be `<Field>Id: 42`
- ❌ Skipping the process flow — it surfaces missing transitions and missing notifications
