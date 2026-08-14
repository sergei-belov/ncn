import { describe, expect, it } from "vitest";

import { mockProjectManagementApi } from "@/app/mocks/project-management-api";
import { moveWorkItemOptimistically } from "@/entities/board";

describe("board query-cache helpers", () => {
  it("creates an immutable optimistic board snapshot", async () => {
    const board = await mockProjectManagementApi.getBoard("demo", "project-web", {});
    const optimistic = moveWorkItemOptimistically(board, {
      workItemId: "wi-web-2",
      fromStateId: "web-todo",
      toStateId: "web-done",
      afterWorkItemId: "wi-web-4",
    });

    expect(optimistic).not.toBe(board);
    expect(optimistic.workItems.find((item) => item.id === "wi-web-2")?.stateId).toBe("web-done");
    expect(optimistic.columns.find((column) => column.stateId === "web-done")?.workItemIds).toContain("wi-web-2");
    expect(board.workItems.find((item) => item.id === "wi-web-2")?.stateId).toBe("web-todo");
  });
});
