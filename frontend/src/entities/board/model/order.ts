import type { UUID } from "@/shared/lib/domain-primitives";

import type { BoardColumn, MoveWorkItemInput } from "./types";

export function moveInColumns(
  columns: BoardColumn[],
  input: Pick<MoveWorkItemInput, "workItemId" | "fromStateId" | "toStateId" | "beforeWorkItemId" | "afterWorkItemId">,
): BoardColumn[] {
  const next = columns.map((column) => ({ ...column, workItemIds: [...column.workItemIds] }));
  const source = next.find((column) => column.stateId === input.fromStateId);
  const target = next.find((column) => column.stateId === input.toStateId);
  if (!source || !target) return next;

  source.workItemIds = source.workItemIds.filter((id) => id !== input.workItemId);
  if (source !== target) target.workItemIds = target.workItemIds.filter((id) => id !== input.workItemId);

  let index = target.workItemIds.length;
  if (input.beforeWorkItemId) {
    const beforeIndex = target.workItemIds.indexOf(input.beforeWorkItemId);
    if (beforeIndex >= 0) index = beforeIndex;
  } else if (input.afterWorkItemId) {
    const afterIndex = target.workItemIds.indexOf(input.afterWorkItemId);
    if (afterIndex >= 0) index = afterIndex + 1;
  }
  target.workItemIds.splice(index, 0, input.workItemId);
  source.totalCount = source.workItemIds.length;
  target.totalCount = target.workItemIds.length;
  return next;
}

export function neighborIds(ids: UUID[], index: number): { beforeWorkItemId?: UUID; afterWorkItemId?: UUID } {
  const beforeWorkItemId = ids[index];
  const afterWorkItemId = index > 0 ? ids[index - 1] : undefined;
  return { beforeWorkItemId, afterWorkItemId };
}

export function placementForCardEdge(
  targetWorkItemId: UUID,
  edge: "top" | "bottom",
): { beforeWorkItemId?: UUID; afterWorkItemId?: UUID } {
  return edge === "top" ? { beforeWorkItemId: targetWorkItemId } : { afterWorkItemId: targetWorkItemId };
}
