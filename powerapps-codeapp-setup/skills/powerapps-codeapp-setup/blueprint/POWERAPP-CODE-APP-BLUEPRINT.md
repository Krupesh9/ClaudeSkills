# Power Apps Code App — Project Blueprint v3

> **Purpose:** The definitive, battle-tested reference for building Power Apps Code Apps with React + TypeScript.
> Every section is backed by working code from the App Inventory Tracker and Approval Tracker apps.
> This is the starting point for every new CodeApps project — follow it and you won't repeat mistakes.

---

## Table of Contents

1. [Quick Start — What to fill in](#1-quick-start--what-to-fill-in)
2. [Project Scaffold](#2-project-scaffold)
3. [CLI Reference — pac vs npx power-apps](#3-cli-reference--pac-vs-npx-power-apps)
4. [Environment Configuration](#4-environment-configuration)
5. [Backend Service Pattern](#5-backend-service-pattern)
6. [SharePoint Field Type Reference](#6-sharepoint-field-type-reference)
7. [CRITICAL: Field Write Gotchas](#7-critical-field-write-gotchas)
8. [Office 365 Users Connector — People Picker](#8-office-365-users-connector--people-picker)
9. [Office 365 Outlook — Email Notifications](#9-office-365-outlook--email-notifications)
10. [Deep Linking](#10-deep-linking)
11. [Parent-Child Lists & Action History](#11-parent-child-lists--action-history)
12. [SharePoint Attachments](#12-sharepoint-attachments)
13. [Smart Auto-Connect Scripts](#13-smart-auto-connect-scripts)
14. [Reusable UI Patterns](#14-reusable-ui-patterns)
15. [Reusable Hooks & Utilities](#15-reusable-hooks--utilities)
16. [Reusable Services — Copy/Paste Ready](#16-reusable-services--copypaste-ready)
17. [CSS & Animation Library](#17-css--animation-library)
18. [Deployment Workflow](#18-deployment-workflow)
19. [Key Gotchas — Master List](#19-key-gotchas--master-list)
20. [Checklists](#20-checklists)

---

## 1. Quick Start — What to fill in

Copy and fill in before starting a new project:

```
PROJECT NAME:       <e.g. App Inventory Tracker>
APP DISPLAY NAME:   <shown in header, e.g. App Inventory>
SHAREPOINT LISTS:   <comma-separated list names, e.g. App Inventory Tracker,ApprovalActions>

SP SITE URL:        https://yourorg.sharepoint.com/sites/YourSite
PP ENVIRONMENT ID:  xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  (find it: make.powerapps.com → Settings gear → Session details → environmentId)
PP APP ID:          leave blank for new app; fill after npm run setup
ENV LABEL:          DEV | TEST | UAT | PROD

CONNECTORS NEEDED:  (check all that apply)
  [x] SharePoint (always)
  [ ] Office 365 Users (for People Picker)
  [ ] Office 365 Outlook (for email notifications)
  [ ] Dataverse

FEATURES NEEDED:    (check all that apply)
  [x] CRUD operations
  [ ] People Picker (requires O365 Users connector)
  [ ] Email notifications (requires O365 Outlook connector)
  [ ] Deep linking (pass record ID in URL)
  [ ] Parent-child lists (e.g. Requests + Actions)
  [ ] Action/comment history timeline
  [ ] Interactive dashboard charts (clickable donut filters)
  [ ] CSV export
  [ ] Toast notifications
```

---

## 2. Project Scaffold

### 2.1 Create project

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app
```

### 2.2 Install dependencies

```bash
# Core
npm install zustand @microsoft/power-apps@latest @tanstack/react-query

# Styling
npm install tailwindcss @tailwindcss/vite

# Dev
npm install -D @microsoft/power-apps-vite @types/node
```

### 2.3 npm scripts (package.json)

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "push": "power-apps push",
    "start": "power-apps run",
    "setup": "node scripts/setup.js",
    "connect": "node scripts/connect.js"
  }
}
```

### 2.4 vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { powerApps } from '@microsoft/power-apps-vite';  // NAMED export, not default

export default defineConfig({
  plugins: [react(), tailwindcss(), powerApps()],
  server: { port: 3000 },
});
```

### 2.5 tsconfig.app.json — must include `.power`

```json
{
  "include": ["src", ".power"]
}
```

The `.power` directory contains `dataSourcesInfo.ts` which is imported by the generated services. Without this, TypeScript will error on the import path.

### 2.6 Required file structure

```
my-app/
├── .env                          ← environment values (gitignored)
├── .env.example                  ← committed template
├── power.config.json             ← app config (gitignored)
├── DEPLOYMENT.md                 ← deployment guide
├── scripts/
│   ├── setup.js                  ← npm run setup
│   ├── connect.js                ← npm run connect
│   ├── lib/
│   │   ├── env-parser.js
│   │   ├── pac-connections.js
│   │   └── prompt.js
│   └── connectors/
│       ├── registry.js
│       ├── sharepoint.js
│       ├── office365users.js     ← if People Picker needed
│       └── office365outlook.js   ← if email notifications needed
├── src/
│   ├── config.ts                 ← ONLY file that reads import.meta.env
│   ├── services/
│   │   ├── dataService.ts        ← SP + localStorage fallback (CRUD)
│   │   ├── userService.ts        ← O365 Users search + current user
│   │   ├── notificationService.ts← email orchestration (if needed)
│   │   └── emailTemplates.ts     ← HTML templates with deep links (if needed)
│   ├── store/
│   │   └── appStore.ts           ← Zustand (client-side UI state)
│   ├── hooks/
│   │   ├── useMyData.ts          ← TanStack Query hooks (server state)
│   │   ├── useFilteredData.ts    ← client-side filtering/sorting/search
│   │   ├── useChoiceOptions.ts   ← extract unique values for dropdowns
│   │   └── useDebounce.ts        ← debounce hook
│   ├── components/
│   │   ├── Layout.tsx            ← header + nav
│   │   ├── Dashboard.tsx         ← stat cards + interactive charts
│   │   ├── AppCard.tsx           ← data card + skeleton
│   │   ├── AppTable.tsx          ← sortable table
│   │   ├── AppForm.tsx           ← add/edit slide-over form
│   │   ├── DetailDrawer.tsx      ← read-only detail slide-over
│   │   ├── DeleteDialog.tsx      ← confirm delete modal
│   │   ├── FilterPanel.tsx       ← sidebar + mobile filter sheet
│   │   ├── PeoplePicker.tsx      ← O365 user search (if needed)
│   │   ├── ActionTimeline.tsx    ← comment/action history (if needed)
│   │   └── Toast.tsx             ← toast notification stack
│   ├── types/
│   │   └── myTypes.ts            ← app-level TypeScript interfaces
│   ├── generated/                ← DO NOT HAND-EDIT (auto-generated)
│   │   ├── index.ts
│   │   ├── services/
│   │   └── models/
│   └── App.tsx
├── .power/
│   └── schemas/appschemas/
│       └── dataSourcesInfo.ts    ← auto-generated connection metadata
└── docs/
    └── GOVERNANCE.md
```

---

## 3. CLI Reference — pac vs npx power-apps

The `pac code *` subcommand has a known `FileNotFoundException` bug in `GetPowerAppsCliScript()`.
**Use `npx power-apps *` directly for all code app operations.**

### Command mapping

| Operation | Broken (pac CLI) | Working (npx power-apps) | npm script |
|-----------|------------------|--------------------------|------------|
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

### pac CLI — still needed for

```bash
pac auth create --environment <ID>   # authenticate
pac auth list                        # list environments
pac connection list                  # discover connection IDs
```

### Known Windows issue

`npm run setup` may show: `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c, line 76`

This is a Node.js libuv bug on Windows. **The command succeeds despite the error.** Check `power.config.json` for the generated `appId` to confirm.

---

## 4. Environment Configuration

### 4.1 config.ts — the ONLY file that reads import.meta.env

```typescript
// src/config.ts
// ─────────────────────────────────────────────────────────────────────────────
// Centralized environment configuration.
// This is the ONLY file that reads import.meta.env.VITE_* variables.
// All other files import constants from here.
// ─────────────────────────────────────────────────────────────────────────────

// Backend type
export const BACKEND_TYPE     = import.meta.env.VITE_BACKEND_TYPE      ?? 'sharepoint';

// ── SharePoint ───────────────────────────────────────────────────────────────
export const SP_SITE_URL      = import.meta.env.VITE_SP_SITE_URL       ?? '';
export const SP_LISTS         = import.meta.env.VITE_SP_LISTS          ?? '';
export const SP_CONNECTOR_ID  = 'shared_sharepointonline';
export const SP_CONNECTION_ID = import.meta.env.VITE_SP_CONNECTION_ID   ?? '';

// ── Office 365 Users (for People Picker) ─────────────────────────────────────
export const O365U_ENABLED       = import.meta.env.VITE_O365U_ENABLED === 'true';
export const O365U_CONNECTION_ID = import.meta.env.VITE_O365U_CONNECTION_ID ?? '';

// ── Office 365 Outlook (for email notifications) ────────────────────────────
export const OUTLOOK_ENABLED       = import.meta.env.VITE_OUTLOOK_ENABLED === 'true';
export const OUTLOOK_CONNECTION_ID = import.meta.env.VITE_OUTLOOK_CONNECTION_ID ?? '';

// ── App identity (for deep links) ───────────────────────────────────────────
export const APP_ID            = import.meta.env.VITE_APP_ID            ?? '';
export const PP_ENVIRONMENT_ID = import.meta.env.VITE_PP_ENVIRONMENT_ID ?? '';

// ── App display ─────────────────────────────────────────────────────────────
export const APP_ENV_LABEL    = import.meta.env.VITE_APP_ENV_LABEL     ?? '';
export const APP_DISPLAY_NAME = import.meta.env.VITE_APP_DISPLAY_NAME  ?? '';
```

**Rule:** `import.meta.env.VITE_*` is used ONLY in config.ts. Every other file imports from config.ts.

### 4.2 .env (gitignored)

```dotenv
VITE_BACKEND_TYPE=sharepoint
VITE_SP_SITE_URL=https://yourorg.sharepoint.com/sites/YourSite
VITE_SP_LISTS=MyList1,MyList2
VITE_SP_CONNECTION_ID=                   # auto-populated by npm run connect
VITE_O365U_ENABLED=true
VITE_O365U_CONNECTION_ID=               # auto-populated by npm run connect
VITE_OUTLOOK_ENABLED=true
VITE_OUTLOOK_CONNECTION_ID=             # auto-populated by npm run connect
VITE_APP_ID=                            # from power.config.json after npm run setup
VITE_PP_ENVIRONMENT_ID=                 # your Power Platform environment ID
VITE_APP_ENV_LABEL=DEV
VITE_APP_DISPLAY_NAME=My App
```

### 4.3 Vite substitutes .env at BUILD time

`import.meta.env.VITE_*` variables are baked into the bundle during `npm run build`.
Changing .env after build has no effect — you must rebuild.

---

## 5. Backend Service Pattern

### 5.1 Why the fallback is necessary

The Power Apps SDK communicates via `postMessage` through `DefaultPowerAppsBridge`.
When the app runs at `localhost` (not inside the PA player), the bridge never answers.
A timeout + fallback prevents the UI from hanging.

### 5.2 NEVER check `window.powerAppsBridge`

`window.powerAppsBridge` is NEVER set by the PA player. The SDK uses its internal bridge.
Detection is done reactively: try the real backend, catch the timeout, fall back.

### 5.3 Reactive backend state — shared across all services

```typescript
// In dataService.ts — exported for use by other services and UI components
type BackendType = 'sharepoint' | 'localStorage' | 'unknown';
let _backend: BackendType = 'unknown';
const _listeners = new Set<(b: BackendType) => void>();

export function getBackend(): BackendType { return _backend; }
export function onBackendChange(fn: (b: BackendType) => void) {
  _listeners.add(fn);
  return () => { _listeners.delete(fn); };
}
function setBackend(b: BackendType) {
  if (_backend !== b) { _backend = b; _listeners.forEach((fn) => fn(b)); }
}
```

**Usage in UI:** The `BackendBadge` component subscribes to `onBackendChange()` to show "SharePoint" / "Local" / "Connecting..." in the header.

### 5.4 Timeout helper

```typescript
const BACKEND_TIMEOUT_MS = 15_000;  // 15s for first load, can reduce to 6s after confirmed

function withTimeout<T>(promise: Promise<T>): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error('SP_TIMEOUT: no response — not in PA player?')), BACKEND_TIMEOUT_MS),
    ),
  ]);
}
```

### 5.5 Write result pattern — verify every write

SharePoint writes can return `success: true` but silently fail to persist data (wrong field format, missing permissions). Always verify writes with a follow-up read:

```typescript
export interface WriteResult {
  item: MyRecord;
  verified: boolean;
  warning?: string;
}

export async function updateItem(id: string, updates: Partial<MyRecord>): Promise<WriteResult> {
  const payload = buildPayload(updates);
  console.log('[DataService] UPDATE id:', id, 'payload:', JSON.stringify(payload, null, 2));

  try {
    const result = await withTimeout(MyListService.update(id, payload as any));
    if (!result.success) throw result.error ?? new Error('Update: success=false');
    setBackend('sharepoint');

    // Verification read — check if write actually persisted
    try {
      const verified = await spGet(id);
      if (updates.title && verified.title !== updates.title) {
        console.warn('[DataService] UPDATE verification FAILED — write did not persist');
        return { item: verified, verified: false, warning: 'SharePoint returned success but data did not persist.' };
      }
      return { item: verified, verified: true };
    } catch {
      return { item: spToRecord(result.data), verified: false, warning: 'Updated but verification read failed.' };
    }
  } catch (err) {
    // Fall back to localStorage...
  }
}
```

### 5.6 localStorage fallback pattern

```typescript
const LS_KEY = 'my_app_items_v1';

function lsReadAll<T>(key: string): T[] {
  try { return JSON.parse(localStorage.getItem(key) || '[]'); } catch { return []; }
}
function lsWriteAll<T>(key: string, items: T[]) {
  try { localStorage.setItem(key, JSON.stringify(items)); } catch { /* noop */ }
}

function ensureSeeded() {
  if (lsReadAll(LS_KEY).length === 0) {
    lsWriteAll(LS_KEY, getSeedData());
  }
}
```

### 5.7 SP → App record mapping

Always map SharePoint field names to clean app-level names in a single function. This isolates the ugly SP column names (like `field_7`, `busunit`) from the rest of the app:

```typescript
function spToRecord(sp: MyListRead): MyRecord {
  return {
    id: String(sp.ID ?? ''),
    title: sp.Title ?? '',
    description: sp.field_7 ?? '',
    // Choice fields — extract .Value from the object
    businessUnit: sp.busunit?.Value ?? '',
    platform: sp.tools?.Value ?? '',
    appStatus: sp.field_5?.Value ?? '',
    // Person fields — extract .DisplayName and .Email
    developmentPoC: sp.DevelopmentPoC?.DisplayName ?? '',
    developmentPoCEmail: sp.DevelopmentPoC?.Email ?? '',
    // Dates and timestamps
    lastDeliveryDate: sp.field_9 ?? '',
    createdOn: sp.Created ?? new Date().toISOString(),
    modifiedOn: sp.Modified ?? new Date().toISOString(),
  };
}
```

### 5.8 TanStack Query hooks for CRUD (with optimistic updates + toasts)

```typescript
// src/hooks/useMyData.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getItems, createItem, updateItem, deleteItem } from '../services/dataService';
import type { WriteResult } from '../services/dataService';
import type { MyRecord } from '../types/myTypes';
import { useAppStore } from '../store/appStore';

const QUERY_KEY = ['myData'];

export function useMyData() {
  return useQuery({
    queryKey: QUERY_KEY,
    queryFn: getItems,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
  });
}

function toast(type: 'success' | 'error' | 'warning', title: string, message?: string) {
  useAppStore.getState().addToast({ type, title, message });
}

export function useCreateItem() {
  const qc = useQueryClient();
  return useMutation<WriteResult, Error, Omit<MyRecord, 'id' | 'createdOn' | 'modifiedOn'>>({
    mutationFn: (record) => createItem(record),
    onSuccess: (result) => {
      qc.invalidateQueries({ queryKey: QUERY_KEY });
      if (result.warning) toast('warning', 'Created with warning', result.warning);
      else toast('success', 'Item created', `"${result.item.title}" added successfully.`);
    },
    onError: (err) => toast('error', 'Create failed', err.message),
  });
}

export function useUpdateItem() {
  const qc = useQueryClient();
  return useMutation<WriteResult, Error, { id: string; updates: Partial<MyRecord> }>({
    // Optimistic update — instant UI feedback
    onMutate: async ({ id, updates }) => {
      await qc.cancelQueries({ queryKey: QUERY_KEY });
      const prev = qc.getQueryData<MyRecord[]>(QUERY_KEY);
      qc.setQueryData<MyRecord[]>(QUERY_KEY, (old) =>
        (old ?? []).map((item) =>
          item.id === id ? { ...item, ...updates, modifiedOn: new Date().toISOString() } : item,
        ),
      );
      return { prev };
    },
    mutationFn: ({ id, updates }) => updateItem(id, updates),
    onSuccess: (result) => {
      if (result.warning) toast('warning', 'Saved with warning', result.warning);
      else toast('success', 'Item updated', `"${result.item.title}" saved.`);
    },
    onError: (err, _vars, context) => {
      // Rollback on failure
      if (context && 'prev' in context) {
        qc.setQueryData(QUERY_KEY, (context as { prev: MyRecord[] }).prev);
      }
      toast('error', 'Update failed', err.message);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: QUERY_KEY }),
  });
}

export function useDeleteItem() {
  const qc = useQueryClient();
  return useMutation<void, Error, { id: string; title: string }>({
    onMutate: async ({ id }) => {
      await qc.cancelQueries({ queryKey: QUERY_KEY });
      const prev = qc.getQueryData<MyRecord[]>(QUERY_KEY);
      qc.setQueryData<MyRecord[]>(QUERY_KEY, (old) =>
        (old ?? []).filter((item) => item.id !== id),
      );
      return { prev };
    },
    mutationFn: ({ id }) => deleteItem(id),
    onSuccess: (_data, vars) => toast('success', 'Item deleted', `"${vars.title}" removed.`),
    onError: (err, _vars, context) => {
      if (context && 'prev' in context) {
        qc.setQueryData(QUERY_KEY, (context as { prev: MyRecord[] }).prev);
      }
      toast('error', 'Delete failed', err.message);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: QUERY_KEY }),
  });
}
```

---

## 6. SharePoint Field Type Reference

### 6.1 Single Line of Text

**SP type:** Single line of text | **Read:** `string` | **Write:** `string`

```typescript
// Read
const title = sp.Title ?? '';
// Write
{ Title: 'My Value' }
```

### 6.2 Multiple Lines of Text

**SP type:** Multiple lines of text | **Read:** `string` | **Write:** `string`

```typescript
// Read
const desc = sp.Description ?? '';
// Write
{ Description: 'Long text here...' }
```

> **Gotcha:** Rich text / large JSON may be silently truncated. Use "Multiple lines → Plain text → Unlimited" for JSON storage.

### 6.3 Choice (Single Select)

**SP type:** Choice | **Read:** `{ Value: string; Id: number; "@odata.type": string }` | **Write:** see Section 7

```typescript
// Read — Choice fields return an object, extract .Value
const status = sp.Status?.Value ?? '';

// Write for CREATE — plain string works
{ Status: 'Active' }

// Write for UPDATE — MUST use Value object (see Section 7)
{ Status: { Value: 'Active' } }
```

### 6.4 Choice (Multi-Select)

**SP type:** Choice (Allow multiple) | **Read:** `{ results: string[] }` or `string[]`

```typescript
// Read
const categories = sp.Categories?.results ?? [];
// Write — semicolon-separated string
{ Categories: 'Category1;Category2;Category3' }
// Clear
{ Categories: '' }
```

### 6.5 Person (Single Select)

**SP type:** Person or Group | **Read:** `{ DisplayName, Email, Claims, ... }` | **Write:** see Section 7

```typescript
// Read — returns object with sub-properties
const devName = sp.DevelopmentPoC?.DisplayName ?? '';
const devEmail = sp.DevelopmentPoC?.Email ?? '';

// Write — ONLY @odata.type and Claims are writable (see Section 7)
{
  DevelopmentPoC: {
    '@odata.type': '#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser',
    Claims: 'i:0#.f|membership|user@company.com',
  }
}
```

### 6.6 Person (Multi-Select)

**SP type:** Person or Group (Allow multiple)

```typescript
// Read
const stakeholders = (sp.BusinessPoC ?? []).map(p => ({
  displayName: p.DisplayName ?? '',
  email: p.Email ?? '',
}));

// Write — BOTH @odata.type declaration AND Claims array required
{
  'BusinessPoC@odata.type': '#Collection(Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser)',
  'BusinessPoC#Claims': [
    'i:0#.f|membership|user1@company.com',
    'i:0#.f|membership|user2@company.com',
  ],
}
```

### 6.7 Date / DateTime

**SP type:** Date and Time | **Read:** `string` (ISO) | **Write:** `string` (ISO)

```typescript
// Read
const date = sp.DueDate ?? '';  // "2026-04-15"
// Write
{ DueDate: '2026-04-15' }
{ DueDateTime: '2026-04-15T14:30:00Z' }
```

### 6.8 Number / Currency

**SP type:** Number or Currency | **Read/Write:** `number`

```typescript
const amount = sp.Amount ?? 0;
{ Amount: 1500.50 }
```

### 6.9 Hyperlink

**SP type:** Hyperlink or Picture | **Read/Write:** `string` (URL only)

```typescript
const link = sp.AppLink ?? '';
{ AppLink: 'https://apps.powerapps.com/play/my-app' }
```

### 6.10 Yes/No (Boolean)

**SP type:** Yes/No | **Read/Write:** `boolean`

```typescript
const isActive = sp.IsActive ?? false;
{ IsActive: true }
```

### 6.11 Lookup

**SP type:** Lookup | **Read:** `{ Id: number; Value: string }` | **Write:** `number` (target ID)

```typescript
// Read
const deptName = sp.Department?.Value ?? '';
const deptId = sp.Department?.Id ?? 0;
// Write — pass the ID, not the display value
{ DepartmentId: 42 }
```

---

## 7. CRITICAL: Field Write Gotchas

> **This section exists because of real bugs we hit.** The generated TypeScript Write types are **wrong** for Choice and Person fields. Following the generated types will result in silent write failures where SP returns `success: true` but data does not persist.

### 7.1 The generated types lie

The auto-generated `MyListWrite` interface says things like:

```typescript
// GENERATED (WRONG for updates):
interface MyListWrite {
  Status?: string;           // ← WRONG for updates — needs { Value: "..." }
  DevelopmentPoC?: {         // ← WRONG — includes read-only sub-properties
    DisplayName?: string;    // ← read-only!
    Email?: string;          // ← read-only!
    Claims?: string;
    // ...
  };
}
```

### 7.2 How to check the REAL schema

The authoritative source is the schema file at:
```
.power/schemas/sharepointonline/<listname>.Schema.json
```

Look for:
- `"IsChoice": true` — field is a Choice column
- `"x-ms-permission": "read-only"` — sub-property cannot be written
- `"x-ms-permission": "read-write"` — sub-property CAN be written

### 7.3 Choice fields — CREATE vs UPDATE

```typescript
// CREATE — plain string works for some lists
MyListService.create({ Status: 'Active' })

// UPDATE — MUST use Value object format
// If you send a plain string, SP returns success but the value does NOT change.
MyListService.update(id, {
  Status: { Value: 'Active' }  // ← THIS is what actually works
} as any)
```

**Why `as any`?** Because the generated type says `Status?: string` but the connector actually needs `{ Value: string }`. Use `Record<string, unknown>` for the payload to bypass the incorrect types.

### 7.4 Person fields — only 2 properties are writable

From the SP schema, Person field sub-properties have these permissions:
- `@odata.type` → **read-write**
- `Claims` → **writable** (not explicitly marked, but accepted)
- `DisplayName` → **read-only**
- `Email` → **read-only**
- `Picture` → **read-only**
- `Department` → **read-only**
- `JobTitle` → **read-only**

**If you send read-only properties, the entire write silently fails.** No error, no warning — the field just doesn't update.

```typescript
// WRONG — includes read-only properties, causes silent failure
{
  DevelopmentPoC: {
    '@odata.type': '#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser',
    Claims: 'i:0#.f|membership|user@company.com',
    DisplayName: 'User Name',      // ← READ-ONLY, causes failure
    Email: 'user@company.com',     // ← READ-ONLY, causes failure
    Picture: '',                    // ← READ-ONLY
    Department: '',                // ← READ-ONLY
    JobTitle: '',                  // ← READ-ONLY
  }
}

// CORRECT — only writable properties
{
  DevelopmentPoC: {
    '@odata.type': '#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser',
    Claims: 'i:0#.f|membership|user@company.com',
  }
}
```

### 7.5 The correct buildPayload pattern

Always build the write payload with `Record<string, unknown>` to bypass incorrect generated types:

```typescript
function buildPayload(
  record: Partial<Omit<MyRecord, 'id' | 'createdOn' | 'modifiedOn'>>,
): Record<string, unknown> {
  const p: Record<string, unknown> = {};

  // Text / simple fields — plain values
  if (record.title !== undefined)       p.Title = record.title;
  if (record.description !== undefined) p.field_7 = record.description;
  if (record.appLink !== undefined)     p.field_6 = record.appLink;
  if (record.dueDate !== undefined)     p.DueDate = record.dueDate;

  // Number fields
  if (record.timeFrame !== undefined && record.timeFrame !== '')
    p.field_8 = Number(record.timeFrame);

  // Choice fields — MUST be objects with { Value: "..." }
  if (record.businessUnit) p.busunit = { Value: record.businessUnit };
  if (record.platform)     p.tools  = { Value: record.platform };
  if (record.appStatus)    p.field_5 = { Value: record.appStatus };

  // Person fields — ONLY writable sub-properties
  if (record.developmentPoCEmail) {
    p.DevelopmentPoC = {
      '@odata.type': '#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser',
      Claims: `i:0#.f|membership|${record.developmentPoCEmail}`,
    };
  }

  return p;
}

// Usage in CRUD operations:
MyListService.update(id, payload as Partial<Omit<MyListWrite, 'ID'>>)
MyListService.create(payload as Omit<MyListWrite, 'ID'>)
```

### 7.6 Debugging write failures

1. **Add logging** — `console.log('[DataService] UPDATE payload:', JSON.stringify(payload, null, 2))`
2. **Verify after write** — always do a `get(id)` after update and compare values
3. **Check the schema** — read `.power/schemas/sharepointonline/<list>.Schema.json`
4. **Check permissions** — the connection account needs Contribute access on the SP list
5. **Check F12 console** — look for `[DataService] UPDATE verified successfully` vs `verification FAILED`

---

## 8. Office 365 Users Connector — People Picker

### 8.1 Adding the connector

```bash
npx power-apps add-data-source \
  --api-id shared_office365users \
  --connection-id "<O365_USERS_CONNECTION_ID>" \
  --resource-name "MyProfile"
```

### 8.2 User service (copy/paste ready)

```typescript
// src/services/userService.ts
import { Office365UsersService } from '../generated/services/Office365UsersService.ts';

export interface UserProfile {
  displayName: string;
  email: string;
  jobTitle?: string;
  id?: string;
}

const LOCAL_USER: UserProfile = {
  displayName: 'Local User',
  email: 'localuser@localhost.dev',
  jobTitle: 'Developer (Local Mode)',
};

// Add your team members here for local dev testing
const SAMPLE_USERS: UserProfile[] = [
  { displayName: 'Krupesh Patel', email: 'kpatel@huntoil.com', jobTitle: 'Developer' },
  { displayName: 'Bob Smith', email: 'bsmith@huntoil.com', jobTitle: 'Manager' },
  { displayName: 'Alice Johnson', email: 'ajohnson@huntoil.com', jobTitle: 'Director' },
];

export async function getCurrentUser(): Promise<UserProfile> {
  // 1. Try Power Apps SDK context (works inside the player)
  try {
    const { getContext } = await import('@microsoft/power-apps/app');
    const ctx = await getContext();
    if (ctx?.user?.fullName) {
      const profile: UserProfile = {
        displayName: ctx.user.fullName,
        email: ctx.user.userPrincipalName ?? '',
        id: ctx.user.objectId ?? '',
      };
      // Enrich with O365 Users (optional)
      try {
        const result = await Office365UsersService.MyProfile_V2();
        if (result.data) {
          profile.email = result.data.mail ?? result.data.userPrincipalName ?? profile.email;
          profile.jobTitle = result.data.jobTitle ?? undefined;
        }
      } catch { /* O365 enrichment is optional */ }
      return profile;
    }
  } catch { /* Not in Power Apps player */ }

  // 2. Fallback for local dev
  return LOCAL_USER;
}

export async function searchUsers(query: string): Promise<UserProfile[]> {
  if (!query || query.length < 2) return [];

  // Try O365 Users connector (searches Azure AD)
  try {
    const result = await Office365UsersService.SearchUser(query, 10);
    if (result.data && Array.isArray(result.data)) {
      return result.data
        .filter((u) => u.DisplayName && (u.Mail || u.UserPrincipalName))
        .map((u) => ({
          displayName: u.DisplayName ?? '',
          email: u.Mail ?? u.UserPrincipalName ?? '',
          jobTitle: u.JobTitle ?? undefined,
          id: u.Id,
        }));
    }
  } catch (err) {
    console.warn('[UserService] O365 search failed, using sample data:', (err as Error).message);
  }

  // Fallback: filter sample users locally
  const q = query.toLowerCase();
  return SAMPLE_USERS.filter(
    (u) => u.displayName.toLowerCase().includes(q) || u.email.toLowerCase().includes(q),
  );
}
```

### 8.3 PeoplePicker component (copy/paste ready)

```tsx
// src/components/PeoplePicker.tsx
import { useState, useRef, useEffect } from 'react';
import { searchUsers, type UserProfile } from '../services/userService';

interface PeoplePickerProps {
  value: { displayName: string; email: string } | null;
  onChange: (person: { displayName: string; email: string } | null) => void;
  placeholder?: string;
  label?: string;
  error?: string;
}

export function PeoplePicker({ value, onChange, placeholder = 'Search for a person...', label, error }: PeoplePickerProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [highlightIdx, setHighlightIdx] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  // Debounced search (300ms, 2-char minimum)
  useEffect(() => {
    if (query.length < 2) { setResults([]); setOpen(false); return; }
    setLoading(true);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      const users = await searchUsers(query);
      setResults(users);
      setHighlightIdx(0);
      setOpen(users.length > 0);
      setLoading(false);
    }, 300);
    return () => clearTimeout(debounceRef.current);
  }, [query]);

  // Close on click outside
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  function handleSelect(user: UserProfile) {
    onChange({ displayName: user.displayName, email: user.email });
    setQuery('');
    setOpen(false);
  }

  function handleClear() {
    onChange(null);
    setQuery('');
    inputRef.current?.focus();
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (!open) return;
    if (e.key === 'ArrowDown') { e.preventDefault(); setHighlightIdx((i) => Math.min(i + 1, results.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setHighlightIdx((i) => Math.max(i - 1, 0)); }
    else if (e.key === 'Enter' && results[highlightIdx]) { e.preventDefault(); handleSelect(results[highlightIdx]); }
    else if (e.key === 'Escape') setOpen(false);
  }

  const inputClass = 'w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 bg-white';

  // Selected state — show person chip
  if (value) {
    return (
      <div>
        {label && <label className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>}
        <div className={`${inputClass} flex items-center gap-2`}>
          <div className="flex items-center gap-2 bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-md flex-1 min-w-0">
            <div className="w-6 h-6 bg-indigo-200 rounded-full flex items-center justify-center text-xs font-bold shrink-0">
              {value.displayName.split(' ').map((n) => n[0]).join('')}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{value.displayName}</p>
              <p className="text-xs opacity-70 truncate">{value.email}</p>
            </div>
          </div>
          <button type="button" onClick={handleClear}
            className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100 shrink-0">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
      </div>
    );
  }

  // Search state
  return (
    <div ref={containerRef} className="relative">
      {label && <label className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>}
      <div className="relative">
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <input ref={inputRef} type="text" value={query}
          onChange={(e) => setQuery(e.target.value)} onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder={placeholder} className={`${inputClass} pl-10`} />
        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
          </div>
        )}
      </div>
      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {results.map((user, idx) => (
            <button key={user.email} type="button" onClick={() => handleSelect(user)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 text-left transition-colors ${idx === highlightIdx ? 'bg-indigo-50' : 'hover:bg-gray-50'}`}>
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 text-xs font-bold shrink-0">
                {user.displayName.split(' ').map((n) => n[0]).join('')}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{user.displayName}</p>
                <p className="text-xs text-gray-500 truncate">{user.email}{user.jobTitle ? ` · ${user.jobTitle}` : ''}</p>
              </div>
            </button>
          ))}
        </div>
      )}
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  );
}
```

### 8.4 Using PeoplePicker in forms

```tsx
const [devPoC, setDevPoC] = useState<{ displayName: string; email: string } | null>(null);

<PeoplePicker label="Development PoC" value={devPoC} onChange={setDevPoC}
  placeholder="Search by name or email..." />

// When saving — use the email for the Claims field:
const payload = buildPayload({ developmentPoCEmail: devPoC?.email ?? '' });
```

---

## 9. Office 365 Outlook — Email Notifications

### 9.1 Adding the connector

```bash
npx power-apps add-data-source \
  --api-id shared_office365 \
  --connection-id "<OUTLOOK_CONNECTION_ID>" \
  --resource-name "SendAnEmail_V2"
```

### 9.2 Notification service (copy/paste ready)

```typescript
// src/services/notificationService.ts
import { OUTLOOK_ENABLED } from '../config';
import { getBackend } from './dataService';
import { Office365OutlookService } from '../generated/services/Office365OutlookService.ts';
import { myEmail1, myEmail2, myEmail3 } from './emailTemplates';

type NotificationType = 'submitted' | 'approved' | 'rejected';

export async function sendNotification(
  type: NotificationType,
  record: MyRecord,
  comment?: string,
): Promise<void> {
  // Build the email based on notification type
  let email: { to: string; subject: string; body: string };
  switch (type) {
    case 'submitted': email = myEmail1(record); break;
    case 'approved':  email = myEmail2(record, comment ?? ''); break;
    case 'rejected':  email = myEmail3(record, comment ?? ''); break;
  }

  // Skip in local dev mode
  if (getBackend() === 'localStorage') {
    console.log(`[Notification] Would send email (${type}):`, { to: email.to, subject: email.subject });
    return;
  }

  // Skip if Outlook not enabled
  if (!OUTLOOK_ENABLED) {
    console.log(`[Notification] Outlook not enabled — skipping ${type} email`);
    return;
  }

  // Send via Office 365 Outlook connector
  try {
    await Office365OutlookService.SendEmailV2({
      To: email.to,
      Subject: email.subject,
      Body: email.body,
    });
    console.log(`[Notification] Sent ${type} email to ${email.to}`);
  } catch (err) {
    console.warn(`[Notification] Failed to send ${type} email:`, (err as Error).message);
  }
}
```

### 9.3 Email templates pattern

```typescript
// src/services/emailTemplates.ts
import { APP_ID, PP_ENVIRONMENT_ID } from '../config';

function buildDeepLink(recordId: string): string {
  if (!APP_ID || !PP_ENVIRONMENT_ID) return '';
  return `https://apps.powerapps.com/play/e/${PP_ENVIRONMENT_ID}/a/${APP_ID}?recordId=${recordId}`;
}

function actionButtonHtml(label: string, url: string, color: string): string {
  if (!url) return '';
  return `
    <div style="text-align: center; margin: 24px 0 8px;">
      <a href="${url}" target="_blank" style="display: inline-block; background: ${color}; color: #ffffff; padding: 12px 32px; border-radius: 6px; font-size: 14px; font-weight: 600; text-decoration: none;">
        ${label}
      </a>
    </div>
  `;
}

function baseTemplate(title: string, bodyHtml: string): string {
  return `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
      <div style="background: #1E3A5F; padding: 20px 24px;">
        <h1 style="margin: 0; color: #ffffff; font-size: 18px; font-weight: 600;">${title}</h1>
      </div>
      <div style="padding: 24px;">${bodyHtml}</div>
      <div style="padding: 16px 24px; background: #f9fafb; border-top: 1px solid #e5e7eb; text-align: center;">
        <p style="margin: 0; color: #9ca3af; font-size: 12px;">Sent by ${APP_DISPLAY_NAME} — Do not reply</p>
      </div>
    </div>
  `;
}

// Export one function per email type:
export function requestSubmittedEmail(request: MyRecord) {
  const deepLink = buildDeepLink(request.id);
  return {
    to: request.approverEmail,
    subject: `[${APP_DISPLAY_NAME}] Action Required: ${request.title}`,
    body: baseTemplate('New Request', `
      <p>Hi <strong>${request.approver}</strong>, you have a new request:</p>
      <!-- request details table -->
      ${actionButtonHtml('Review & Approve', deepLink, '#1E3A5F')}
    `),
  };
}
```

### 9.4 Fire-and-forget pattern

Notifications should never block the main operation. Always call with `.catch(() => {})`:

```typescript
// In dataService.ts, after creating a record:
notifyApproverOfNewRequest(item).catch(() => {});

// Lazy import to avoid circular dependencies:
async function notifyApproverOfNewRequest(request: MyRecord) {
  const { sendNotification } = await import('./notificationService');
  return sendNotification('submitted', request);
}
```

---

## 10. Deep Linking

### 10.1 How deep links work

Deep links let you open the app directly to a specific record. The URL format:

```
https://apps.powerapps.com/play/e/{envId}/a/{appId}?recordId={id}
```

### 10.2 Building deep links (for emails)

```typescript
// In emailTemplates.ts
import { APP_ID, PP_ENVIRONMENT_ID } from '../config';

function buildDeepLink(recordId: string): string {
  if (!APP_ID || !PP_ENVIRONMENT_ID) return '';
  return `https://apps.powerapps.com/play/e/${PP_ENVIRONMENT_ID}/a/${APP_ID}?recordId=${recordId}`;
}
```

### 10.3 Handling deep links on app load

```typescript
// In App.tsx — useEffect on mount
useEffect(() => {
  handleDeepLink();

  async function handleDeepLink() {
    let recordId: string | null = null;

    // 1. Try Power Apps context first (works inside the player)
    try {
      const { getContext } = await import('@microsoft/power-apps/app');
      const ctx = await getContext();
      recordId = ctx?.app?.queryParams?.recordId ?? null;
      if (recordId) console.log(`[DeepLink] Found recordId in PA context: ${recordId}`);
    } catch { /* Not in PA player */ }

    // 2. Fallback to URL search params (works in browser / npm run start)
    if (!recordId) {
      const params = new URLSearchParams(window.location.search);
      recordId = params.get('recordId');
      if (recordId) console.log(`[DeepLink] Found recordId in URL params: ${recordId}`);
    }

    // 3. Navigate to the record detail view
    if (recordId) {
      navigate('detail', recordId);  // or openDetail(recordId) depending on your store
    }
  }
}, []);
```

### 10.4 Required .env variables for deep links

```dotenv
VITE_APP_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx       # from power.config.json
VITE_PP_ENVIRONMENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  # your PP env
```

---

## 11. Parent-Child Lists & Action History

### 11.1 When to use multiple lists

Use multiple SharePoint lists when:
- Data has a parent-child relationship (e.g., Requests ↔ Actions)
- Different data entities have different permission requirements
- You need to query/filter one entity independently

### 11.2 Connecting multiple lists

Run `npx power-apps add-data-source` once per list:

```bash
# List 1: Parent
npx power-apps add-data-source \
  --api-id shared_sharepointonline \
  --connection-id "<CONNECTION_ID>" \
  --resource-name "ParentList" \
  --dataset "<SP_SITE_URL>"

# List 2: Child (Actions/Comments)
npx power-apps add-data-source \
  --api-id shared_sharepointonline \
  --connection-id "<CONNECTION_ID>" \
  --resource-name "ChildList" \
  --dataset "<SP_SITE_URL>"
```

### 11.3 ERD pattern

```
┌──────────────────────┐        ┌──────────────────────┐
│  ParentList          │        │  ChildList (Actions)  │
├──────────────────────┤        ├──────────────────────┤
│  ID (auto)           │◄──────┐│  ID (auto)           │
│  Title               │       ││  Title               │
│  Status (Choice)     │       ││  RequestId (Text)    │──┘
│  Priority (Choice)   │        │  Action (Choice)     │
│  Modified            │        │  ActionBy (Text)     │
│  Created             │        │  ActionByEmail (Text)│
└──────────────────────┘        │  Comment (Multi-line)│
                                │  Created             │
                                └──────────────────────┘
```

### 11.4 Child list CRUD in data service

```typescript
// Query child records filtered by parent ID
async function spGetActions(requestId: string): Promise<Action[]> {
  const result = await withTimeout(
    ChildListService.getAll({
      select: ['ID', 'Title', 'RequestId', 'Action', 'ActionBy', 'ActionByEmail', 'Comment', 'Created'],
      filter: `RequestId eq '${requestId}'`,
      orderBy: ['Created desc'],
    })
  );
  if (!result.success) throw result.error ?? new Error('SP getAll actions: success=false');
  return (result.data ?? []).map(spActionToRecord);
}

// Create child record + cascade status update to parent
export async function createAction(
  record: Omit<Action, 'id' | 'createdOn'>
): Promise<Action> {
  // Step 1: Create the action
  let action: Action;
  try {
    action = await spCreateAction(record);
    setBackend('sharepoint');
  } catch {
    setBackend('localStorage');
    action = { id: crypto.randomUUID(), ...record, createdOn: new Date().toISOString() };
    lsWriteAll(LS_ACTIONS_KEY, [...lsReadAll(LS_ACTIONS_KEY), action]);
  }

  // Step 2: Cascade — if Approved/Rejected, update parent status
  if (record.action === 'Approved' || record.action === 'Rejected') {
    try {
      await spUpdateRequest(record.requestId, { Status: record.action });
    } catch (err) {
      console.error('[DataService] FAILED to cascade status update:', (err as Error).message);
    }

    // Step 3: Send notification (fire-and-forget)
    notifyRequester(record.action, record.requestId, record.comment).catch(() => {});
  }

  return action;
}
```

### 11.5 Delete cascade

When deleting a parent, also delete related children:

```typescript
export async function deleteRequest(id: string): Promise<void> {
  try {
    await spDeleteRequest(id);
    // Note: SP doesn't cascade — child records remain as orphans.
    // If cleanup is needed, query and delete children separately.
    setBackend('sharepoint');
  } catch {
    setBackend('localStorage');
    lsWriteAll(LS_REQUESTS_KEY, lsReadAll(LS_REQUESTS_KEY).filter((i) => i.id !== id));
    lsWriteAll(LS_ACTIONS_KEY, lsReadAll(LS_ACTIONS_KEY).filter((a) => a.requestId !== id));
  }
}
```

### 11.6 ActionTimeline component (copy/paste ready)

```tsx
// src/components/ActionTimeline.tsx
import type { Action } from '../services/dataService';

const actionIcons: Record<string, { color: string; icon: string }> = {
  Submitted:  { color: 'bg-blue-500',   icon: 'S' },
  Approved:   { color: 'bg-green-500',  icon: 'A' },
  Rejected:   { color: 'bg-red-500',    icon: 'R' },
  Commented:  { color: 'bg-gray-400',   icon: 'C' },
  Reassigned: { color: 'bg-purple-500', icon: 'T' },
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit',
  });
}

export function ActionTimeline({ actions }: { actions: Action[] }) {
  if (actions.length === 0) return <p className="text-sm text-gray-400 italic">No activity yet.</p>;

  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {actions.map((action, idx) => {
          const config = actionIcons[action.action] ?? actionIcons.Commented;
          const isLast = idx === actions.length - 1;
          return (
            <li key={action.id}>
              <div className="relative pb-8">
                {!isLast && <span className="absolute left-4 top-8 -ml-px h-full w-0.5 bg-gray-200" />}
                <div className="relative flex items-start gap-3">
                  <div className={`flex h-8 w-8 items-center justify-center rounded-full text-white text-xs font-bold ${config.color} ring-4 ring-white shrink-0`}>
                    {config.icon}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-semibold text-gray-900">{action.actionBy}</span>
                      <span className="text-xs font-medium text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">{action.action}</span>
                    </div>
                    {action.comment && <p className="mt-1 text-sm text-gray-600">{action.comment}</p>}
                    <p className="mt-1 text-xs text-gray-400">{formatDate(action.createdOn)}</p>
                  </div>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
```

---

## 12. SharePoint Attachments

### 12.1 Reading attachments

```typescript
const hasAttachments = sp['{HasAttachments}'] ?? false;
const attachments = (sp['{Attachments}'] ?? []).map(a => ({
  id: a.Id ?? '',
  url: a.AbsoluteUri ?? '',
  name: a.DisplayName ?? '',
}));

// Open in new tab (works in PA player)
window.open(attachment.url, '_blank');
```

### 12.2 Uploading attachments

Attachment upload is NOT supported through the SharePoint connector's standard CRUD. Workarounds:

1. Power Automate flow triggered by the app
2. SharePoint REST API with auth token from PA context
3. Collect metadata in app, upload separately

---

## 13. Smart Auto-Connect Scripts

### 13.1 Developer workflow

```bash
npm run connect   # auto-discovers connections, wires up data sources
```

### 13.2 Adding a new connector type

Create a file in `scripts/connectors/`:

```javascript
// scripts/connectors/myconnector.js
export default {
  name: 'MyConnector',
  apiId: 'shared_myconnector',
  envPrefix: 'MC',
  connectionRefKey: 'MC_FULL_CONNECTION_ID',
  connectionNameKey: 'MC_CONNECTION_NAME',
  envConnectionIdKey: 'VITE_MC_CONNECTION_ID',

  isConfigured(env) { return env.VITE_MC_ENABLED === 'true'; },
  getResources(env) { return (env.VITE_MC_TABLES || '').split(',').map(s => s.trim()).filter(Boolean); },
  getDataset(env) { return ''; },
  buildArgs(connectionId, dataset, resourceName) {
    return ['--api-id', 'shared_myconnector', '--connection-id', connectionId, '--resource-name', resourceName];
  },
};
```

Then add it to `scripts/connectors/registry.js`.

---

## 14. Reusable UI Patterns

### 14.1 Toast notification system

**Store slice** (add to your Zustand store):

```typescript
interface Toast { id: string; type: 'success' | 'error' | 'warning' | 'info'; title: string; message?: string; }

// In store:
toasts: [] as Toast[],
addToast: (toast: Omit<Toast, 'id'>) => {
  const id = `t-${++_tid}`;
  set((s) => ({ toasts: [...s.toasts, { ...toast, id }] }));
  return id;
},
removeToast: (id: string) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
```

**Toast component** (copy/paste ready):

```tsx
// src/components/Toast.tsx
import { useEffect } from 'react';
import { useAppStore } from '../store/appStore';

const ICONS: Record<string, string> = {
  success: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  error: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
  warning: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z',
  info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
};
const COLORS: Record<string, { bg: string; border: string; icon: string }> = {
  success: { bg: 'bg-emerald-50', border: 'border-emerald-200', icon: 'text-emerald-500' },
  error:   { bg: 'bg-red-50',     border: 'border-red-200',     icon: 'text-red-500' },
  warning: { bg: 'bg-amber-50',   border: 'border-amber-200',   icon: 'text-amber-500' },
  info:    { bg: 'bg-blue-50',    border: 'border-blue-200',    icon: 'text-blue-500' },
};

export function ToastContainer() {
  const toasts = useAppStore((s) => s.toasts);
  const removeToast = useAppStore((s) => s.removeToast);
  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
      {toasts.map((t) => (
        <ToastItem key={t.id} id={t.id} type={t.type} title={t.title} message={t.message} onDismiss={removeToast} />
      ))}
    </div>
  );
}

function ToastItem({ id, type, title, message, onDismiss }: {
  id: string; type: string; title: string; message?: string; onDismiss: (id: string) => void;
}) {
  useEffect(() => { const timer = setTimeout(() => onDismiss(id), 4500); return () => clearTimeout(timer); }, [id, onDismiss]);
  const c = COLORS[type] ?? COLORS.info;
  return (
    <div className={`pointer-events-auto animate-toast-in w-80 rounded-lg border ${c.border} ${c.bg} p-3 shadow-lg`}>
      <div className="flex items-start gap-2.5">
        <svg className={`mt-0.5 h-5 w-5 shrink-0 ${c.icon}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={ICONS[type] ?? ICONS.info} />
        </svg>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-gray-900">{title}</p>
          {message && <p className="mt-0.5 text-xs text-gray-600">{message}</p>}
        </div>
        <button onClick={() => onDismiss(id)} className="shrink-0 text-gray-400 hover:text-gray-600">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
```

### 14.2 Interactive donut charts as filters

SVG donut charts that toggle Zustand filter state on click — replaces traditional sidebar filters:

```tsx
function DonutChart({ data, colorMap, title, filterKey }: {
  data: { label: string; count: number }[];
  colorMap: Record<string, string>;
  title: string;
  filterKey: 'statuses' | 'platforms' | 'businessUnits' | 'developers';
}) {
  const { filters, setFilters } = useAppStore();
  const total = data.reduce((s, d) => s + d.count, 0);
  if (total === 0) return null;

  const activeFilters = filters[filterKey];
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  function toggleFilter(value: string) {
    const current = filters[filterKey];
    if (current.includes(value)) setFilters({ [filterKey]: current.filter((v) => v !== value) });
    else setFilters({ [filterKey]: [...current, value] });
  }

  return (
    <div className="rounded-xl border border-gray-100 bg-white p-4 transition hover:shadow-md">
      <h3 className="mb-3 text-[10px] font-bold uppercase tracking-widest text-gray-400">{title}</h3>
      <div className="flex items-center gap-4">
        <svg viewBox="0 0 100 100" className="h-24 w-24 shrink-0 -rotate-90">
          {data.map((d, i) => {
            const pct = d.count / total;
            const dash = pct * circumference;
            const gap = circumference - dash;
            const isActive = activeFilters.includes(d.label);
            const segment = (
              <circle key={d.label} cx="50" cy="50" r={radius} fill="none"
                stroke={colorMap[d.label] ?? FALLBACK_COLORS[i % FALLBACK_COLORS.length]}
                strokeWidth={isActive ? 14 : 12}
                strokeDasharray={`${dash} ${gap}`} strokeDashoffset={-offset} strokeLinecap="round"
                className="cursor-pointer transition-all duration-300 hover:opacity-80"
                opacity={activeFilters.length === 0 || isActive ? 1 : 0.3}
                onClick={() => toggleFilter(d.label)} />
            );
            offset += dash;
            return segment;
          })}
          <text x="50" y="50" textAnchor="middle" dominantBaseline="central"
            className="rotate-90 origin-center fill-gray-900 font-bold" style={{ fontSize: '18px' }}>
            {total}
          </text>
        </svg>
        <div className="flex flex-col gap-1.5 min-w-0">
          {data.slice(0, 6).map((d, i) => {
            const isActive = activeFilters.includes(d.label);
            return (
              <button key={d.label} type="button" onClick={() => toggleFilter(d.label)}
                className={`flex items-center gap-2 rounded-md px-1.5 py-0.5 text-xs transition hover:bg-gray-50 ${
                  activeFilters.length > 0 && !isActive ? 'opacity-40' : ''
                } ${isActive ? 'bg-gray-100 font-semibold' : ''}`}>
                <span className="h-2.5 w-2.5 shrink-0 rounded-full"
                  style={{ backgroundColor: colorMap[d.label] ?? FALLBACK_COLORS[i % FALLBACK_COLORS.length] }} />
                <span className="truncate text-gray-600">{d.label}</span>
                <span className="ml-auto font-semibold text-gray-900">{d.count}</span>
              </button>
            );
          })}
          {activeFilters.length > 0 && (
            <button type="button" onClick={() => setFilters({ [filterKey]: [] })}
              className="mt-0.5 text-[10px] font-medium text-[#1E3A5F] hover:underline">Clear filter</button>
          )}
        </div>
      </div>
    </div>
  );
}
```

### 14.3 Stat cards

```tsx
function StatCard({ label, value, icon, accent }: { label: string; value: number; icon: string; accent: string }) {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wide text-gray-400">{label}</p>
          <p className="animate-count-up mt-1 text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${accent}`}>
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d={icon} />
          </svg>
        </div>
      </div>
    </div>
  );
}
```

### 14.4 Backend badge

```tsx
function BackendBadge() {
  const [backend, setBackendState] = useState(getBackend());
  useEffect(() => onBackendChange(setBackendState), []);

  const config = {
    sharepoint: { label: 'SharePoint', class: 'bg-emerald-100 text-emerald-700' },
    localStorage: { label: 'Local', class: 'bg-amber-100 text-amber-700' },
    unknown: { label: 'Connecting...', class: 'bg-gray-100 text-gray-500' },
  }[backend];

  return <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${config.class}`}>{config.label}</span>;
}
```

### 14.5 CSV export

```typescript
function exportCsv(items: MyRecord[]) {
  const headers = ['Title', 'Status', 'Platform', 'Business Unit', 'Developer', 'Last Delivery', 'Modified'];
  const rows = items.map((i) => [i.title, i.appStatus, i.platform, i.businessUnit, i.developmentPoC, i.lastDeliveryDate, i.modifiedOn]);
  const csv = [headers, ...rows].map((r) => r.map((c) => `"${(c ?? '').replace(/"/g, '""')}"`).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `export-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
```

---

## 15. Reusable Hooks & Utilities

### 15.1 useDebounce

```typescript
// src/hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delayMs = 300): T {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);
  return debouncedValue;
}
```

### 15.2 useChoiceOptions

Extracts unique values from loaded SP data for form dropdowns — ensures dropdowns match whatever values are actually in SharePoint:

```typescript
// src/hooks/useChoiceOptions.ts
import { useMemo } from 'react';

function uniqueNonEmpty<T>(items: T[], field: keyof T): string[] {
  const set = new Set<string>();
  for (const item of items) {
    const val = item[field] as string;
    if (val) set.add(val);
  }
  return Array.from(set).sort();
}

export function useChoiceOptions(items: MyRecord[] | undefined) {
  return useMemo(() => {
    if (!items || items.length === 0) return { platforms: [], statuses: [], businessUnits: [] };
    return {
      platforms: uniqueNonEmpty(items, 'platform'),
      statuses: uniqueNonEmpty(items, 'appStatus'),
      businessUnits: uniqueNonEmpty(items, 'businessUnit'),
    };
  }, [items]);
}
```

### 15.3 useFilteredData (client-side filtering, sorting, search)

```typescript
// src/hooks/useFilteredData.ts
import { useMemo } from 'react';
import { useAppStore } from '../store/appStore';
import { useDebounce } from './useDebounce';

export function useFilteredData(items: MyRecord[] | undefined) {
  const { filters, sortField, sortDirection } = useAppStore();
  const debouncedSearch = useDebounce(filters.searchTerm, 300);

  return useMemo(() => {
    if (!items) return [];
    let result = [...items];

    // Filter by each active filter dimension
    if (filters.statuses.length > 0)
      result = result.filter((i) => filters.statuses.includes(i.appStatus));
    if (filters.platforms.length > 0)
      result = result.filter((i) => filters.platforms.includes(i.platform));
    if (filters.businessUnits.length > 0)
      result = result.filter((i) => filters.businessUnits.includes(i.businessUnit));
    if (filters.developers.length > 0)
      result = result.filter((i) => filters.developers.includes(i.developmentPoC));

    // Search across text fields
    if (debouncedSearch) {
      const term = debouncedSearch.toLowerCase();
      result = result.filter((i) =>
        i.title.toLowerCase().includes(term) ||
        i.developmentPoC.toLowerCase().includes(term) ||
        i.businessUnit.toLowerCase().includes(term),
      );
    }

    // Sort
    result.sort((a, b) => {
      const dir = sortDirection === 'asc' ? 1 : -1;
      return compareField(a, b, sortField) * dir;
    });

    return result;
  }, [items, filters, debouncedSearch, sortField, sortDirection]);
}
```

### 15.4 Cancellation pattern for async effects

```typescript
useEffect(() => {
  if (!selectedId) return;
  let cancelled = false;
  setLoading(true);

  Promise.all([getById(selectedId), getActionsByRequestId(selectedId)])
    .then(([record, actions]) => {
      if (cancelled) return;  // Prevent state updates on unmount
      setRecord(record);
      setActions(actions);
    })
    .finally(() => { if (!cancelled) setLoading(false); });

  return () => { cancelled = true; };
}, [selectedId]);
```

---

## 16. Reusable Services — Copy/Paste Ready

### 16.1 Complete dataService.ts template

This template handles single-list CRUD with Choice + Person field handling and verification reads. For multi-list, extend with the patterns from Section 11.

```typescript
// src/services/dataService.ts
// Replace MyList, MyRecord, etc. with your actual names.

import { MyListService } from '../generated/services/MyListService.ts';
import type { MyListRead, MyListWrite } from '../generated/models/MyListModel.ts';

// ── Timeout ─────────────────────────────────────────────────────────────────
const BACKEND_TIMEOUT_MS = 15_000;
function withTimeout<T>(promise: Promise<T>): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error('SP_TIMEOUT')), BACKEND_TIMEOUT_MS),
    ),
  ]);
}

// ── Reactive backend state ──────────────────────────────────────────────────
type BackendType = 'sharepoint' | 'localStorage' | 'unknown';
let _backend: BackendType = 'unknown';
const _listeners = new Set<(b: BackendType) => void>();
export function getBackend(): BackendType { return _backend; }
export function onBackendChange(fn: (b: BackendType) => void) {
  _listeners.add(fn); return () => { _listeners.delete(fn); };
}
function setBackend(b: BackendType) {
  if (_backend !== b) { _backend = b; _listeners.forEach((fn) => fn(b)); }
}

// ── SP → App mapping ────────────────────────────────────────────────────────
function spToRecord(sp: MyListRead): MyRecord {
  return {
    id: String(sp.ID ?? ''),
    title: sp.Title ?? '',
    // ... map all fields, extracting .Value for Choice, .DisplayName/.Email for Person
  };
}

// ── App → SP payload ────────────────────────────────────────────────────────
function buildPayload(record: Partial<MyRecord>): Record<string, unknown> {
  const p: Record<string, unknown> = {};
  // Text fields
  if (record.title !== undefined) p.Title = record.title;
  // Choice fields — { Value: "..." }
  if (record.status) p.Status = { Value: record.status };
  // Person fields — only @odata.type + Claims
  if (record.assigneeEmail) {
    p.Assignee = {
      '@odata.type': '#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser',
      Claims: `i:0#.f|membership|${record.assigneeEmail}`,
    };
  }
  return p;
}

// ── SP helpers ──────────────────────────────────────────────────────────────
const SELECT = ['ID', 'Title', /* ... all needed fields ... */ 'Modified', 'Created'];

async function spGetAll(): Promise<MyRecord[]> {
  const r = await withTimeout(MyListService.getAll({ select: SELECT, orderBy: ['Modified desc'] }));
  if (!r.success) throw r.error ?? new Error('getAll failed');
  return (r.data ?? []).map(spToRecord);
}
async function spGet(id: string): Promise<MyRecord> {
  const r = await withTimeout(MyListService.get(id));
  if (!r.success || !r.data) throw r.error ?? new Error('not found');
  return spToRecord(r.data);
}

// ── localStorage fallback ───────────────────────────────────────────────────
const LS_KEY = 'my_data_v1';
function lsReadAll(): MyRecord[] { try { return JSON.parse(localStorage.getItem(LS_KEY) || '[]'); } catch { return []; } }
function lsWriteAll(items: MyRecord[]) { try { localStorage.setItem(LS_KEY, JSON.stringify(items)); } catch {} }

// ── Write result ────────────────────────────────────────────────────────────
export interface WriteResult { item: MyRecord; verified: boolean; warning?: string; }

// ── Public API ──────────────────────────────────────────────────────────────
export async function getItems(): Promise<MyRecord[]> {
  try { const items = await spGetAll(); setBackend('sharepoint'); return items; }
  catch { setBackend('localStorage'); return lsReadAll(); }
}

export async function createItem(record: Omit<MyRecord, 'id' | 'createdOn' | 'modifiedOn'>): Promise<WriteResult> {
  const payload = buildPayload(record);
  try {
    const r = await withTimeout(MyListService.create(payload as any));
    if (!r.success) throw r.error ?? new Error('create failed');
    const created = spToRecord(r.data);
    setBackend('sharepoint');
    try { const v = await spGet(created.id); return { item: v, verified: true }; }
    catch { return { item: created, verified: false, warning: 'Created but verification failed.' }; }
  } catch {
    setBackend('localStorage');
    const item = { id: crypto.randomUUID(), ...record, createdOn: new Date().toISOString(), modifiedOn: new Date().toISOString() } as MyRecord;
    lsWriteAll([...lsReadAll(), item]);
    return { item, verified: true };
  }
}

export async function updateItem(id: string, updates: Partial<MyRecord>): Promise<WriteResult> {
  const payload = buildPayload(updates);
  console.log('[DataService] UPDATE', id, JSON.stringify(payload, null, 2));
  try {
    const r = await withTimeout(MyListService.update(id, payload as any));
    if (!r.success) throw r.error ?? new Error('update failed');
    setBackend('sharepoint');
    try {
      const v = await spGet(id);
      if (updates.title && v.title !== updates.title)
        return { item: v, verified: false, warning: 'Write did not persist.' };
      return { item: v, verified: true };
    } catch { return { item: spToRecord(r.data), verified: false, warning: 'Verification read failed.' }; }
  } catch {
    setBackend('localStorage');
    const all = lsReadAll();
    const idx = all.findIndex((i) => i.id === id);
    if (idx >= 0) { all[idx] = { ...all[idx], ...updates, modifiedOn: new Date().toISOString() }; lsWriteAll(all); return { item: all[idx], verified: true }; }
    throw new Error('Not found');
  }
}

export async function deleteItem(id: string): Promise<void> {
  try { await withTimeout(MyListService.delete(id)); setBackend('sharepoint'); }
  catch { setBackend('localStorage'); lsWriteAll(lsReadAll().filter((i) => i.id !== id)); }
}
```

---

## 17. CSS & Animation Library

Add this to your `src/index.css` — it provides all the animations and utility classes used across our apps:

```css
@import "tailwindcss";

:root {
  --navy: #1E3A5F;
  --navy-light: #2B4F7E;
  --navy-dark: #152C4A;
  --bg: #F8FAFC;
}

body {
  margin: 0;
  background-color: var(--bg);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ── Animations ────────────────────────────────────────────────────────────── */
@keyframes slideInRight {
  from { transform: translateX(100%); opacity: 0; }
  to   { transform: translateX(0); opacity: 1; }
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInScale {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}
@keyframes toastIn {
  from { opacity: 0; transform: translateX(100%) scale(0.95); }
  to   { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
@keyframes countUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Utility classes ───────────────────────────────────────────────────────── */
.animate-slide-in      { animation: slideInRight 250ms ease-out; }
.animate-fade-in       { animation: fadeIn 300ms ease-out; }
.animate-fade-in-scale { animation: fadeInScale 200ms ease-out; }
.animate-toast-in      { animation: toastIn 300ms cubic-bezier(0.16, 1, 0.3, 1); }
.animate-count-up      { animation: countUp 500ms ease-out; }

.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

/* ── Scrollbar ─────────────────────────────────────────────────────────────── */
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* ── Form input base ──────────────────────────────────────────────────────── */
.input {
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: #111827;
  outline: none;
  transition: border-color 150ms, box-shadow 150ms;
}
.input::placeholder { color: #9ca3af; }
.input:focus { border-color: #1E3A5F; box-shadow: 0 0 0 1px #1E3A5F; }

/* ── Card hover lift ──────────────────────────────────────────────────────── */
.card-hover { transition: transform 150ms ease, box-shadow 150ms ease; }
.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px -5px rgba(0,0,0,0.1), 0 4px 10px -5px rgba(0,0,0,0.04);
}
```

---

## 18. Deployment Workflow

### 18.1 First deploy

```bash
# 1. Authenticate
pac auth create --environment <PP_ENVIRONMENT_ID>

# 2. Init app
npm run setup
# Creates app, saves appId to power.config.json

# 3. Connect data sources
npm run connect

# 4. Build and deploy
npm run build
npm run push

# 5. Test with live data
npm run start
```

### 18.2 Subsequent deploys

```bash
npm run build && npm run push
```

### 18.3 Promoting DEV → TEST → PROD

For each environment:
1. `pac auth create --environment <NEW_ENV_ID>`
2. Update `.env` with new site URL, list names, env label
3. Update `power.config.json` (environmentId, clear appId for new env)
4. `npm run setup`
5. `npm run connect`
6. `npm run build && npm run push`
7. Smoke-test in PA player

---

## 19. Key Gotchas — Master List

| # | Gotcha | Details |
| --- | ------ | ------- |
| 1 | **Choice field updates need Value object** | `{ Value: "Active" }` not `"Active"`. Creates may work with strings, updates require the object. See Section 7.3. |
| 2 | **Person field writes — only 2 props writable** | Only `@odata.type` and `Claims`. Sending DisplayName/Email/etc. causes **silent** failure. See Section 7.4. |
| 3 | **Generated TypeScript types are wrong** | The Write interfaces say `string` for Choice and include read-only Person props. Use `Record<string, unknown>`. See Section 7.1. |
| 4 | **SP writes can return success but not persist** | Always do a verification read after write. See Section 5.5. |
| 5 | `window.powerAppsBridge` is always undefined | PA player never sets it. Use timeout+fallback. |
| 6 | Generated `dataSourceName` is lowercase | `add-data-source` lowercases the table name. Don't change it. |
| 7 | `pac code *` commands broken | Use `npx power-apps *` instead. See Section 3. |
| 8 | `.env` is build-time only | Changes after build have no effect. Always rebuild. |
| 9 | `.ts` extension needed in imports | `import { X } from '../generated/index.ts'` — Vite needs the extension. |
| 10 | `SP_CONNECTOR_ID` is always `shared_sharepointonline` | Same across all environments on commercial M365. |
| 11 | Claims format is `i:0#.f\|membership\|email` | Always this format for Person field writes. |
| 12 | Multi-person needs `@odata.type` Collection | Must include the type declaration alongside the Claims array. See Section 6.6. |
| 13 | `tsconfig.app.json` must include `.power` | Without this, TS can't resolve `dataSourcesInfo` import. |
| 14 | `@microsoft/power-apps-vite` uses named export | `import { powerApps }` not `import powerApps`. |
| 15 | `npm run setup` Windows assertion error | Cosmetic libuv bug. Command succeeds. Check power.config.json. |
| 16 | Notifications must be fire-and-forget | Always `.catch(() => {})` — never let email failure block CRUD. |
| 17 | Deep links need APP_ID + PP_ENVIRONMENT_ID | Both must be in `.env` for `buildDeepLink()` to work. |
| 18 | Child records don't auto-delete in SP | SP has no cascade delete. Delete children explicitly or accept orphans. |
| 19 | `import.meta.env` only in config.ts | Every other file imports from config.ts — never reads env directly. |

---

## 20. Checklists

### 20.1 New project setup

- [ ] Fill in Section 1 values
- [ ] Create Vite + React + TypeScript project
- [ ] Install packages (zustand, @microsoft/power-apps, @tanstack/react-query, tailwindcss)
- [ ] Configure vite.config.ts (react + tailwindcss + powerApps plugins)
- [ ] Add `.power` to tsconfig.app.json include
- [ ] Create `src/config.ts` (Section 4.1)
- [ ] Create `.env` with values, `.env.example` with placeholders
- [ ] Create `power.config.json` with environmentId
- [ ] Scaffold scripts (setup.js, connect.js, connectors/)
- [ ] Verify `.gitignore` excludes `.env`, `power.config.json`, `.connection-refs.local`
- [ ] Copy `index.css` from Section 17
- [ ] Copy `useDebounce.ts` from Section 15.1
- [ ] Copy `useChoiceOptions.ts` from Section 15.2
- [ ] Copy `Toast.tsx` from Section 14.1
- [ ] `pac auth create --environment <ID>`
- [ ] `npm run setup` — confirm appId in power.config.json
- [ ] `npm run connect` — confirm data sources added
- [ ] Verify `src/generated/` has service + model files
- [ ] Wire up dataService.ts with:
  - [ ] Timeout + fallback
  - [ ] `spToRecord` mapping (extract `.Value` for Choice, `.DisplayName/.Email` for Person)
  - [ ] `buildPayload` with Choice as `{ Value: "..." }` and Person with only writable props
  - [ ] Verification reads on create/update
- [ ] Add BackendBadge to header
- [ ] `npm run build` — no errors
- [ ] `npm run push` — app appears in make.powerapps.com
- [ ] Open in PA player — badge shows "SharePoint"
- [ ] Smoke-test CRUD (create, edit, delete — verify data persists in SP)

### 20.2 Add People Picker

- [ ] Add O365 Users connector (`npm run connect` with `VITE_O365U_ENABLED=true`)
- [ ] Copy `userService.ts` from Section 8.2
- [ ] Copy `PeoplePicker.tsx` from Section 8.3
- [ ] Add sample users for local dev testing
- [ ] Use PeoplePicker in forms, wire email to `buildPayload` Claims field

### 20.3 Add email notifications

- [ ] Add O365 Outlook connector
- [ ] Copy `notificationService.ts` from Section 9.2
- [ ] Create `emailTemplates.ts` with `buildDeepLink()` + templates
- [ ] Add `VITE_APP_ID` and `VITE_PP_ENVIRONMENT_ID` to `.env`
- [ ] Wire notifications as fire-and-forget in dataService CRUD methods
- [ ] Test in PA player (emails only send when Outlook connector is live)

### 20.4 Add deep linking

- [ ] Add `VITE_APP_ID` and `VITE_PP_ENVIRONMENT_ID` to `.env` and config.ts
- [ ] Add `handleDeepLink()` in App.tsx useEffect (Section 10.3)
- [ ] Use `buildDeepLink()` in email templates
- [ ] Test with `?recordId=xxx` in URL at localhost

### 20.5 Add parent-child lists

- [ ] Connect second list via `npx power-apps add-data-source`
- [ ] Add child record types and SP mapping functions
- [ ] Add child CRUD in dataService with parent filter
- [ ] Add status cascade logic (child action → update parent status)
- [ ] Copy `ActionTimeline.tsx` from Section 11.6
- [ ] Handle delete cascade in localStorage fallback

### 20.6 Promote to next environment

- [ ] Get new environment values (site URL, env ID)
- [ ] Update `.env` and `power.config.json`
- [ ] `pac auth create --environment <NEW_ID>`
- [ ] `npm run setup`
- [ ] `npm run connect`
- [ ] `npm run build && npm run push`
- [ ] Verify in PA player — CRUD, notifications, deep links all work

---

*Blueprint version: 3.0 · Last updated: 2026-04-16*
*Based on: App Inventory Tracker + Approval Tracker — battle-tested patterns*
*Previous versions: v1 (initial), v2 (field types + attachments), v3 (write gotchas + notifications + deep links + reusable components)*
