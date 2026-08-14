import { inject, type InjectionKey } from "vue";

import type { UUID } from "@/shared/lib/domain-primitives";

import type { CreateProjectInput, Project, ProjectFilters, UpdateProjectInput } from "../model/types";

export interface ProjectApi {
  listProjects(workspaceSlug: string, filters: ProjectFilters, signal?: AbortSignal): Promise<Project[]>;
  getProject(workspaceSlug: string, projectId: UUID, signal?: AbortSignal): Promise<Project>;
  createProject(workspaceSlug: string, input: CreateProjectInput): Promise<Project>;
  updateProject(workspaceSlug: string, projectId: UUID, input: UpdateProjectInput, version: number): Promise<Project>;
  archiveProject(workspaceSlug: string, projectId: UUID, version: number): Promise<Project>;
  restoreProject(workspaceSlug: string, projectId: UUID, version: number): Promise<Project>;
}

export const projectApiKey: InjectionKey<ProjectApi> = Symbol("project-api");

export function useProjectApi(): ProjectApi {
  const api = inject(projectApiKey);
  if (!api) throw new Error("Project API provider is not installed");
  return api;
}
