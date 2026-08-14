import { z } from "zod";

import type { Project, ProjectPermissions, ProjectRole } from "../model/types";

export const permissionsSchema = z.object({
  can_view_project: z.boolean(),
  can_edit_project: z.boolean(),
  can_archive_project: z.boolean(),
  can_manage_states: z.boolean(),
  can_manage_agents: z.boolean().optional(),
  can_create_work_item: z.boolean(),
  can_edit_work_item: z.boolean(),
  can_move_work_item: z.boolean(),
  can_delete_own_work_item: z.boolean().optional(),
  can_delete_any_work_item: z.boolean().optional(),
  can_create_epic: z.boolean(),
  can_edit_epic: z.boolean(),
  can_delete_own_epic: z.boolean().optional(),
  can_delete_any_epic: z.boolean().optional(),
});

export const wireProjectSchema = z.object({
  id: z.string(),
  workspace_slug: z.string(),
  name: z.string(),
  identifier: z.string(),
  description: z.string().default(""),
  access: z.enum(["private", "workspace"]),
  role: z.enum(["admin", "member", "viewer"]),
  color: z.string().default("#6d5dfc"),
  archived_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
  version: z.number(),
  permissions: permissionsSchema,
});

export function mapPermissions(value: z.infer<typeof permissionsSchema>, role?: ProjectRole): ProjectPermissions {
  return {
    canViewProject: value.can_view_project,
    canEditProject: value.can_edit_project,
    canArchiveProject: value.can_archive_project,
    canManageStates: value.can_manage_states,
    canManageAgents: value.can_manage_agents ?? role === "admin",
    canCreateWorkItem: value.can_create_work_item,
    canEditWorkItem: value.can_edit_work_item,
    canMoveWorkItem: value.can_move_work_item,
    canDeleteWorkItem: Boolean(value.can_delete_any_work_item || value.can_delete_own_work_item),
    canCreateEpic: value.can_create_epic,
    canEditEpic: value.can_edit_epic,
    canDeleteEpic: Boolean(value.can_delete_any_epic || value.can_delete_own_epic),
  };
}

export function mapProject(value: z.infer<typeof wireProjectSchema>): Project {
  return {
    id: value.id,
    workspaceSlug: value.workspace_slug,
    name: value.name,
    identifier: value.identifier,
    description: value.description,
    access: value.access,
    role: value.role,
    color: value.color,
    archivedAt: value.archived_at,
    createdAt: value.created_at,
    updatedAt: value.updated_at,
    version: value.version,
    permissions: mapPermissions(value.permissions, value.role),
  };
}
