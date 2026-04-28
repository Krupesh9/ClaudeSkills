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
      qc.setQueryData<MyRecord[]>(QUERY_KEY, (old) => (old ?? []).filter((item) => item.id !== id));
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
