import { useEffect } from 'react';
import { APP_DISPLAY_NAME, APP_ENV_LABEL } from './config';
import { BackendBadge } from './components/BackendBadge';
import { ToastContainer } from './components/Toast';

export default function App() {
  // Deep link handler — opens detail view when ?recordId=... is present
  useEffect(() => {
    handleDeepLink();

    async function handleDeepLink() {
      let recordId: string | null = null;

      try {
        const { getContext } = await import('@microsoft/power-apps/app');
        const ctx = await getContext();
        recordId = (ctx as any)?.app?.queryParams?.recordId ?? null;
      } catch {
        /* not in PA player */
      }

      if (!recordId) {
        const params = new URLSearchParams(window.location.search);
        recordId = params.get('recordId');
      }

      if (recordId) {
        // TODO: navigate to detail view in your store / router
        console.log('[DeepLink] recordId:', recordId);
      }
    }
  }, []);

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <header className="bg-[#1E3A5F] text-white px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold">{APP_DISPLAY_NAME}</h1>
          {APP_ENV_LABEL && (
            <span className="text-[10px] font-bold uppercase tracking-wider bg-white/15 px-2 py-0.5 rounded">
              {APP_ENV_LABEL}
            </span>
          )}
        </div>
        <BackendBadge />
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="rounded-xl border border-gray-100 bg-white p-8 text-center text-gray-500">
          <p className="text-sm">Welcome to your new Power Apps Code App.</p>
          <p className="text-xs mt-2">
            Wire up your data hooks and components, then deploy with{' '}
            <code className="bg-gray-100 px-1.5 py-0.5 rounded">npm run push</code>.
          </p>
        </div>
      </main>

      <ToastContainer />
    </div>
  );
}
