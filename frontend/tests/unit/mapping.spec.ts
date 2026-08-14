import { describe, expect, it } from "vitest";

import { mapAgent, wireAgentSchema } from "@/entities/agent";
import { mapProject, wireProjectSchema } from "@/entities/project";

describe("project wire mapping", () => {
  it("maps snake_case transport data without losing permissions or versions", () => {
    const wire = wireProjectSchema.parse({
      id: "project-1",
      workspace_slug: "demo",
      name: "Portal",
      identifier: "WEB",
      description: "Customer portal",
      access: "workspace",
      role: "member",
      color: "#6d5dfc",
      archived_at: null,
      created_at: "2026-08-01T00:00:00.000Z",
      updated_at: "2026-08-10T00:00:00.000Z",
      version: 7,
      permissions: {
        can_view_project: true,
        can_edit_project: false,
        can_archive_project: false,
        can_manage_states: false,
        can_create_work_item: true,
        can_edit_work_item: true,
        can_move_work_item: true,
        can_delete_own_work_item: true,
        can_create_epic: true,
        can_edit_epic: true,
        can_delete_own_epic: true,
      },
    });

    expect(mapProject(wire)).toMatchObject({
      workspaceSlug: "demo",
      archivedAt: null,
      version: 7,
      permissions: { canDeleteWorkItem: true, canDeleteEpic: true },
    });
  });

  it("maps agent configuration from the snake_case wire contract", () => {
    const wire = wireAgentSchema.parse({
      id: "agent-risk",
      project_id: "project-web",
      kind: "worker",
      name: "Risk analyst",
      instructions: "Analyze project risks and return a structured recommendation.",
      model: "qwen3:14b",
      memory_policy: "project",
      max_steps_per_run: 25,
      approval_mode: "always",
      status: "active",
      system_tool_names: ["procurement.read"],
      created_at: "2026-08-01T00:00:00.000Z",
      updated_at: "2026-08-10T00:00:00.000Z",
      version: 3,
    });

    expect(mapAgent(wire)).toMatchObject({
      projectId: "project-web",
      maxStepsPerRun: 25,
      approvalMode: "always",
      systemToolNames: ["procurement.read"],
      version: 3,
    });
  });
});
