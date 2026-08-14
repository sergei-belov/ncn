import { describe, expect, it } from "vitest";

import { replaceAgentInList, withAgentStatus, type Agent } from "@/entities/agent";

const worker: Agent = {
  id: "agent-risk",
  projectId: "project-web",
  kind: "worker",
  name: "Аналитик рисков",
  description: "",
  instructions: "Анализируй риски проекта и возвращай рекомендации.",
  model: "qwen3:14b",
  memoryPolicy: "project",
  maxStepsPerRun: 25,
  approvalMode: "project",
  status: "active",
  systemToolNames: [],
  createdAt: "2026-08-01T00:00:00.000Z",
  updatedAt: "2026-08-01T00:00:00.000Z",
  version: 1,
};

describe("agent query-cache helpers", () => {
  it("creates immutable status and list snapshots", () => {
    const disabled = withAgentStatus(worker, "disabled");
    const list = [worker];
    const updatedList = replaceAgentInList(list, disabled);

    expect(worker.status).toBe("active");
    expect(disabled).not.toBe(worker);
    expect(updatedList).not.toBe(list);
    expect(updatedList?.[0]?.status).toBe("disabled");
  });
});
