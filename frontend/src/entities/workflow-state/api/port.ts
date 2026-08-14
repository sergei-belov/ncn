import { inject, type InjectionKey } from "vue";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { CreateStateInput, UpdateStateInput, WorkflowState } from "../model/types";

export interface WorkflowStateApi {
  listStates(workspaceSlug: string, projectId: UUID, signal?: AbortSignal): Promise<WorkflowState[]>;
  createState(workspaceSlug: string, projectId: UUID, input: CreateStateInput): Promise<WorkflowState>;
  updateState(
    workspaceSlug: string,
    projectId: UUID,
    stateId: UUID,
    input: UpdateStateInput,
    version: number,
  ): Promise<WorkflowState>;
  reorderStates(workspaceSlug: string, projectId: UUID, orderedStateIds: UUID[]): Promise<WorkflowState[]>;
  deleteState(workspaceSlug: string, projectId: UUID, stateId: UUID, replacementStateId: UUID): Promise<void>;
}

export const workflowStateApiKey: InjectionKey<WorkflowStateApi> = Symbol("workflow-state-api");

export function useWorkflowStateApi(): WorkflowStateApi {
  const api = inject(workflowStateApiKey);
  if (!api) throw new Error("Workflow state API provider is not installed");
  return api;
}
