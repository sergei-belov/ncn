<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Bot, Plus } from "@lucide/vue";
import { toast } from "vue-sonner";

import { AgentCard, useAgentsQuery, type Agent, type CreateAgentInput } from "@/entities/agent";
import { useProjectQuery } from "@/entities/project";
import { AgentFormDialog, useAgentMutations } from "@/features/agent-manage";
import { getErrorMessage } from "@/shared/api/api-error";
import { routeNames } from "@/shared/routes";
import { AppButton, AppEmptyState, AppSkeleton } from "@/shared/ui";

const route = useRoute();
const router = useRouter();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const projectQuery = useProjectQuery(workspaceSlug, projectId);
const agentsQuery = useAgentsQuery(workspaceSlug, projectId);
const mutations = useAgentMutations(workspaceSlug, projectId);
const createOpen = ref(false);
const project = computed(() => projectQuery.data.value);
const canManage = computed(() => Boolean(project.value?.permissions.canManageAgents && !project.value.archivedAt));
const agents = computed(() =>
  [...(agentsQuery.data.value ?? [])].sort((left, right) => {
    if (left.kind !== right.kind) return left.kind === "coordinator" ? -1 : 1;
    if (left.status !== right.status) return left.status === "archived" ? 1 : -1;
    return left.name.localeCompare(right.name, "ru");
  }),
);

async function createAgent(input: CreateAgentInput): Promise<void> {
  try {
    const agent = await mutations.create.mutateAsync(input);
    createOpen.value = false;
    toast.success("Ассистент создан");
    await openAgent(agent);
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

async function openAgent(agent: Agent): Promise<void> {
  await router.push({
    name: routeNames.agentSettings,
    params: { workspaceSlug: workspaceSlug.value, projectId: projectId.value, agentId: agent.id },
  });
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="flex min-h-16 items-center justify-between gap-3 border-b border-border bg-card px-4 py-3 sm:px-7">
      <div class="flex items-center gap-3">
        <Bot class="size-4 text-primary" />
        <div>
          <h1 class="text-base font-semibold">Ассистенты</h1>
          <p class="text-xs text-muted-foreground">Координатор и специализированные работники проекта</p>
        </div>
      </div>
      <AppButton v-if="canManage" @click="createOpen = true"><Plus class="size-4" /> Новый ассистент</AppButton>
    </header>

    <main class="p-4 sm:p-7">
      <div v-if="agentsQuery.isPending.value" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <AppSkeleton v-for="index in 6" :key="index" class="h-64 rounded-xl" />
      </div>
      <AppEmptyState v-else-if="agentsQuery.isError.value" title="Не удалось загрузить ассистентов" :description="getErrorMessage(agentsQuery.error.value)">
        <AppButton variant="outline" @click="agentsQuery.refetch()">Повторить</AppButton>
      </AppEmptyState>
      <AppEmptyState v-else-if="agents.length === 0" title="Ассистенты не найдены" description="В каждом проекте должен существовать системный координатор.">
        <template #icon><Bot class="size-5" /></template>
      </AppEmptyState>
      <div v-else class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <AgentCard
          v-for="agent in agents"
          :key="agent.id"
          :agent="agent"
          :can-manage="canManage"
          @open="openAgent(agent)"
        />
      </div>
    </main>
  </div>

  <AgentFormDialog v-model:open="createOpen" :pending="mutations.create.isPending.value" @submit="createAgent" />
</template>
