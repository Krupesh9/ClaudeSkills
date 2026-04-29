// Config table — single source of truth for all lookup-style values.
// Loaded once on app boot, cached by TanStack Query.
//
// SP table schema (recommended):
//   Title (text), Value (text), Category (Choice), IsActive (Yes/No),
//   SortOrder (Number), Description (multi-line)
//
// Replace ConfigService with the actual generated service for your Config list.

import { ConfigService } from '../generated/services/ConfigService.ts';

export interface ConfigRow {
  id: number;          // Lookup target ID — pass this as <FieldName>Id when writing
  title: string;       // Display label shown to users
  value: string;       // Stable internal key (use this for code-side equality, not title)
  category: string;    // Lookup category — "Status", "Priority", "BusinessUnit", ...
  sortOrder: number;
  description?: string;
}

export async function getConfigRows(): Promise<ConfigRow[]> {
  const r = await ConfigService.getAll({
    select: ['ID', 'Title', 'Value', 'Category', 'IsActive', 'SortOrder', 'Description'],
    filter: 'IsActive eq true',
    orderBy: ['SortOrder', 'Title'],
  });
  if (!r.success) throw r.error ?? new Error('Config getAll failed');
  return (r.data ?? []).map((c: any) => ({
    id: c.ID ?? 0,
    title: c.Title ?? '',
    value: c.Value ?? '',
    category: c.Category?.Value ?? '',
    sortOrder: c.SortOrder ?? 0,
    description: c.Description ?? undefined,
  }));
}

export function rowsByCategory(rows: ConfigRow[], category: string): ConfigRow[] {
  return rows.filter((r) => r.category === category);
}

export function findRowById(rows: ConfigRow[], id: number | null | undefined): ConfigRow | undefined {
  if (!id) return undefined;
  return rows.find((r) => r.id === id);
}

export function findRowByValue(rows: ConfigRow[], category: string, value: string): ConfigRow | undefined {
  return rows.find((r) => r.category === category && r.value === value);
}
