// ─────────────────────────────────────────────────────────────────────────────
// Data service — SharePoint primary, localStorage fallback.
//
// CRITICAL CONVENTIONS (do not deviate):
//   • Choice field UPDATEs must use { Value: "..." } objects, not plain strings.
//   • Person field WRITEs must include only @odata.type + Claims (no DisplayName/Email).
//   • Always verify writes with a follow-up read; surface WriteResult.verified to UI.
//   • Bypass generated TypeScript Write types with `Record<string, unknown>` and `as any`.
//
// Replace MyList / MyRecord with your actual names. See BLUEPRINT.md §16.1.
// ─────────────────────────────────────────────────────────────────────────────

import { MyListService } from '../generated/services/MyListService.ts';
import type { MyListRead, MyListWrite } from '../generated/models/MyListModel.ts';
import type { MyRecord } from '../types/myTypes';

// ── Timeout ──────────────────────────────────────────────────────────────────
const BACKEND_TIMEOUT_MS = 15_000;

function withTimeout<T>(promise: Promise<T>): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error('SP_TIMEOUT: no response — not in PA player?')), BACKEND_TIMEOUT_MS),
    ),
  ]);
}

// ── Reactive backend state ───────────────────────────────────────────────────
type BackendType = 'sharepoint' | 'localStorage' | 'unknown';
let _backend: BackendType = 'unknown';
const _listeners = new Set<(b: BackendType) => void>();

export function getBackend(): BackendType {
  return _backend;
}
export function onBackendChange(fn: (b: BackendType) => void) {
  _listeners.add(fn);
  return () => {
    _listeners.delete(fn);
  };
}
function setBackend(b: BackendType) {
  if (_backend !== b) {
    _backend = b;
    _listeners.forEach((fn) => fn(b));
  }
}

// ── SP → App mapping ─────────────────────────────────────────────────────────
function spToRecord(sp: MyListRead): MyRecord {
  return {
    id: String(sp.ID ?? ''),
    title: sp.Title ?? '',
    description: (sp as any).Description ?? '',
    // Choice fields — extract .Value
    status: (sp as any).Status?.Value ?? '',
    // Person fields — extract .DisplayName and .Email
    assignee: (sp as any).Assignee?.DisplayName ?? '',
    assigneeEmail: (sp as any).Assignee?.Email ?? '',
    // Dates / timestamps
    dueDate: (sp as any).DueDate ?? '',
    createdOn: (sp as any).Created ?? new Date().toISOString(),
    modifiedOn: (sp as any).Modified ?? new Date().toISOString(),
  };
}

// ── App → SP payload ─────────────────────────────────────────────────────────
// Build with Record<string, unknown> to bypass incorrect generated Write types.
function buildPayload(
  record: Partial<Omit<MyRecord, 'id' | 'createdOn' | 'modifiedOn'>>,
): Record<string, unknown> {
  const p: Record<string, unknown> = {};

  // Text / simple fields — plain values
  if (record.title !== undefined) p.Title = record.title;
  if (record.description !== undefined) p.Description = record.description;
  if (record.dueDate !== undefined) p.DueDate = record.dueDate;

  // Choice fields — MUST be { Value: "..." } objects on UPDATE
  if (record.status) p.Status = { Value: record.status };

  // Person fields — only @odata.type + Claims are writable
  if (record.assigneeEmail) {
    p.Assignee = {
      '@odata.type': '#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser',
      Claims: `i:0#.f|membership|${record.assigneeEmail}`,
    };
  }

  return p;
}

// ── Field selection for queries ──────────────────────────────────────────────
const SELECT = ['ID', 'Title', 'Description', 'Status', 'Assignee', 'DueDate', 'Created', 'Modified'];

async function spGetAll(): Promise<MyRecord[]> {
  const r = await withTimeout(
    MyListService.getAll({ select: SELECT, orderBy: ['Modified desc'] }),
  );
  if (!r.success) throw r.error ?? new Error('getAll failed');
  return (r.data ?? []).map(spToRecord);
}

async function spGet(id: string): Promise<MyRecord> {
  const r = await withTimeout(MyListService.get(id));
  if (!r.success || !r.data) throw r.error ?? new Error('not found');
  return spToRecord(r.data);
}

// ── localStorage fallback ────────────────────────────────────────────────────
const LS_KEY = 'my_data_v1';

function lsReadAll(): MyRecord[] {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY) || '[]');
  } catch {
    return [];
  }
}
function lsWriteAll(items: MyRecord[]) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(items));
  } catch {
    /* noop */
  }
}

// ── Write result ─────────────────────────────────────────────────────────────
export interface WriteResult {
  item: MyRecord;
  verified: boolean;
  warning?: string;
}

// ── Public API ───────────────────────────────────────────────────────────────
export async function getItems(): Promise<MyRecord[]> {
  try {
    const items = await spGetAll();
    setBackend('sharepoint');
    return items;
  } catch (err) {
    console.warn('[DataService] SP getAll failed → localStorage fallback:', (err as Error).message);
    setBackend('localStorage');
    return lsReadAll();
  }
}

export async function getById(id: string): Promise<MyRecord> {
  try {
    const item = await spGet(id);
    setBackend('sharepoint');
    return item;
  } catch {
    setBackend('localStorage');
    const found = lsReadAll().find((i) => i.id === id);
    if (!found) throw new Error(`Not found: ${id}`);
    return found;
  }
}

export async function createItem(
  record: Omit<MyRecord, 'id' | 'createdOn' | 'modifiedOn'>,
): Promise<WriteResult> {
  const payload = buildPayload(record);
  console.log('[DataService] CREATE payload:', JSON.stringify(payload, null, 2));

  try {
    const r = await withTimeout(MyListService.create(payload as Omit<MyListWrite, 'ID'>));
    if (!r.success) throw r.error ?? new Error('create failed');
    const created = spToRecord(r.data as MyListRead);
    setBackend('sharepoint');

    // Verification read
    try {
      const verified = await spGet(created.id);
      return { item: verified, verified: true };
    } catch {
      return { item: created, verified: false, warning: 'Created but verification read failed.' };
    }
  } catch (err) {
    console.warn('[DataService] SP create failed → localStorage fallback:', (err as Error).message);
    setBackend('localStorage');
    const item: MyRecord = {
      id: crypto.randomUUID(),
      ...record,
      createdOn: new Date().toISOString(),
      modifiedOn: new Date().toISOString(),
    } as MyRecord;
    lsWriteAll([...lsReadAll(), item]);
    return { item, verified: true };
  }
}

export async function updateItem(
  id: string,
  updates: Partial<Omit<MyRecord, 'id' | 'createdOn' | 'modifiedOn'>>,
): Promise<WriteResult> {
  const payload = buildPayload(updates);
  console.log('[DataService] UPDATE id:', id, 'payload:', JSON.stringify(payload, null, 2));

  try {
    const r = await withTimeout(
      MyListService.update(id, payload as Partial<Omit<MyListWrite, 'ID'>>),
    );
    if (!r.success) throw r.error ?? new Error('update: success=false');
    setBackend('sharepoint');

    // Verification read — confirm the write actually persisted
    try {
      const verified = await spGet(id);
      if (updates.title !== undefined && verified.title !== updates.title) {
        console.warn('[DataService] UPDATE verification FAILED — write did not persist');
        return {
          item: verified,
          verified: false,
          warning: 'SharePoint returned success but data did not persist.',
        };
      }
      return { item: verified, verified: true };
    } catch {
      return {
        item: spToRecord(r.data as MyListRead),
        verified: false,
        warning: 'Updated but verification read failed.',
      };
    }
  } catch (err) {
    console.warn('[DataService] SP update failed → localStorage fallback:', (err as Error).message);
    setBackend('localStorage');
    const all = lsReadAll();
    const idx = all.findIndex((i) => i.id === id);
    if (idx >= 0) {
      all[idx] = { ...all[idx], ...updates, modifiedOn: new Date().toISOString() };
      lsWriteAll(all);
      return { item: all[idx], verified: true };
    }
    throw new Error(`Not found: ${id}`);
  }
}

export async function deleteItem(id: string): Promise<void> {
  try {
    const r = await withTimeout(MyListService.delete(id));
    if (!r.success) throw r.error ?? new Error('delete failed');
    setBackend('sharepoint');
  } catch (err) {
    console.warn('[DataService] SP delete failed → localStorage fallback:', (err as Error).message);
    setBackend('localStorage');
    lsWriteAll(lsReadAll().filter((i) => i.id !== id));
  }
}
