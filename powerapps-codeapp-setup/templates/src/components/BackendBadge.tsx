import { useEffect, useState } from 'react';
import { getBackend, onBackendChange } from '../services/dataService';

export function BackendBadge() {
  const [backend, setBackend] = useState(getBackend());
  useEffect(() => onBackendChange(setBackend), []);

  const config = {
    sharepoint: { label: 'SharePoint', class: 'bg-emerald-500/15 text-emerald-100 border-emerald-400/30' },
    localStorage: { label: 'Local', class: 'bg-amber-500/15 text-amber-100 border-amber-400/30' },
    unknown: { label: 'Connecting...', class: 'bg-white/10 text-white/70 border-white/20' },
  }[backend];

  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-medium border ${config.class}`}>
      {config.label}
    </span>
  );
}
