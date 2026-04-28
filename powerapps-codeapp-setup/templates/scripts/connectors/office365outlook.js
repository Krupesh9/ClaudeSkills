export default {
  name: 'Office 365 Outlook',
  apiId: 'shared_office365',
  envConnectionIdKey: 'VITE_OUTLOOK_CONNECTION_ID',

  isConfigured(env) {
    return env.VITE_OUTLOOK_ENABLED === 'true';
  },
  getResources() {
    return ['SendAnEmail_V2'];
  },
  getDataset() {
    return '';
  },
  buildArgs(connectionId, _dataset, resourceName) {
    return [
      'power-apps',
      'add-data-source',
      '--api-id', 'shared_office365',
      '--connection-id', connectionId,
      '--resource-name', resourceName,
    ];
  },
};
