import { describe, expect, it } from "vitest";

import { mockAuthzApi } from "@/app/mocks/authz-api";
import { readDatabase, writeDatabase } from "@/app/mocks/database";

describe("mock authz API", () => {
  it("resolves the current user and persisted access summaries", async () => {
    const session = await mockAuthzApi.resolveSession();

    expect(session.user).toMatchObject({ id: "member-alex", isActive: true });
    expect(session.workspaceAccess).toContainEqual({ workspaceId: "demo", role: "owner" });
    expect(session.projectAccess).toContainEqual({
      workspaceId: "demo",
      projectId: "project-web",
      role: "admin",
    });
  });

  it("guards duplicate, stale, and last-owner workspace mutations", async () => {
    await expect(
      mockAuthzApi.addWorkspaceMembership("demo", { userId: "member-maria", role: "owner" }),
    ).rejects.toMatchObject({ code: "OWNER_TRANSFER_REQUIRED" });
    await expect(
      mockAuthzApi.addWorkspaceMembership("demo", { userId: "member-maria", role: "member" }),
    ).rejects.toMatchObject({ code: "MEMBERSHIP_EXISTS" });

    const members = await mockAuthzApi.listWorkspaceMemberships("demo", {});
    const maria = members.items.find((membership) => membership.userId === "member-maria")!;
    const originalVersion = maria.version;
    const updated = await mockAuthzApi.updateWorkspaceMembership("demo", maria.userId, {
      role: "member",
      expectedVersion: originalVersion,
    });

    await expect(
      mockAuthzApi.updateWorkspaceMembership("demo", maria.userId, {
        role: "admin",
        expectedVersion: originalVersion,
      }),
    ).rejects.toMatchObject({ code: "VERSION_CONFLICT" });
    expect(updated.version).toBe(originalVersion + 1);

    const alex = members.items.find((membership) => membership.userId === "member-alex")!;
    await expect(
      mockAuthzApi.updateWorkspaceMembership("demo", alex.userId, {
        role: "member",
        expectedVersion: alex.version,
      }),
    ).rejects.toMatchObject({ code: "LAST_WORKSPACE_OWNER" });
  });

  it("adds an existing active User while never provisioning from form input", async () => {
    const database = readDatabase();
    database.authzUsers.push({ id: "member-new", email: "new@example.com", name: "Новый участник", isActive: true });
    writeDatabase(database);

    const membership = await mockAuthzApi.addWorkspaceMembership("demo", {
      userId: "member-new",
      role: "member",
    });

    expect(membership).toMatchObject({ userId: "member-new", role: "member", version: 1 });
  });

  it("enforces project admin coverage and service-role narrowing", async () => {
    const page = await mockAuthzApi.listProjectMemberships("project-web", {});
    const alex = page.items.find((membership) => membership.userId === "member-alex")!;
    const maria = page.items.find((membership) => membership.userId === "member-maria")!;
    const restriction = maria.serviceRestrictions[0]!;

    await expect(
      mockAuthzApi.revokeProjectMembership("project-web", alex.userId, alex.version),
    ).rejects.toMatchObject({ code: "LAST_PROJECT_ADMIN" });
    await expect(
      mockAuthzApi.setServiceRestriction("project-web", maria.userId, "ncn-pms", {
        role: "admin",
        expectedVersion: null,
      }),
    ).rejects.toMatchObject({ code: "SERVICE_ROLE_ELEVATION" });

    await mockAuthzApi.removeServiceRestriction(
      "project-web",
      maria.userId,
      restriction.serviceId,
      restriction.version,
    );
    const refreshed = await mockAuthzApi.listProjectMemberships("project-web", {});
    expect(
      refreshed.items.find((membership) => membership.userId === maria.userId)?.serviceRestrictions,
    ).toEqual([]);
  });
});
