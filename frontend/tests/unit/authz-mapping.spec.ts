import { describe, expect, it } from "vitest";

import {
  mapAuthzSession,
  mapProjectMembership,
  mapServiceRestriction,
  mapWorkspaceMembership,
  wireAuthzSessionSchema,
  wireProjectMembershipSchema,
  wireServiceRestrictionResultSchema,
  wireWorkspaceMembershipSchema,
} from "@/entities/authz";

describe("authz wire mapping", () => {
  it("maps the protected session without deriving access from identity fields", () => {
    const session = mapAuthzSession(
      wireAuthzSessionSchema.parse({
        user: { id: "user-1", email: "user@example.com", name: "User", is_active: true },
        workspace_access: [{ workspace_id: "demo", role: "owner" }],
        project_access: [{ workspace_id: "demo", project_id: "project-1", role: "admin" }],
        policy_version: "v1",
        ignored_oidc_role: "superuser",
      }),
    );

    expect(session).toEqual({
      user: { id: "user-1", email: "user@example.com", name: "User", isActive: true },
      workspaceAccess: [{ workspaceId: "demo", role: "owner" }],
      projectAccess: [{ workspaceId: "demo", projectId: "project-1", role: "admin" }],
      policyVersion: "v1",
    });
  });

  it("maps project provenance, versions, and service restrictions", () => {
    const membership = mapProjectMembership(
      wireProjectMembershipSchema.parse({
        id: "project-user-1",
        workspace_id: "demo",
        project_id: "project-1",
        user_id: "user-1",
        user: { id: "user-1", email: "user@example.com", name: null, is_active: true },
        role: "member",
        source: "bootstrap",
        version: 4,
        service_restrictions: [
          {
            id: "service-user-1",
            project_user_id: "project-user-1",
            service_id: "ncn-agents",
            role: "viewer",
            version: 2,
          },
        ],
      }),
    );

    expect(membership).toMatchObject({
      source: "bootstrap",
      version: 4,
      user: { name: "user@example.com" },
      serviceRestrictions: [{ serviceId: "ncn-agents", role: "viewer", version: 2 }],
    });
  });

  it("accepts canonical mutation records that omit list-only user enrichment", () => {
    const workspaceMembership = mapWorkspaceMembership(
      wireWorkspaceMembershipSchema.parse({
        id: "workspace-user-1",
        workspace_id: "demo",
        user_id: "user-1",
        role: "member",
        version: 2,
      }),
    );
    const serviceRestriction = mapServiceRestriction(
      wireServiceRestrictionResultSchema.parse({
        id: "service-user-1",
        project_user_id: "project-user-1",
        service_id: "ncn-agents",
        role: "viewer",
        version: 1,
        effective_role: "viewer",
      }),
    );

    expect(workspaceMembership.user).toMatchObject({ id: "user-1", name: "Пользователь user-1" });
    expect(serviceRestriction).toMatchObject({ serviceId: "ncn-agents", role: "viewer" });
  });
});
