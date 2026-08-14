<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { ArrowLeft, Bot, LockKeyhole } from "@lucide/vue";

import { useAgentQuery } from "@/entities/agent";
import { useProjectQuery } from "@/entities/project";
import { AgentSettingsPanel } from "@/features/agent-manage";
import { getErrorMessage } from "@/shared/api/api-error";
import { routeNames } from "@/shared/routes";
import { AppEmptyState, AppSkeleton } from "@/shared/ui";

const route = useRoute();
const router = useRouter();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const agentId = computed(() => String(route.params.agentId));
const projectQuery = useProjectQuery(workspaceSlug, projectId);
const agentQuery = useAgentQuery(workspaceSlug, projectId, agentId);
const project = computed(() => projectQuery.data.value);
const agent = computed(() => agentQuery.data.value);
const readOnly = computed(() => !project.value?.permissions.canManageAgents || Boolean(project.value?.archivedAt));

async function backToAgents(): Promise<void> {
  await router.push({ name: routeNames.agents, params: { workspaceSlug: workspaceSlug.value, projectId: projectId.value } });
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="flex min-h-16 items-center gap-3 border-b border-border bg-card px-4 py-3 sm:px-7">
      <RouterLink
        :to="{ name: routeNames.agents, params: { workspaceSlug, projectId } }"
        class="focus-ring flex size-8 shrink-0 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
        aria-label="Назад к ассистентам"
      >
        <ArrowLeft class="size-4" />
      </RouterLink>
      <Bot class="size-4 text-primary" />
      <div class="min-w-0">
        <h1 class="truncate text-base font-semibold">{{ agent?.name ?? "Настройки ассистента" }}</h1>
        <p class="text-xs text-muted-foreground">{{ readOnly ? "Только просмотр" : "Конфигурация агента проекта" }}</p>
      </div>
      <LockKeyhole v-if="readOnly" class="ml-auto size-4 text-muted-foreground" aria-label="Редактирование недоступно" />
    </header>

    <main class="mx-auto max-w-4xl p-4 sm:p-7">
      <div v-if="agentQuery.isPending.value" class="space-y-5">
        <AppSkeleton class="h-[520px] rounded-xl" />
        <AppSkeleton class="h-32 rounded-xl" />
      </div>
      <AppEmptyState
        v-else-if="agentQuery.isError.value || !agent"
        title="Ассистент не найден"
        :description="agentQuery.isError.value ? getErrorMessage(agentQuery.error.value) : 'Возможно, ассистент был удалён или у вас нет доступа.'"
      />
      <AgentSettingsPanel
        v-else
        :workspace-slug="workspaceSlug"
        :project-id="projectId"
        :agent="agent"
        :read-only="readOnly"
        @archived="backToAgents"
      />
    </main>
  </div>
</template>
