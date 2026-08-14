import { inject, type InjectionKey } from "vue";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { BoardFilters, BoardPayload, MoveWorkItemInput, MoveWorkItemResult } from "../model/types";

export interface BoardApi {
  getBoard(workspaceSlug: string, projectId: UUID, filters: BoardFilters, signal?: AbortSignal): Promise<BoardPayload>;
  moveWorkItem(workspaceSlug: string, projectId: UUID, input: MoveWorkItemInput): Promise<MoveWorkItemResult>;
}

export const boardApiKey: InjectionKey<BoardApi> = Symbol("board-api");

export function useBoardApi(): BoardApi {
  const api = inject(boardApiKey);
  if (!api) throw new Error("Board API provider is not installed");
  return api;
}
