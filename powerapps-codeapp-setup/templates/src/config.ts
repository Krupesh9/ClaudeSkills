// ─────────────────────────────────────────────────────────────────────────────
// Centralized environment configuration.
// This is the ONLY file that reads import.meta.env.VITE_* variables.
// All other files import constants from here.
// ─────────────────────────────────────────────────────────────────────────────

export const BACKEND_TYPE     = import.meta.env.VITE_BACKEND_TYPE      ?? 'sharepoint';

// SharePoint
export const SP_SITE_URL      = import.meta.env.VITE_SP_SITE_URL       ?? '';
export const SP_LISTS         = import.meta.env.VITE_SP_LISTS          ?? '';
export const SP_CONNECTOR_ID  = 'shared_sharepointonline';
export const SP_CONNECTION_ID = import.meta.env.VITE_SP_CONNECTION_ID  ?? '';

// Office 365 Users (People Picker)
export const O365U_ENABLED       = import.meta.env.VITE_O365U_ENABLED === 'true';
export const O365U_CONNECTION_ID = import.meta.env.VITE_O365U_CONNECTION_ID ?? '';

// Office 365 Outlook (Email Notifications)
export const OUTLOOK_ENABLED       = import.meta.env.VITE_OUTLOOK_ENABLED === 'true';
export const OUTLOOK_CONNECTION_ID = import.meta.env.VITE_OUTLOOK_CONNECTION_ID ?? '';

// App identity (deep links)
export const APP_ID            = import.meta.env.VITE_APP_ID            ?? '';
export const PP_ENVIRONMENT_ID = import.meta.env.VITE_PP_ENVIRONMENT_ID ?? '';

// Display
export const APP_ENV_LABEL    = import.meta.env.VITE_APP_ENV_LABEL     ?? '';
export const APP_DISPLAY_NAME = import.meta.env.VITE_APP_DISPLAY_NAME  ?? '';
