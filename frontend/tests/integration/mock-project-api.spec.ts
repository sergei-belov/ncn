import { describe, expect, it } from "vitest";

import { mockProjectManagementApi } from "@/app/mocks/project-management-api";

describe("mock project API", () => {
  it("creates a project with the default workflow", async () => {
    const created = await mockProjectManagementApi.createProject("demo", {
      name: "Release Hub",
      identifier: "REL",
      access: "private",
    });
    const states = await mockProjectManagementApi.listStates("demo", created.id);
    const agents = await mockProjectManagementApi.listAgents("demo", created.id);

    expect(states).toHaveLength(4);
    expect(states[0]?.isDefault).toBe(true);
    expect(states.map((state) => state.group)).toEqual(["backlog", "unstarted", "started", "completed"]);
    expect(agents).toHaveLength(1);
    expect(agents[0]).toMatchObject({ kind: "coordinator", status: "active", systemToolNames: ["task-management"] });
  });

  it("moves a work item and increments board version", async () => {
    const board = await mockProjectManagementApi.getBoard("demo", "project-web", {});
    const item = board.workItems.find((candidate) => candidate.id === "wi-web-2")!;
    const result = await mockProjectManagementApi.moveWorkItem("demo", "project-web", {
      workItemId: item.id,
      fromStateId: item.stateId,
      toStateId: "web-done",
      afterWorkItemId: "wi-web-4",
      entityVersion: item.version,
      boardVersion: board.boardVersion,
      clientMutationId: crypto.randomUUID(),
    });

    expect(result.workItem.stateId).toBe("web-done");
    expect(result.boardVersion).toBe(board.boardVersion + 1);
    expect(result.columns.find((column) => column.stateId === "web-done")?.workItemIds).toContain(item.id);
  });

  it("updates, archives, and restores a versioned project", async () => {
    const project = await mockProjectManagementApi.getProject("demo", "project-web");
    const updated = await mockProjectManagementApi.updateProject(
      "demo",
      project.id,
      { name: "Кабинет 2.0" },
      project.version,
    );
    const archived = await mockProjectManagementApi.archiveProject("demo", updated.id, updated.version);
    const restored = await mockProjectManagementApi.restoreProject("demo", archived.id, archived.version);

    expect(updated.name).toBe("Кабинет 2.0");
    expect(archived.archivedAt).not.toBeNull();
    expect(restored.archivedAt).toBeNull();
    expect(restored.version).toBe(project.version + 3);
  });

  it("creates, updates, reads, and deletes a work item", async () => {
    const created = await mockProjectManagementApi.createWorkItem("demo", "project-web", {
      title: "Проверить ресурсный порт",
      stateId: "web-todo",
    });
    const updated = await mockProjectManagementApi.updateWorkItem(
      "demo",
      "project-web",
      created.id,
      { priority: "high", dueDate: "2026-08-31" },
      created.version,
    );

    expect(await mockProjectManagementApi.getWorkItem("demo", "project-web", created.id)).toMatchObject({
      priority: "high",
      dueDate: "2026-08-31",
    });

    await mockProjectManagementApi.deleteWorkItem("demo", "project-web", created.id, updated.version);
    await expect(mockProjectManagementApi.getWorkItem("demo", "project-web", created.id)).rejects.toMatchObject({
      status: 404,
    });
  });

  it("manages epic membership and unlinks cards when deleting an epic", async () => {
    const created = await mockProjectManagementApi.createEpic("demo", "project-web", { name: "Migration parity" });
    const updated = await mockProjectManagementApi.updateEpic(
      "demo",
      "project-web",
      created.id,
      { description: "Resource ports" },
      created.version,
    );
    const withItems = await mockProjectManagementApi.setEpicWorkItems("demo", "project-web", created.id, ["wi-web-2"]);

    expect(withItems.workItemIds).toEqual(["wi-web-2"]);
    expect((await mockProjectManagementApi.getWorkItem("demo", "project-web", "wi-web-2")).epicId).toBe(created.id);

    await mockProjectManagementApi.deleteEpic("demo", "project-web", created.id, withItems.version);
    expect((await mockProjectManagementApi.getWorkItem("demo", "project-web", "wi-web-2")).epicId).toBeNull();
    expect(updated.description).toBe("Resource ports");
  });

  it("edits and reorders states, then migrates cards on safe deletion", async () => {
    const created = await mockProjectManagementApi.createState("demo", "project-web", {
      name: "Review",
      color: "#a855f7",
      group: "started",
    });
    const workItem = await mockProjectManagementApi.createWorkItem("demo", "project-web", {
      title: "Card in removable state",
      stateId: created.id,
    });
    const updated = await mockProjectManagementApi.updateState(
      "demo",
      "project-web",
      created.id,
      { name: "Code review" },
      created.version,
    );
    const states = await mockProjectManagementApi.listStates("demo", "project-web");
    const reordered = await mockProjectManagementApi.reorderStates("demo", "project-web", [
      updated.id,
      ...states.filter((state) => state.id !== updated.id).map((state) => state.id),
    ]);

    expect(reordered[0]?.name).toBe("Code review");
    await mockProjectManagementApi.deleteState("demo", "project-web", updated.id, "web-todo");
    expect((await mockProjectManagementApi.getWorkItem("demo", "project-web", workItem.id)).stateId).toBe("web-todo");
    expect((await mockProjectManagementApi.listStates("demo", "project-web")).some((state) => state.id === updated.id)).toBe(false);
  });

  it("creates and manages a project-scoped worker while protecting the coordinator", async () => {
    const created = await mockProjectManagementApi.createAgent("demo", "project-web", {
      name: "Аналитик поставщиков",
      description: "Сравнивает предложения",
      instructions: "Сравнивай цены, сроки и риски поставщиков, затем возвращай структурированную рекомендацию.",
      model: "qwen3:14b",
      memoryPolicy: "project",
      maxStepsPerRun: 25,
      approvalMode: "always",
    });
    const updated = await mockProjectManagementApi.updateAgent(
      "demo",
      "project-web",
      created.id,
      { description: "Сравнивает предложения и сроки" },
      created.version,
    );
    const disabled = await mockProjectManagementApi.setAgentEnabled(
      "demo",
      "project-web",
      updated.id,
      false,
      updated.version,
    );
    const archived = await mockProjectManagementApi.archiveAgent("demo", "project-web", disabled.id, disabled.version);
    const coordinator = (await mockProjectManagementApi.listAgents("demo", "project-web")).find(
      (agent) => agent.kind === "coordinator",
    )!;

    expect(created.kind).toBe("worker");
    expect(disabled.status).toBe("disabled");
    expect(archived.status).toBe("archived");
    await expect(mockProjectManagementApi.getAgent("demo", "project-ncn", created.id)).rejects.toMatchObject({ status: 404 });
    await expect(
      mockProjectManagementApi.setAgentEnabled("demo", "project-web", coordinator.id, false, coordinator.version),
    ).rejects.toMatchObject({ code: "COORDINATOR_REQUIRED" });
    await expect(
      mockProjectManagementApi.archiveAgent("demo", "project-web", coordinator.id, coordinator.version),
    ).rejects.toMatchObject({ code: "COORDINATOR_REQUIRED" });
  });
});
