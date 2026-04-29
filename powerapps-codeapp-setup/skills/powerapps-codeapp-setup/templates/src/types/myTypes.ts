// App-level TypeScript interfaces.
// Replace MyRecord / MyList* with your actual list names.

export interface MyRecord {
  id: string;
  title: string;
  description?: string;
  // Choice fields — store the .Value as a plain string at app level
  status: string;
  // Lookup fields (→ Config table) — keep the ID for writes, label for display
  priorityId: number | null;
  priorityLabel?: string;
  // Person fields — store both display name and email
  assignee?: string;
  assigneeEmail?: string;
  // Date fields — ISO strings
  dueDate?: string;
  // System fields
  createdOn: string;
  modifiedOn: string;
}

export interface FilterState {
  searchTerm: string;
  statuses: string[];
  // add other multi-select dimensions as needed
}

export type SortField = 'title' | 'modifiedOn' | 'dueDate' | 'status';
export type SortDirection = 'asc' | 'desc';
