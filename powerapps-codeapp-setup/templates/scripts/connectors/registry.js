import sharepoint from './sharepoint.js';
import office365users from './office365users.js';
import office365outlook from './office365outlook.js';

// Order matters — SharePoint always first.
export const CONNECTORS = [sharepoint, office365users, office365outlook];
