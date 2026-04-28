import { APP_ID, PP_ENVIRONMENT_ID, APP_DISPLAY_NAME } from '../config';
import type { MyRecord } from '../types/myTypes';

function buildDeepLink(recordId: string): string {
  if (!APP_ID || !PP_ENVIRONMENT_ID) return '';
  return `https://apps.powerapps.com/play/e/${PP_ENVIRONMENT_ID}/a/${APP_ID}?recordId=${recordId}`;
}

function actionButtonHtml(label: string, url: string, color: string): string {
  if (!url) return '';
  return `
    <div style="text-align: center; margin: 24px 0 8px;">
      <a href="${url}" target="_blank" style="display: inline-block; background: ${color}; color: #ffffff; padding: 12px 32px; border-radius: 6px; font-size: 14px; font-weight: 600; text-decoration: none;">
        ${label}
      </a>
    </div>
  `;
}

function baseTemplate(title: string, bodyHtml: string): string {
  return `
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
      <div style="background: #1E3A5F; padding: 20px 24px;">
        <h1 style="margin: 0; color: #ffffff; font-size: 18px; font-weight: 600;">${title}</h1>
      </div>
      <div style="padding: 24px;">${bodyHtml}</div>
      <div style="padding: 16px 24px; background: #f9fafb; border-top: 1px solid #e5e7eb; text-align: center;">
        <p style="margin: 0; color: #9ca3af; font-size: 12px;">Sent by ${APP_DISPLAY_NAME} — Do not reply</p>
      </div>
    </div>
  `;
}

export function requestSubmittedEmail(record: MyRecord) {
  const deepLink = buildDeepLink(record.id);
  return {
    to: record.assigneeEmail ?? '',
    subject: `[${APP_DISPLAY_NAME}] Action Required: ${record.title}`,
    body: baseTemplate(
      'New Request',
      `
        <p>Hi <strong>${record.assignee ?? 'there'}</strong>, you have a new request:</p>
        <table style="width: 100%; margin: 16px 0; border-collapse: collapse;">
          <tr><td style="padding: 6px 0; color: #6b7280; font-size: 13px; width: 130px;">Title</td><td style="padding: 6px 0; color: #111827; font-size: 13px; font-weight: 600;">${record.title}</td></tr>
          ${record.dueDate ? `<tr><td style="padding: 6px 0; color: #6b7280; font-size: 13px;">Due Date</td><td style="padding: 6px 0; color: #111827; font-size: 13px;">${record.dueDate}</td></tr>` : ''}
        </table>
        ${actionButtonHtml('Review & Approve', deepLink, '#1E3A5F')}
      `,
    ),
  };
}

export function requestApprovedEmail(record: MyRecord, comment: string) {
  const deepLink = buildDeepLink(record.id);
  return {
    to: record.assigneeEmail ?? '',
    subject: `[${APP_DISPLAY_NAME}] Approved: ${record.title}`,
    body: baseTemplate(
      'Request Approved',
      `
        <p>Your request <strong>${record.title}</strong> has been approved.</p>
        ${comment ? `<p style="margin-top: 12px; padding: 12px; background: #f9fafb; border-radius: 6px; font-style: italic; color: #4b5563;">"${comment}"</p>` : ''}
        ${actionButtonHtml('View Details', deepLink, '#10B981')}
      `,
    ),
  };
}

export function requestRejectedEmail(record: MyRecord, comment: string) {
  const deepLink = buildDeepLink(record.id);
  return {
    to: record.assigneeEmail ?? '',
    subject: `[${APP_DISPLAY_NAME}] Rejected: ${record.title}`,
    body: baseTemplate(
      'Request Rejected',
      `
        <p>Your request <strong>${record.title}</strong> was not approved.</p>
        ${comment ? `<p style="margin-top: 12px; padding: 12px; background: #fef2f2; border-radius: 6px; font-style: italic; color: #991b1b;">"${comment}"</p>` : ''}
        ${actionButtonHtml('View Details', deepLink, '#EF4444')}
      `,
    ),
  };
}
