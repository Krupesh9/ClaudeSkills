import { useMemo } from 'react';
import { useAppStore } from '../store/appStore';
import { useDebounce } from './useDebounce';
import type { MyRecord, SortField, SortDirection } from '../types/myTypes';

function compareField(a: MyRecord, b: MyRecord, field: SortField): number {
  const av = (a[field] ?? '') as string;
  const bv = (b[field] ?? '') as string;
  return av.localeCompare(bv);
}

export function useFilteredData(items: MyRecord[] | undefined) {
  const { filters, sortField, sortDirection } = useAppStore();
  const debouncedSearch = useDebounce(filters.searchTerm, 300);

  return useMemo(() => {
    if (!items) return [];
    let result = [...items];

    if (filters.statuses.length > 0)
      result = result.filter((i) => filters.statuses.includes(i.status));

    if (debouncedSearch) {
      const term = debouncedSearch.toLowerCase();
      result = result.filter(
        (i) =>
          i.title.toLowerCase().includes(term) ||
          (i.assignee ?? '').toLowerCase().includes(term) ||
          (i.description ?? '').toLowerCase().includes(term),
      );
    }

    result.sort((a, b) => {
      const dir: number = sortDirection === 'asc' ? 1 : -1;
      return compareField(a, b, sortField as SortField) * dir;
    });

    return result;
  }, [items, filters, debouncedSearch, sortField, sortDirection]);
}

export type { SortField, SortDirection };
