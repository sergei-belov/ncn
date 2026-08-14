<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { ShieldCheck } from "@lucide/vue";

import { useProjectQuery } from "@/entities/project";
import { AppEmptyState, AppSkeleton } from "@/shared/ui";
import { AccessManagementView } from "@/widgets/access-management";
import { SettingsTabs } from "@/widgets/project-navigation";

const route = useRoute();
const workspaceId = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const projectQuery = useProjectQuery(workspaceId, projectId);
const project = computed(() => projectQuery.data.value);
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="flex h-16 items-center gap-3 border-b border-border bg-card px-4 sm:px-7">
      <ShieldCheck class="size-4 text-primary" />
      <div>
        <h1 class="text-base font-semibold">Доступ к проекту</h1>
        <p class="text-xs text-muted-foreground">{{ project?.name ?? "Проект" }}</p>
      </div>
    </header>
    <SettingsTabs />

    <div v-if="projectQuery.isPending.value" class="mx-auto max-w-6xl space-y-3 p-4 sm:p-7">
      <AppSkeleton class="h-24 rounded-xl" />
      <AppSkeleton v-for="index in 4" :key="index" class="h-20 rounded-xl" />
    </div>
    <AppEmptyState
      v-else-if="projectQuery.isError.value || !project"
      class="m-4 sm:m-7"
      title="Проект недоступен"
      description="Проект не найден или у вас больше нет доступа к его настройкам."
    />
    <AccessManagementView
      v-else
      scope="project"
      :workspace-id="workspaceId"
      :project-id="projectId"
      :scope-name="`проект ${project.name}`"
      :read-only="Boolean(project.archivedAt)"
    />
  </div>
</template>

