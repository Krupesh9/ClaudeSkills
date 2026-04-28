export default {
  name: 'SharePoint',
  apiId: 'shared_sharepointonline',
  envConnectionIdKey: 'VITE_SP_CONNECTION_ID',

  isConfigured(env) {
    return (env.VITE_BACKEND_TYPE ?? 'sharepoint') === 'sharepoint';
  },
  getResources(env) {
    return (env.VITE_SP_LISTS ?? '')
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
  },
  getDataset(env) {
    return env.VITE_SP_SITE_URL ?? '';
  },
  buildArgs(connectionId, dataset, resourceName) {
    return [
      'power-apps',
      'add-data-source',
      '--api-id', 'shared_sharepointonline',
      '--connection-id', connectionId,
      '--resource-name', resourceName,
      '--dataset', dataset,
    ];
  },
};
