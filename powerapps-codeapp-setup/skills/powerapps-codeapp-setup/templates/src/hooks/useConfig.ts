// Config table — TanStack Query hook with long stale time.
// Loaded once, used everywhere via rowsByCategory().

import { useQuery } from '@tanstack/react-query';
import { getConfigRows, rowsByCategory } from '../services/configService';

export function useConfig() {
  return useQuery({
    queryKey: ['config'],
    queryFn: getConfigRows,
    staleTime: 30 * 60 * 1000, // 30 min — config changes rarely
    gcTime: 60 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

// Convenience hook for a single category — wraps useConfig + filter
export function useConfigCategory(category: string) {
  const { data, isLoading, error } = useConfig();
  return {
    options: data ? rowsByCategory(data, category) : [],
    isLoading,
    error,
  };
}
