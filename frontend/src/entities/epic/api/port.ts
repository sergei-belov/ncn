import { inject, type InjectionKey } from "vue";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { CreateEpicInput, Epic, EpicFilters, UpdateEpicInput } from "../model/types";

export interface EpicApi {
  listEpics(workspaceSlug: string, projectId: UUID, filters: EpicFilters, signal?: AbortSignal): Promise<Epic[]>;
  getEpic(workspaceSlug: string, projectId: UUID, epicId: UUID, signal?: AbortSignal): Promise<Epic>;
  createEpic(workspaceSlug: string, projectId: UUID, input: CreateEpicInput): Promise<Epic>;
  updateEpic(workspaceSlug: string, projectId: UUID, epicId: UUID, input: UpdateEpicInput, version: number): Promise<Epic>;
  deleteEpic(workspaceSlug: string, projectId: UUID, epicId: UUID, version: number): Promise<void>;
  setEpicWorkItems(workspaceSlug: string, projectId: UUID, epicId: UUID, workItemIds: UUID[]): Promise<Epic>;
}

export const epicApiKey: InjectionKey<EpicApi> = Symbol("epic-api");

export function useEpicApi(): EpicApi {
  const api = inject(epicApiKey);
  if (!api) throw new Error("Epic API provider is not installed");
  return api;
}
