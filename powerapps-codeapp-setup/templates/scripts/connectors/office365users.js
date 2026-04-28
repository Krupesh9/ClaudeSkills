export default {
  name: 'Office 365 Users',
  apiId: 'shared_office365users',
  envConnectionIdKey: 'VITE_O365U_CONNECTION_ID',

  isConfigured(env) {
    return env.VITE_O365U_ENABLED === 'true';
  },
  getResources() {
    // Single virtual resource — wires up MyProfile / SearchUser etc.
    return ['MyProfile'];
  },
  getDataset() {
    return '';
  },
  buildArgs(connectionId, _dataset, resourceName) {
    return [
      'power-apps',
      'add-data-source',
      '--api-id', 'shared_office365users',
      '--connection-id', connectionId,
      '--resource-name', resourceName,
    ];
  },
};
