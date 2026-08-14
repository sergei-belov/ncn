import type { UUID } from "@/shared/lib/domain-primitives";

export interface MemberSummary {
  id: UUID;
  displayName: string;
  email: string;
  avatarUrl: string | null;
  initials: string;
  isActive: boolean;
}
