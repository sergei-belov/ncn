import type { UUID } from "@/shared/lib/domain-primitives";

export type StateGroup = "backlog" | "unstarted" | "started" | "completed" | "cancelled";

export interface WorkflowState {
  id: UUID;
  projectId: UUID;
  name: string;
  color: string;
  group: StateGroup;
  order: number;
  isDefault: boolean;
  version: number;
}

export interface CreateStateInput {
  name: string;
  color: string;
  group: StateGroup;
}

export interface UpdateStateInput extends Partial<CreateStateInput> {
  isDefault?: boolean;
}
