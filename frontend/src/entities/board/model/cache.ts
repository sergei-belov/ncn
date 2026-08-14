import type { WorkItem } from "@/entities/work-item/@x/board";

import { moveInColumns } from "./order";
import type { BoardPayload, MoveCommand, MoveWorkItemResult } from "./types";

export function insertWorkItem(payload: BoardPayload, workItem: WorkItem): BoardPayload {
  const workItems = payload.workItems.some((item) => item.id === workItem.id)
    ? payload.workItems.map((item) => (item.id === workItem.id ? workItem : item))
    : [...payload.workItems, workItem];
  const columns = payload.columns.map((column) => {
    if (column.stateId !== workItem.stateId || column.workItemIds.includes(workItem.id)) return column;
    return { ...column, workItemIds: [...column.workItemIds, workItem.id], totalCount: column.totalCount + 1 };
  });
  return { ...payload, workItems, columns };
}

export function updateWorkItem(payload: BoardPayload, workItem: WorkItem): BoardPayload {
  const previous = payload.workItems.find((item) => item.id === workItem.id);
  if (!previous) return payload;
  let columns = payload.columns;
  if (previous.stateId !== workItem.stateId) {
    columns = moveInColumns(payload.columns, {
      workItemId: workItem.id,
      fromStateId: previous.stateId,
      toStateId: workItem.stateId,
    });
  }
  return {
    ...payload,
    columns,
    workItems: payload.workItems.map((item) => (item.id === workItem.id ? workItem : item)),
  };
}

export function removeWorkItem(payload: BoardPayload, workItemId: string): BoardPayload {
  return {
    ...payload,
    workItems: payload.workItems.filter((item) => item.id !== workItemId),
    columns: payload.columns.map((column) => {
      const workItemIds = column.workItemIds.filter((id) => id !== workItemId);
      return { ...column, workItemIds, totalCount: workItemIds.length };
    }),
  };
}

export function moveWorkItemOptimistically(payload: BoardPayload, command: MoveCommand): BoardPayload {
  if (!payload.workItems.some((item) => item.id === command.workItemId)) return payload;
  return {
    ...payload,
    columns: moveInColumns(payload.columns, command),
    workItems: payload.workItems.map((item) =>
      item.id === command.workItemId ? { ...item, stateId: command.toStateId } : item,
    ),
  };
}

export function commitWorkItemMove(payload: BoardPayload, result: MoveWorkItemResult): BoardPayload {
  if (!payload.workItems.some((item) => item.id === result.workItem.id)) return payload;
  return {
    ...payload,
    workItems: payload.workItems.map((item) => (item.id === result.workItem.id ? result.workItem : item)),
    columns: result.columns.map((column) => ({ ...column, workItemIds: [...column.workItemIds] })),
    boardVersion: result.boardVersion,
  };
}
