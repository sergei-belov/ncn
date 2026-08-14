import { inject, type InjectionKey } from "vue";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { CreateWorkItemInput, UpdateWorkItemInput, WorkItem } from "../model/types";

export interface WorkItemApi {
  getWorkItem(workspaceSlug: string, projectId: UUID, workItemId: UUID, signal?: AbortSignal): Promise<WorkItem>;
  createWorkItem(workspaceSlug: string, projectId: UUID, input: CreateWorkItemInput): Promise<WorkItem>;
  updateWorkItem(
    workspaceSlug: string,
    projectId: UUID,
    workItemId: UUID,
    input: UpdateWorkItemInput,
    version: number,
  ): Promise<WorkItem>;
  deleteWorkItem(workspaceSlug: string, projectId: UUID, workItemId: UUID, version: number): Promise<void>;
}

export const workItemApiKey: InjectionKey<WorkItemApi> = Symbol("work-item-api");

export function useWorkItemApi(): WorkItemApi {
  const api = inject(workItemApiKey);
  if (!api) throw new Error("Work item API provider is not installed");
  return api;
}
