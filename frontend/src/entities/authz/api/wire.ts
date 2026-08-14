import { z } from "zod";

import type {
  AuthzSession,
  AuthzUser,
  CursorPage,
  ProjectMembership,
  ServiceRestriction,
  WorkspaceMembership,
} from "../model/types";

export const wireAuthzUserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string().nullable().optional(),
  is_active: z.boolean(),
});

export const wireWorkspaceAccessSchema = z.object({
  workspace_id: z.string(),
  role: z.enum(["owner", "admin", "member"]),
});

export const wireProjectAccessSchema = z.object({
  workspace_id: z.string(),
  project_id: z.string(),
  role: z.enum(["admin", "member", "viewer"]),
});

export const wireAuthzSessionSchema = z.object({
  user: wireAuthzUserSchema,
  workspace_access: z.array(wireWorkspaceAccessSchema).default([]),
  project_access: z.array(wireProjectAccessSchema).default([]),
  policy_version: z.string(),
});

export const wireServiceRestrictionSchema = z.object({
  id: z.string(),
  project_user_id: z.string(),
  service_id: z.string(),
  role: z.enum(["admin", "member", "viewer"]),
  version: z.number().int().positive(),
});

export const wireWorkspaceMembershipSchema = z.object({
  id: z.string(),
  workspace_id: z.string(),
  user_id: z.string(),
  user: wireAuthzUserSchema.optional(),
  role: z.enum(["owner", "admin", "member"]),
  version: z.number().int().positive(),
});

export const wireProjectMembershipSchema = z.object({
  id: z.string(),
  workspace_id: z.string(),
  project_id: z.string(),
  user_id: z.string(),
  user: wireAuthzUserSchema.optional(),
  role: z.enum(["admin", "member", "viewer"]),
  source: z.enum(["manual", "bootstrap"]),
  version: z.number().int().positive(),
  service_restrictions: z.array(wireServiceRestrictionSchema).default([]),
});

const wireWorkspaceMembershipItemSchema = wireWorkspaceMembershipSchema.extend({
  user: wireAuthzUserSchema,
});

const wireProjectMembershipItemSchema = wireProjectMembershipSchema.extend({
  user: wireAuthzUserSchema,
});

export const wireWorkspaceMembershipPageSchema = z.object({
  items: z.array(wireWorkspaceMembershipItemSchema),
  next_cursor: z.string().nullable(),
});

export const wireProjectMembershipPageSchema = z.object({
  items: z.array(wireProjectMembershipItemSchema),
  next_cursor: z.string().nullable(),
});

export const wireServiceRestrictionResultSchema = wireServiceRestrictionSchema.extend({
  effective_role: z.enum(["admin", "member", "viewer"]),
});

export function mapAuthzUser(value: z.infer<typeof wireAuthzUserSchema>): AuthzUser {
  return {
    id: value.id,
    email: value.email,
    name: value.name?.trim() || value.email,
    isActive: value.is_active,
  };
}

export function mapAuthzSession(value: z.infer<typeof wireAuthzSessionSchema>): AuthzSession {
  return {
    user: mapAuthzUser(value.user),
    workspaceAccess: value.workspace_access.map((access) => ({ workspaceId: access.workspace_id, role: access.role })),
    projectAccess: value.project_access.map((access) => ({
      workspaceId: access.workspace_id,
      projectId: access.project_id,
      role: access.role,
    })),
    policyVersion: value.policy_version,
  };
}

export function mapServiceRestriction(value: z.infer<typeof wireServiceRestrictionSchema>): ServiceRestriction {
  return {
    id: value.id,
    projectUserId: value.project_user_id,
    serviceId: value.service_id,
    role: value.role,
    version: value.version,
  };
}

export function mapWorkspaceMembership(value: z.infer<typeof wireWorkspaceMembershipSchema>): WorkspaceMembership {
  const user = value.user
    ? mapAuthzUser(value.user)
    : { id: value.user_id, email: "", name: `Пользователь ${value.user_id}`, isActive: true };
  return {
    id: value.id,
    workspaceId: value.workspace_id,
    userId: value.user_id,
    user,
    role: value.role,
    version: value.version,
  };
}

export function mapProjectMembership(value: z.infer<typeof wireProjectMembershipSchema>): ProjectMembership {
  const user = value.user
    ? mapAuthzUser(value.user)
    : { id: value.user_id, email: "", name: `Пользователь ${value.user_id}`, isActive: true };
  return {
    id: value.id,
    workspaceId: value.workspace_id,
    projectId: value.project_id,
    userId: value.user_id,
    user,
    role: value.role,
    source: value.source,
    version: value.version,
    serviceRestrictions: value.service_restrictions.map(mapServiceRestriction),
  };
}

export function mapWorkspaceMembershipPage(
  value: z.infer<typeof wireWorkspaceMembershipPageSchema>,
): CursorPage<WorkspaceMembership> {
  return { items: value.items.map(mapWorkspaceMembership), nextCursor: value.next_cursor };
}

export function mapProjectMembershipPage(
  value: z.infer<typeof wireProjectMembershipPageSchema>,
): CursorPage<ProjectMembership> {
  return { items: value.items.map(mapProjectMembership), nextCursor: value.next_cursor };
}
