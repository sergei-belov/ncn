import { z } from "zod";

import type { MemberSummary } from "../model/types";

export const wireMemberSchema = z.object({
  id: z.string(),
  display_name: z.string(),
  email: z.string().default(""),
  avatar_url: z.string().nullable(),
  initials: z.string().optional(),
  is_active: z.boolean(),
});

export function mapMember(value: z.infer<typeof wireMemberSchema>): MemberSummary {
  return {
    id: value.id,
    displayName: value.display_name,
    email: value.email,
    avatarUrl: value.avatar_url,
    initials:
      value.initials ??
      value.display_name
        .split(" ")
        .map((part) => part[0])
        .join("")
        .slice(0, 2),
    isActive: value.is_active,
  };
}
