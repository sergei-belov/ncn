<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, FileWarning } from "@lucide/vue";

import { useBoardQuery } from "@/entities/board";
import { routeNames } from "@/shared/routes";
import { AppButton, AppEmptyState, AppSheet, AppSkeleton } from "@/shared/ui";
import { ProjectBoardView } from "@/widgets/project-board";
import { WorkItemDetail } from "@/widgets/work-item-sheet";

const route = useRoute();
const router = useRouter();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const workItemId = computed(() => String(route.params.workItemId));
const historyState = window.history.state as { backgroundRoute?: string; backgroundName?: string };
const navigationEntry = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
const isDesktop = window.matchMedia("(min-width: 768px)").matches;
const isSheet = ref(Boolean(historyState.backgroundRoute && historyState.backgroundName === "board" && isDesktop && navigationEntry?.type !== "reload"));
const sheetOpen = ref(true);
const query = useBoardQuery(workspaceSlug, projectId, {});
const board = computed(() => query.data.value);
const workItem = computed(() => board.value?.workItems.find((item) => item.id === workItemId.value));
const project = computed(() => board.value?.project);
const readOnly = computed(() => Boolean(project.value?.archivedAt || !project.value?.permissions.canEditWorkItem));

watch(sheetOpen, (open) => {
  if (!open) close();
});

function close(): void {
  if (isSheet.value && historyState.backgroundRoute) void router.replace(historyState.backgroundRoute);
  else void router.push({ name: routeNames.board, params: { workspaceSlug: workspaceSlug.value, projectId: projectId.value } });
}
</script>

<template>
  <template v-if="isSheet">
    <ProjectBoardView />
    <AppSheet v-model:open="sheetOpen" :title="workItem?.title ?? 'Карточка'" :description="workItem?.identifier ?? ''">
      <AppSkeleton v-if="query.isPending.value" class="m-6 h-[560px]" />
      <WorkItemDetail
        v-else-if="workItem"
        :workspace-slug="workspaceSlug"
        :project-id="projectId"
        :work-item="workItem"
        :states="board?.states ?? []"
        :epics="board?.epics ?? []"
        :members="board?.members ?? []"
        :read-only="readOnly"
        @deleted="close"
      />
      <AppEmptyState v-else title="Карточка не найдена" description="Возможно, она была удалена."><FileWarning class="size-5" /></AppEmptyState>
    </AppSheet>
  </template>

  <div v-else class="min-h-screen bg-background">
    <header class="flex h-16 items-center gap-3 border-b border-border bg-card px-4 sm:px-7">
      <AppButton variant="ghost" size="icon" aria-label="Назад к доске" @click="close"><ArrowLeft class="size-4" /></AppButton>
      <div>
        <h1 class="text-sm font-semibold">{{ workItem?.identifier ?? "Карточка" }}</h1>
        <p class="text-xs text-muted-foreground">{{ project?.name }}</p>
      </div>
    </header>
    <AppSkeleton v-if="query.isPending.value" class="m-7 h-[560px]" />
    <WorkItemDetail
      v-else-if="workItem"
      class="mx-auto min-h-[calc(100vh-4rem)] max-w-6xl bg-card"
      :workspace-slug="workspaceSlug"
      :project-id="projectId"
      :work-item="workItem"
      :states="board?.states ?? []"
      :epics="board?.epics ?? []"
      :members="board?.members ?? []"
      :read-only="readOnly"
      @deleted="close"
    />
    <div v-else class="p-7">
      <AppEmptyState title="Карточка не найдена" description="Возможно, она была удалена или у вас нет доступа.">
        <template #icon><FileWarning class="size-5" /></template>
        <AppButton variant="outline" @click="close">Вернуться к доске</AppButton>
      </AppEmptyState>
    </div>
  </div>
</template>
