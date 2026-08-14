import { describe, expect, it } from "vitest";

import { epicSchema } from "@/features/epic-create";
import { agentSchema, toAgentInput } from "@/features/agent-manage";
import { projectSchema } from "@/features/project-create";

describe("form schemas", () => {
  it("normalizes a valid project identifier", () => {
    const result = projectSchema.parse({ name: "Новый проект", identifier: "web2", description: "", access: "workspace" });
    expect(result.identifier).toBe("WEB2");
  });

  it("rejects invalid project identifiers", () => {
    expect(() => projectSchema.parse({ name: "Проект", identifier: "я", description: "", access: "private" })).toThrow();
  });

  it("rejects an epic target date before its start", () => {
    const result = epicSchema.safeParse({
      name: "Запуск",
      description: "",
      color: "#8b5cf6",
      startDate: "2026-08-20",
      targetDate: "2026-08-10",
    });
    expect(result.success).toBe(false);
  });

  it("validates agent instructions and maps the run limit to a number", () => {
    const values = agentSchema.parse({
      name: "Аналитик рисков",
      description: "Проверяет сроки",
      instructions: "Анализируй сроки, зависимости и явно перечисляй найденные риски.",
      model: "qwen3:14b",
      memoryPolicy: "project",
      maxStepsPerRun: "25",
      approvalMode: "project",
    });

    expect(toAgentInput(values)).toMatchObject({ maxStepsPerRun: 25, memoryPolicy: "project" });
    expect(agentSchema.safeParse({ ...values, instructions: "Слишком кратко" }).success).toBe(false);
  });
});
