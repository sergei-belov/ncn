import { describe, expect, it } from "vitest";

import { moveInColumns, neighborIds, placementForCardEdge, type BoardColumn } from "@/entities/board";

const columns: BoardColumn[] = [
  { stateId: "todo", workItemIds: ["a", "b", "c"], totalCount: 3, nextCursor: null },
  { stateId: "done", workItemIds: ["d", "e"], totalCount: 2, nextCursor: null },
];

describe("board ordering", () => {
  it("moves a card between columns using neighbors", () => {
    const result = moveInColumns(columns, {
      workItemId: "b",
      fromStateId: "todo",
      toStateId: "done",
      beforeWorkItemId: "e",
      afterWorkItemId: "d",
    });

    expect(result[0]?.workItemIds).toEqual(["a", "c"]);
    expect(result[1]?.workItemIds).toEqual(["d", "b", "e"]);
    expect(result[1]?.totalCount).toBe(3);
  });

  it("reorders inside the same column without duplicates", () => {
    const result = moveInColumns(columns, {
      workItemId: "c",
      fromStateId: "todo",
      toStateId: "todo",
      beforeWorkItemId: "a",
    });

    expect(result[0]?.workItemIds).toEqual(["c", "a", "b"]);
  });

  it("resolves neighbor ids for an insertion position", () => {
    expect(neighborIds(["a", "b", "c"], 1)).toEqual({ beforeWorkItemId: "b", afterWorkItemId: "a" });
  });

  it("inserts between cards using the target edge", () => {
    const before = moveInColumns(columns, {
      workItemId: "c",
      fromStateId: "todo",
      toStateId: "todo",
      ...placementForCardEdge("b", "top"),
    });
    const after = moveInColumns(columns, {
      workItemId: "d",
      fromStateId: "done",
      toStateId: "todo",
      ...placementForCardEdge("b", "bottom"),
    });

    expect(before[0]?.workItemIds).toEqual(["a", "c", "b"]);
    expect(after[0]?.workItemIds).toEqual(["a", "b", "d", "c"]);
    expect(after[1]?.workItemIds).toEqual(["e"]);
  });
});
