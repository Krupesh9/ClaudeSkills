import { useMemo } from 'react';
import type { MyRecord } from '../types/myTypes';

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
    if (!items || items.length === 0) return { statuses: [] };
    return {
      statuses: uniqueNonEmpty(items, 'status'),
      // Add more dimensions as your data model grows
    };
  }, [items]);
}
