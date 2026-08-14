import type { Epic } from "@/entities/epic/@x/board";
import type { MemberSummary } from "@/entities/member/@x/board";
import type { Project } from "@/entities/project/@x/board";
import type { WorkItem } from "@/entities/work-item/@x/board";
import type { Priority } from "@/entities/work-item/@x/board";
import type { WorkflowState } from "@/entities/workflow-state/@x/board";
import type { UUID } from "@/shared/lib/domain-primitives";

export interface BoardColumn {
  stateId: UUID;
  workItemIds: UUID[];
  totalCount: number;
  nextCursor: string | null;
}

export interface BoardPayload {
  project: Project;
  states: WorkflowState[];
  workItems: WorkItem[];
  epics: Epic[];
  members: MemberSummary[];
  columns: BoardColumn[];
  boardVersion: number;
}

export interface BoardFilters {
  search?: string;
  priorities?: Priority[];
  epicId?: UUID | null;
  assigneeId?: UUID | null;
}

export interface MoveWorkItemInput {
  workItemId: UUID;
  fromStateId: UUID;
  toStateId: UUID;
  beforeWorkItemId?: UUID;
  afterWorkItemId?: UUID;
  entityVersion: number;
  boardVersion: number;
  clientMutationId: UUID;
}

export interface MoveWorkItemResult {
  workItem: WorkItem;
  columns: BoardColumn[];
  boardVersion: number;
}

export type MoveCommand = Pick<
  MoveWorkItemInput,
  "workItemId" | "fromStateId" | "toStateId" | "beforeWorkItemId" | "afterWorkItemId"
>;
