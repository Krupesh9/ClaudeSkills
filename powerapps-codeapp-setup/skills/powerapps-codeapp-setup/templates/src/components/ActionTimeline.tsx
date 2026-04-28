// For parent-child setups (e.g., Requests + Actions). Pass a chronological list
// of action records — the timeline renders icons, timestamps, and comments.

export interface TimelineAction {
  id: string;
  action: string; // e.g., "Submitted", "Approved", "Rejected", "Commented", "Reassigned"
  actionBy: string;
  comment?: string;
  createdOn: string;
}

const actionIcons: Record<string, { color: string; icon: string }> = {
  Submitted: { color: 'bg-blue-500', icon: 'S' },
  Approved: { color: 'bg-green-500', icon: 'A' },
  Rejected: { color: 'bg-red-500', icon: 'R' },
  Commented: { color: 'bg-gray-400', icon: 'C' },
  Reassigned: { color: 'bg-purple-500', icon: 'T' },
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function ActionTimeline({ actions }: { actions: TimelineAction[] }) {
  if (actions.length === 0)
    return <p className="text-sm text-gray-400 italic">No activity yet.</p>;

  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {actions.map((action, idx) => {
          const config = actionIcons[action.action] ?? actionIcons.Commented;
          const isLast = idx === actions.length - 1;
          return (
            <li key={action.id}>
              <div className="relative pb-8">
                {!isLast && (
                  <span className="absolute left-4 top-8 -ml-px h-full w-0.5 bg-gray-200" />
                )}
                <div className="relative flex items-start gap-3">
                  <div
                    className={`flex h-8 w-8 items-center justify-center rounded-full text-white text-xs font-bold ${config.color} ring-4 ring-white shrink-0`}
                  >
                    {config.icon}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-semibold text-gray-900">{action.actionBy}</span>
                      <span className="text-xs font-medium text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                        {action.action}
                      </span>
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
