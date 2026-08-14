import type { RouteRecordRaw } from "vue-router";

import { env } from "@/shared/config/env";
import { routeNames } from "@/shared/routes";

export const routes: RouteRecordRaw[] = [
  { path: "/", redirect: `/${env.VITE_WORKSPACE_SLUG}/projects` },
  {
    path: "/:workspaceSlug",
    component: () => import("@/widgets/app-shell/WorkspaceShell.vue"),
    children: [
      {
        path: "projects",
        name: routeNames.projects,
        component: () => import("@/pages/projects/ProjectsPage.vue"),
      },
      {
        path: "projects/:projectId",
        component: () => import("@/widgets/project-navigation/ProjectLayout.vue"),
        children: [
          { path: "", redirect: { name: routeNames.board } },
          {
            path: "board",
            name: routeNames.board,
            component: () => import("@/pages/board/BoardPage.vue"),
          },
          {
            path: "work-items/:workItemId",
            name: routeNames.workItem,
            component: () => import("@/pages/work-item/WorkItemPage.vue"),
          },
          {
            path: "epics",
            name: routeNames.epics,
            component: () => import("@/pages/epics/EpicsPage.vue"),
          },
          {
            path: "epics/:epicId",
            name: routeNames.epic,
            component: () => import("@/pages/epic/EpicPage.vue"),
          },
          {
            path: "agents",
            name: routeNames.agents,
            component: () => import("@/pages/agents/AgentsPage.vue"),
          },
          {
            path: "agents/:agentId/settings",
            name: routeNames.agentSettings,
            component: () => import("@/pages/agent-settings/AgentSettingsPage.vue"),
          },
          {
            path: "sessions",
            name: routeNames.sessions,
            component: () => import("@/pages/sessions/SessionsPage.vue"),
          },
          {
            path: "settings",
            name: routeNames.projectSettings,
            component: () => import("@/pages/project-settings/ProjectSettingsPage.vue"),
          },
          {
            path: "settings/states",
            name: routeNames.stateSettings,
            component: () => import("@/pages/project-settings/StateSettingsPage.vue"),
          },
        ],
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    component: () => import("@/pages/not-found/NotFoundPage.vue"),
  },
];
