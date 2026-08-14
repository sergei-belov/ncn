import type { Plugin } from "vue";

import { agentApiKey, httpAgentApi } from "@/entities/agent";
import { boardApiKey, httpBoardApi } from "@/entities/board";
import { epicApiKey, httpEpicApi } from "@/entities/epic";
import { httpProjectApi, projectApiKey } from "@/entities/project";
import { httpWorkItemApi, workItemApiKey } from "@/entities/work-item";
import { httpWorkflowStateApi, workflowStateApiKey } from "@/entities/workflow-state";
import { env } from "@/shared/config/env";
import { runtimeControlsKey } from "@/shared/config/runtime-controls";

import { resetDatabase } from "../mocks/database";
import { mockProjectManagementApi } from "../mocks/project-management-api";

export const projectManagementApiPlugin: Plugin = {
  install(app) {
    const mock = env.VITE_API_MODE === "mock";
    app.provide(agentApiKey, mock ? mockProjectManagementApi : httpAgentApi);
    app.provide(projectApiKey, mock ? mockProjectManagementApi : httpProjectApi);
    app.provide(boardApiKey, mock ? mockProjectManagementApi : httpBoardApi);
    app.provide(workItemApiKey, mock ? mockProjectManagementApi : httpWorkItemApi);
    app.provide(epicApiKey, mock ? mockProjectManagementApi : httpEpicApi);
    app.provide(workflowStateApiKey, mock ? mockProjectManagementApi : httpWorkflowStateApi);
    app.provide(runtimeControlsKey, { resetDemoData: resetDatabase });
  },
};
