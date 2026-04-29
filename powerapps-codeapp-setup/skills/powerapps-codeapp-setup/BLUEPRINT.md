# Power Apps Code App — Reference Blueprint

This is the deep reference for the `powerapps-codeapp-setup` skill. SKILL.md covers the workflow; this file covers the gotchas and field-level details.

> **Source:** Battle-tested patterns from the App Inventory Tracker and Approval Tracker apps (Hunt Oil, 2026). Do not deviate without good reason.

---

## 1. CLI reference — pac vs npx power-apps

The `pac code *` subcommand has a known `FileNotFoundException` bug in `GetPowerAppsCliScript()`. **Use `npx power-apps *` directly for all code app operations.**

### Command mapping

| Operation | Broken (pac CLI) | Working | npm script |
|---|---|---|---|
| Init app | `pac code init` | `npx power-apps init` | `npm run setup` |
| Push build | `pac code push` | `npx power-apps push` | `npm run push` |
| Add data source | `pac code add-data-source` | `npx power-apps add-data-source` | `npm run connect` |
| Run locally | `pac code run` | `npx power-apps run` | `npm run start` |

### Flag mapping (pac → npx power-apps)

| pac CLI flag | npx power-apps flag |
|---|---|
| `--displayName` | `--display-name` |
| `--environment` | `--environment-id` |
| `--buildPath` | `--build-path` |
| `--fileEntryPoint` | `--file-entry-point` |
| `--appUrl` | `--app-url` |
| `--region` | `--cloud` |
| `-a` (apiId) | `--api-id` |
| `-c` (connectionId) | `--connection-id` |
| `-t` (table) | `--resource-name` |
| `-d` (dataset) | `--dataset` |

### Still use pac for

```bash
pac auth create --environment <ID>   # authenticate
pac auth list                        # list environments
pac connection list                  # discover connection IDs
```

### Windows libuv warning

`npm run setup` may show: `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c, line 76`

Cosmetic. The command succeeded. Verify by checking `power.config.json` for the generated `appId`.

---

## 2. SharePoint field type reference

### 2.1 Single Line of Text

| | |
|---|---|
| SP type | Single line of text |
| Read | `string` |
| Write | `string` |

```typescript
const title = sp.Title ?? '';
{ Title: 'My Value' }
```

### 2.2 Multiple Lines of Text

| | |
|---|---|
| SP type | Multiple lines of text |
| Read | `string` |
| Write | `string` |

> **Gotcha:** Rich text / large JSON may be silently truncated. For JSON storage, set the column to "Multiple lines → Plain text → Unlimited".

### 2.3 Choice (Single Select)

| | |
|---|---|
| SP type | Choice |
| Read | `{ Value: string; Id: number; "@odata.type": string }` |
| Write (CREATE) | plain string MAY work |
| Write (UPDATE) | **must** be `{ Value: "..." }` |

```typescript
// Read — always extract .Value
const status = sp.Status?.Value ?? '';

// Write — UPDATE MUST use Value object
MyListService.update(id, { Status: { Value: 'Active' } } as any)
```

> Plain-string updates return `success: true` but data does NOT persist.

### 2.4 Choice (Multi-Select)

| | |
|---|---|
| SP type | Choice (Allow multiple) |
| Read | `{ results: string[] }` or `string[]` |
| Write | semicolon-separated string |

```typescript
const categories = sp.Categories?.results ?? [];
{ Categories: 'Category1;Category2;Category3' }
{ Categories: '' }  // clear
```

### 2.5 Person (Single)

| | |
|---|---|
| SP type | Person or Group |
| Read | `{ DisplayName, Email, Claims, ... }` |
| Write | `{ '@odata.type': '#...SPListExpandedUser', Claims: 'i:0#.f|membership|email' }` |

```typescript
// Read
const devName = sp.DevelopmentPoC?.DisplayName ?? '';
const devEmail = sp.DevelopmentPoC?.Email ?? '';

// Write — ONLY @odata.type and Claims
{
  DevelopmentPoC: {
    '@odata.type': '#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser',
    Claims: 'i:0#.f|membership|user@company.com',
  },
}
```

### 2.6 Person (Multi)

| | |
|---|---|
| SP type | Person or Group (Allow multiple) |

```typescript
// Read
const stakeholders = (sp.BusinessPoC ?? []).map((p) => ({
  displayName: p.DisplayName ?? '',
  email: p.Email ?? '',
}));

// Write — TWO keys required
{
  'BusinessPoC@odata.type': '#Collection(Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser)',
  'BusinessPoC#Claims': [
    'i:0#.f|membership|user1@company.com',
    'i:0#.f|membership|user2@company.com',
  ],
}
```

### 2.7 Date / DateTime

| | |
|---|---|
| Read | ISO string |
| Write | ISO string |

```typescript
{ DueDate: '2026-04-15' }
{ DueDateTime: '2026-04-15T14:30:00Z' }
```

### 2.8 Number / Currency

| | |
|---|---|
| Read/Write | `number` |

### 2.9 Hyperlink

URL only as plain string.

```typescript
{ AppLink: 'https://apps.powerapps.com/play/my-app' }
```

### 2.10 Yes/No

```typescript
{ IsActive: true }
```

### 2.11 Lookup (single)

| | |
|---|---|
| SP type | Lookup |
| Read | `{ Id: number, Value: string, "@odata.type": string }` |
| Write | `{ <FieldName>Id: <number> }` — the lookup target's row ID, NOT the value |

```typescript
// Read
const deptName = sp.Department?.Value ?? '';
const deptId = sp.Department?.Id ?? 0;

// Write — pass the ID
{ DepartmentId: 42 }     // ✓ correct
{ Department: 'Sales' }  // ✗ silent failure — SP returns success but no persist
```

> **Critical:** read field name = column name (`Department`); write field name = column name + `Id` (`DepartmentId`). Do not write the un-suffixed name.

### 2.11b Multi-Lookup

```typescript
// Read
const tags = (sp.Tags ?? []).map((t) => ({ id: t.Id, label: t.Value }));

// Write — TWO keys required
{
  'TagsId@odata.type': '#Collection(Edm.Int32)',
  TagsId: [12, 34, 56],
}
```

### 2.11c Config table — the recommended Lookup target

For most "list of options" columns (Status, Priority, Category, BusinessUnit, Department, ActionType), prefer **Lookup → Config table** over **Choice columns**.

**Recommended Config schema:**

| Internal Name | Display Name | SP Type     | Required | Notes                                                               |
| ------------- | ------------ | ----------- | -------- | ------------------------------------------------------------------- |
| `Title`       | Title        | Single line | Yes      | Display label (e.g., "Active")                                      |
| `Value`       | Value        | Single line | Yes      | Internal stable key (e.g., `active`)                                |
| `Category`    | Category     | Choice      | Yes      | Lookup category — `Status`, `Priority`, `BusinessUnit`, `ActionType`|
| `IsActive`    | Active       | Yes/No      | Yes      | Default true. Hides from dropdowns without deleting historical refs |
| `SortOrder`   | Sort Order   | Number      | No       | Dropdown display order                                              |
| `Description` | Description  | Multi-line  | No       | Admin notes                                                         |

**Why this beats Choice columns:**

- Admins add new values without code changes (just add a row in SharePoint)
- `IsActive` flag preserves historical data while hiding the value from new selections
- `SortOrder` controls UI order without alphabetical surprises
- One Config table serves N lookup fields (filter by `Category`)
- Single source of truth — dropdowns auto-populate from cache; no enum drift across forms

**Cache strategy:** load all config rows once on app boot via TanStack Query with `staleTime: 30 * 60 * 1000` (30 min). Filter by `Category` in components to derive each dropdown's options.

**Migrating Choice → Lookup → Config:** add Config rows matching existing Choice values, add a new Lookup column pointing to Config, run a one-time script to populate the new column from the old one, then drop the old Choice column.

### 2.12 Attachments

```typescript
const hasAttachments = sp['{HasAttachments}'] ?? false;
const attachments = (sp['{Attachments}'] ?? []).map((a) => ({
  id: a.Id ?? '',
  url: a.AbsoluteUri ?? '',
  name: a.DisplayName ?? '',
}));
window.open(attachment.url, '_blank');
```

> Attachment **upload** is not supported through the SharePoint connector's standard CRUD. Workarounds: Power Automate flow, SharePoint REST API with PA auth token, or external storage.

---

## 3. Critical write gotchas

### 3.1 The generated TypeScript types are wrong

The auto-generated `MyListWrite` interface says:

```typescript
// GENERATED — WRONG for updates
interface MyListWrite {
  Status?: string;            // wrong — needs { Value: "..." }
  DevelopmentPoC?: {
    DisplayName?: string;     // read-only
    Email?: string;           // read-only
    Claims?: string;
    // ...
  };
}
```

The authoritative schema is at `.power/schemas/sharepointonline/<listname>.Schema.json`. Look for `"x-ms-permission": "read-only"` to identify properties you cannot write.

### 3.2 Person field — only 2 sub-properties are writable

| Sub-property | Permission |
|---|---|
| `@odata.type` | read-write |
| `Claims` | writable |
| `DisplayName` | **read-only** |
| `Email` | **read-only** |
| `Picture` | **read-only** |
| `Department` | **read-only** |
| `JobTitle` | **read-only** |

Including any read-only property causes the **entire** write to silently fail. No error, no warning.

### 3.3 Always verify writes

```typescript
async function updateItem(id: string, updates: Partial<MyRecord>) {
  const r = await withTimeout(MyListService.update(id, payload as any));
  if (!r.success) throw r.error;

  const verified = await spGet(id);
  if (updates.title && verified.title !== updates.title) {
    return { item: verified, verified: false, warning: 'Write did not persist.' };
  }
  return { item: verified, verified: true };
}
```

Surface the `verified` flag to the UI as a warning toast.

### 3.4 Debugging silent failures

1. Log the payload: `console.log('[DataService] UPDATE', JSON.stringify(payload, null, 2))`
2. Compare against the schema file for read-only sub-properties
3. Confirm Choice fields are `{ Value: "..." }` objects, not strings
4. Confirm connection account has Contribute access on the list
5. F12 console — look for `[DataService] UPDATE verification FAILED`

---

## 4. Backend service architecture

### 4.1 Why the localStorage fallback is necessary

The Power Apps SDK communicates via `postMessage` through `DefaultPowerAppsBridge`. When the app runs at `localhost` (not inside the PA player), the bridge never answers. A timeout + fallback prevents the UI from hanging.

### 4.2 Do NOT check `window.powerAppsBridge`

It is never set by the player. Detect reactively: try real backend, catch timeout, fall back.

### 4.3 Reactive backend state

Single source of truth in `dataService.ts`. UI subscribes via `onBackendChange` to render the BackendBadge as "SharePoint" / "Local" / "Connecting...". See `templates/src/services/dataService.ts` lines defining `_backend`, `_listeners`, `setBackend`, `getBackend`, `onBackendChange`.

### 4.4 Timeout

```typescript
const BACKEND_TIMEOUT_MS = 15_000;  // first load
function withTimeout<T>(promise: Promise<T>): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error('SP_TIMEOUT')), BACKEND_TIMEOUT_MS),
    ),
  ]);
}
```

---

## 5. Multi-list / parent-child patterns

### 5.1 ERD example

```
+----------------------+        +----------------------+
| Requests (parent)    |        | RequestActions       |
+----------------------+        +----------------------+
| ID (auto)            |--+--+--| ID (auto)            |
| Title                |  |     | Title                |
| Status (Choice)      |  +--+--| RequestId (Text)     |
| Priority (Choice)    |        | Action (Choice)      |
| Modified             |        | ActionBy (Text)      |
| Created              |        | ActionByEmail (Text) |
+----------------------+        | Comment (Multi-line) |
                                | Created              |
                                +----------------------+
```

Connect both lists with `npx power-apps add-data-source` (one call per list).

### 5.2 Cascading status update

```typescript
export async function createAction(record: Omit<Action, 'id' | 'createdOn'>) {
  // 1. Create the action
  const action = await spCreateAction(record);

  // 2. Cascade — Approved/Rejected updates parent status
  if (record.action === 'Approved' || record.action === 'Rejected') {
    try {
      await spUpdateRequest(record.requestId, { Status: { Value: record.action } });
    } catch (err) {
      console.error('[DataService] Cascade FAILED:', (err as Error).message);
    }

    // 3. Fire-and-forget notification
    notifyRequester(record.action, record.requestId, record.comment).catch(() => {});
  }

  return action;
}
```

### 5.3 No cascade delete

SharePoint has no built-in cascade delete. When deleting a parent, either delete children explicitly or accept orphans:

```typescript
export async function deleteRequest(id: string) {
  await spDeleteRequest(id);
  // Optional: query and delete child actions explicitly
  // const actions = await spGetActions(id);
  // for (const a of actions) await spDeleteAction(a.id);
}
```

---

## 6. Deep linking

URL format:
```
https://apps.powerapps.com/play/e/{envId}/a/{appId}?recordId={id}
```

Build in `emailTemplates.ts`:

```typescript
function buildDeepLink(recordId: string): string {
  if (!APP_ID || !PP_ENVIRONMENT_ID) return '';
  return `https://apps.powerapps.com/play/e/${PP_ENVIRONMENT_ID}/a/${APP_ID}?recordId=${recordId}`;
}
```

Handle on app load (`App.tsx` useEffect):

```typescript
useEffect(() => {
  handleDeepLink();
  async function handleDeepLink() {
    let recordId: string | null = null;
    try {
      const { getContext } = await import('@microsoft/power-apps/app');
      const ctx = await getContext();
      recordId = (ctx as any)?.app?.queryParams?.recordId ?? null;
    } catch {}
    if (!recordId) {
      const params = new URLSearchParams(window.location.search);
      recordId = params.get('recordId');
    }
    if (recordId) useAppStore.getState().setSelectedId(recordId);
  }
}, []);
```

---

## 7. Master gotcha list

| # | Gotcha | Where |
|---|---|---|
| 1 | Choice updates need `{ Value: "..." }` | §2.3, §3 |
| 2 | Person writes — only `@odata.type` + Claims | §2.5, §3.2 |
| 3 | Generated TS types are wrong | §3.1 |
| 4 | SP writes can return success but not persist | §3.3 |
| 5 | `window.powerAppsBridge` is undefined | §4.2 |
| 6 | Generated `dataSourceName` is lowercase | use as-is |
| 7 | `pac code *` broken — use `npx power-apps` | §1 |
| 8 | `.env` is build-time only — rebuild after edits | — |
| 9 | `.ts` extension required in imports | `import { X } from '../generated/index.ts'` |
| 10 | `SP_CONNECTOR_ID` always `shared_sharepointonline` | — |
| 11 | Claims format `i:0#.f\|membership\|email` | §2.5 |
| 12 | Multi-person needs `@odata.type` Collection | §2.6 |
| 13 | `tsconfig.app.json` must include `.power` | scaffold |
| 14 | `@microsoft/power-apps-vite` named export | `import { powerApps }` |
| 15 | `npm run setup` Windows libuv error is cosmetic | §1 |
| 16 | Notifications must be fire-and-forget | always `.catch(() => {})` |
| 17 | Deep links need APP_ID + PP_ENVIRONMENT_ID | §6 |
| 18 | SP no cascade delete | §5.3 |
| 19 | `import.meta.env` only in `config.ts` | §config |
| 20 | Never edit `src/generated/` | regenerated by `npm run connect` |
| 21 | Lookup writes need `<Field>Id`, not `<Field>` | §2.11 |
| 22 | Multi-Lookup writes need `*Id@odata.type: '#Collection(Edm.Int32)'` + `*Id: [...]` | §2.11b |
| 23 | Prefer Lookup → Config table over Choice for evolving enums | §2.11c |
| 24 | Cache Config rows once with TanStack Query (`staleTime: 30 * 60 * 1000`) | §2.11c |

---

## 8. Acknowledgments

This blueprint distills patterns from real production apps. When in doubt, the templates in `templates/` reflect the canonical implementation — copy them as-is and customize the data model.
