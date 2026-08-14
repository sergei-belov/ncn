import type { ISODate, ISODateTime, UUID } from "@/shared/lib/domain-primitives";

export interface Epic {
  id: UUID;
  projectId: UUID;
  name: string;
  description: string;
  color: string;
  startDate: ISODate | null;
  targetDate: ISODate | null;
  workItemIds: UUID[];
  progress: {
    total: number;
    completed: number;
    percentage: number;
  };
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
  version: number;
}

export interface EpicFilters {
  search?: string;
}

export interface CreateEpicInput {
  name: string;
  description?: string;
  color?: string;
  startDate?: ISODate | null;
  targetDate?: ISODate | null;
}

export type UpdateEpicInput = Partial<CreateEpicInput>;
