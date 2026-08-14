<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, Layers3 } from "@lucide/vue";

import { useBoardQuery } from "@/entities/board";
import { useEpicsQuery } from "@/entities/epic";
import { routeNames } from "@/shared/routes";
import { AppButton, AppEmptyState, AppSheet, AppSkeleton } from "@/shared/ui";
import { EpicList } from "@/widgets/epic-list";
import { EpicDetail } from "@/widgets/epic-sheet";

const route = useRoute();
const router = useRouter();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const epicId = computed(() => String(route.params.epicId));
const historyState = window.history.state as { backgroundRoute?: string; backgroundName?: string };
const navigationEntry = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
const isSheet = ref(
  Boolean(
    historyState.backgroundRoute &&
      historyState.backgroundName === "epics" &&
      window.matchMedia("(min-width: 768px)").matches &&
      navigationEntry?.type !== "reload",
  ),
);
const sheetOpen = ref(true);
const query = useEpicsQuery(workspaceSlug, projectId, {});
const boardQuery = useBoardQuery(workspaceSlug, projectId, {});
const epics = computed(() => query.data.value ?? []);
const board = computed(() => boardQuery.data.value);
const epic = computed(() => epics.value.find((item) => item.id === epicId.value));
const project = computed(() => board.value?.project);
const readOnly = computed(() => Boolean(project.value?.archivedAt || !project.value?.permissions.canEditEpic));

watch(sheetOpen, (open) => {
  if (!open) close();
});

function close(): void {
  if (isSheet.value && historyState.backgroundRoute) void router.replace(historyState.backgroundRoute);
  else void router.push({ name: routeNames.epics, params: { workspaceSlug: workspaceSlug.value, projectId: projectId.value } });
}
</script>

<template>
  <template v-if="isSheet">
    <EpicList />
    <AppSheet v-model:open="sheetOpen" :title="epic?.name ?? 'Эпик'" description="Прогресс и связанные карточки">
      <AppSkeleton v-if="query.isPending.value" class="m-6 h-[560px]" />
      <EpicDetail
        v-else-if="epic"
        :workspace-slug="workspaceSlug"
        :project-id="projectId"
        :epic="epic"
        :epics="epics"
        :work-items="board?.workItems ?? []"
        :states="board?.states ?? []"
        :read-only="readOnly"
        @deleted="close"
      />
      <AppEmptyState v-else title="Эпик не найден" description="Возможно, он был удалён." />
    </AppSheet>
  </template>

  <div v-else class="min-h-screen bg-background">
    <header class="flex h-16 items-center gap-3 border-b border-border bg-card px-4 sm:px-7">
      <AppButton variant="ghost" size="icon" aria-label="Назад к эпикам" @click="close"><ArrowLeft class="size-4" /></AppButton>
      <div><h1 class="text-sm font-semibold">Эпик</h1><p class="text-xs text-muted-foreground">{{ project?.name }}</p></div>
    </header>
    <AppSkeleton v-if="query.isPending.value" class="m-7 h-[560px]" />
    <EpicDetail
      v-else-if="epic"
      class="mx-auto max-w-5xl bg-card"
      :workspace-slug="workspaceSlug"
      :project-id="projectId"
      :epic="epic"
      :epics="epics"
      :work-items="board?.workItems ?? []"
      :states="board?.states ?? []"
      :read-only="readOnly"
      @deleted="close"
    />
    <div v-else class="p-7">
      <AppEmptyState title="Эпик не найден" description="Возможно, он был удалён или у вас нет доступа.">
        <template #icon><Layers3 class="size-5" /></template>
        <AppButton variant="outline" @click="close">Вернуться к эпикам</AppButton>
      </AppEmptyState>
    </div>
  </div>
</template>
