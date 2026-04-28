import { create } from 'zustand';
import type { FilterState, SortField, SortDirection } from '../types/myTypes';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
}

interface AppState {
  filters: FilterState;
  setFilters: (updates: Partial<FilterState>) => void;
  resetFilters: () => void;

  sortField: SortField;
  sortDirection: SortDirection;
  setSort: (field: SortField, direction?: SortDirection) => void;

  selectedId: string | null;
  setSelectedId: (id: string | null) => void;

  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
}

const INITIAL_FILTERS: FilterState = {
  searchTerm: '',
  statuses: [],
};

let _tid = 0;

export const useAppStore = create<AppState>((set) => ({
  filters: INITIAL_FILTERS,
  setFilters: (updates) =>
    set((s) => ({ filters: { ...s.filters, ...updates } })),
  resetFilters: () => set({ filters: INITIAL_FILTERS }),

  sortField: 'modifiedOn',
  sortDirection: 'desc',
  setSort: (field, direction) =>
    set((s) => ({
      sortField: field,
      sortDirection: direction ?? (s.sortField === field && s.sortDirection === 'asc' ? 'desc' : 'asc'),
    })),

  selectedId: null,
  setSelectedId: (id) => set({ selectedId: id }),

  toasts: [],
  addToast: (toast) => {
    const id = `t-${++_tid}`;
    set((s) => ({ toasts: [...s.toasts, { ...toast, id }] }));
    return id;
  },
  removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));
