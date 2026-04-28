// Office 365 Users — Current user + people search for People Picker.
// Falls back to LOCAL_USER / SAMPLE_USERS when not running inside the PA player.

import { Office365UsersService } from '../generated/services/Office365UsersService.ts';

export interface UserProfile {
  displayName: string;
  email: string;
  jobTitle?: string;
  id?: string;
}

const LOCAL_USER: UserProfile = {
  displayName: 'Local User',
  email: 'localuser@localhost.dev',
  jobTitle: 'Developer (Local Mode)',
};

// Add your team members here for local-dev testing
const SAMPLE_USERS: UserProfile[] = [
  { displayName: 'Krupesh Patel', email: 'kpatel@huntoil.com', jobTitle: 'Developer' },
  { displayName: 'Bob Smith', email: 'bsmith@huntoil.com', jobTitle: 'Manager' },
  { displayName: 'Alice Johnson', email: 'ajohnson@huntoil.com', jobTitle: 'Director' },
];

export async function getCurrentUser(): Promise<UserProfile> {
  try {
    const { getContext } = await import('@microsoft/power-apps/app');
    const ctx = await getContext();
    if ((ctx as any)?.user?.fullName) {
      const profile: UserProfile = {
        displayName: (ctx as any).user.fullName,
        email: (ctx as any).user.userPrincipalName ?? '',
        id: (ctx as any).user.objectId ?? '',
      };
      try {
        const result = await Office365UsersService.MyProfile_V2();
        if (result.data) {
          profile.email = (result.data as any).mail ?? (result.data as any).userPrincipalName ?? profile.email;
          profile.jobTitle = (result.data as any).jobTitle ?? undefined;
        }
      } catch {
        /* O365 enrichment is optional */
      }
      return profile;
    }
  } catch {
    /* not in PA player */
  }
  return LOCAL_USER;
}

export async function searchUsers(query: string): Promise<UserProfile[]> {
  if (!query || query.length < 2) return [];

  try {
    const result = await Office365UsersService.SearchUser(query, 10);
    if (result.data && Array.isArray(result.data)) {
      return result.data
        .filter((u: any) => u.DisplayName && (u.Mail || u.UserPrincipalName))
        .map((u: any) => ({
          displayName: u.DisplayName ?? '',
          email: u.Mail ?? u.UserPrincipalName ?? '',
          jobTitle: u.JobTitle ?? undefined,
          id: u.Id,
        }));
    }
  } catch (err) {
    console.warn('[UserService] O365 search failed → sample users:', (err as Error).message);
  }

  const q = query.toLowerCase();
  return SAMPLE_USERS.filter(
    (u) => u.displayName.toLowerCase().includes(q) || u.email.toLowerCase().includes(q),
  );
}
