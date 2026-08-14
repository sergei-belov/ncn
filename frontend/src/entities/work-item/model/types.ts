import type { ISODate, ISODateTime, UUID } from "@/shared/lib/domain-primitives";

export type Priority = "none" | "low" | "medium" | "high" | "urgent";

export interface WorkItem {
  id: UUID;
  projectId: UUID;
  sequenceId: number;
  identifier: string;
  title: string;
  descriptionHtml: string;
  stateId: UUID;
  priority: Priority;
  assigneeIds: UUID[];
  epicId: UUID | null;
  startDate: ISODate | null;
  dueDate: ISODate | null;
  sortOrder: number;
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
  version: number;
}

export interface CreateWorkItemInput {
  title: string;
  stateId: UUID;
  priority?: Priority;
  descriptionHtml?: string;
  assigneeIds?: UUID[];
  epicId?: UUID | null;
  startDate?: ISODate | null;
  dueDate?: ISODate | null;
}

export interface UpdateWorkItemInput {
  title?: string;
  descriptionHtml?: string;
  stateId?: UUID;
  priority?: Priority;
  assigneeIds?: UUID[];
  epicId?: UUID | null;
  startDate?: ISODate | null;
  dueDate?: ISODate | null;
}
