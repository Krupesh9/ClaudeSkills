# Checklist — Add Email Notifications (Office 365 Outlook)

## Pre-flight
- [ ] Office 365 Outlook connection exists in the target environment
- [ ] App ID known (`VITE_APP_ID` set) — required for deep links inside emails

## Wire connector
- [ ] Set `VITE_OUTLOOK_ENABLED=true` in `.env`
- [ ] `npm run connect`
- [ ] Confirm `src/generated/services/Office365OutlookService.ts` exists
- [ ] Confirm `.env` has `VITE_OUTLOOK_CONNECTION_ID=<id>`

## Code
- [ ] Confirm `src/services/notificationService.ts` is present
- [ ] Confirm `src/services/emailTemplates.ts` is present — customize templates per your tone/branding
- [ ] In `dataService.ts`, after a successful create/update, fire-and-forget the notification:
  ```typescript
  notifyApprover(item).catch(() => {});

  async function notifyApprover(item: MyRecord) {
    const { sendNotification } = await import('./notificationService');
    return sendNotification('submitted', item);
  }
  ```

## Test
- [ ] Trigger the notification path from the UI
- [ ] Confirm email lands in the recipient's inbox
- [ ] Click the deep link → app opens directly to that record
- [ ] If email doesn't arrive: check F12 console for `[Notification]` logs, confirm Outlook connection is healthy
