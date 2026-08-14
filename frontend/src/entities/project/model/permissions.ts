import type { ProjectPermissions, ProjectRole } from "./types";

export function permissionsForRole(role: ProjectRole): ProjectPermissions {
  const canWrite = role !== "viewer";
  const isAdmin = role === "admin";

  return {
    canViewProject: true,
    canEditProject: isAdmin,
    canArchiveProject: isAdmin,
    canManageStates: isAdmin,
    canManageAgents: isAdmin,
    canCreateWorkItem: canWrite,
    canEditWorkItem: canWrite,
    canMoveWorkItem: canWrite,
    canDeleteWorkItem: canWrite,
    canCreateEpic: canWrite,
    canEditEpic: canWrite,
    canDeleteEpic: canWrite,
  };
}
