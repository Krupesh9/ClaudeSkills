// Office 365 Outlook — fire-and-forget email notifications.
// Always wrap calls in .catch(() => {}) so email failure never blocks CRUD.

import { OUTLOOK_ENABLED } from '../config';
import { getBackend } from './dataService';
import { Office365OutlookService } from '../generated/services/Office365OutlookService.ts';
import * as templates from './emailTemplates';
import type { MyRecord } from '../types/myTypes';

type NotificationType = 'submitted' | 'approved' | 'rejected';

export async function sendNotification(
  type: NotificationType,
  record: MyRecord,
  comment?: string,
): Promise<void> {
  let email: { to: string; subject: string; body: string };

  switch (type) {
    case 'submitted':
      email = templates.requestSubmittedEmail(record);
      break;
    case 'approved':
      email = templates.requestApprovedEmail(record, comment ?? '');
      break;
    case 'rejected':
      email = templates.requestRejectedEmail(record, comment ?? '');
      break;
  }

  if (getBackend() === 'localStorage') {
    console.log(`[Notification] Would send ${type} email:`, { to: email.to, subject: email.subject });
    return;
  }

  if (!OUTLOOK_ENABLED) {
    console.log(`[Notification] Outlook not enabled — skipping ${type} email`);
    return;
  }

  try {
    await Office365OutlookService.SendEmailV2({
      To: email.to,
      Subject: email.subject,
      Body: email.body,
    } as any);
    console.log(`[Notification] Sent ${type} email to ${email.to}`);
  } catch (err) {
    console.warn(`[Notification] Failed to send ${type} email:`, (err as Error).message);
  }
}
