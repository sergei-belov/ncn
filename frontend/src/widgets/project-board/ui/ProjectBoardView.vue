<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { FilterX, KanbanSquare, LayoutTemplate, Search, SlidersHorizontal } from "@lucide/vue";
import { useStorage, watchDebounced } from "@vueuse/core";
import { toast } from "vue-sonner";

import { useBoardQuery, type MoveCommand } from "@/entities/board";
import type { Epic } from "@/entities/epic";
import type { Priority, WorkItem } from "@/entities/work-item";
import { useCreateWorkItem } from "@/features/work-item-create";
import { MoveWorkItemDialog, useMoveWorkItem } from "@/features/work-item-move";
import { getErrorMessage } from "@/shared/api/api-error";
import type { UUID } from "@/shared/lib/domain-primitives";
import { routeNames } from "@/shared/routes";
import { AppBadge, AppButton, AppDialog, AppEmptyState, AppInput, AppSelect, AppSkeleton, AppToggle, type SelectOption } from "@/shared/ui";
import KanbanBoard from "./KanbanBoard.vue";

const route = useRoute();
const router = useRouter();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const searchInput = ref(String(route.query.search ?? ""));
const displayOpen = ref(false);
const moveOpen = ref(false);
const moveWorkItemId = ref<UUID>();
const announcement = ref("");

const priority = computed<Priority | null>({
  get: () => (typeof route.query.priority === "string" ? (route.query.priority as Priority) : null),
  set: (value) => void updateQuery({ priority: value ?? undefined }),
});
const epicId = computed<string | null>({
  get: () => (typeof route.query.epic === "string" ? route.query.epic : null),
  set: (value) => void updateQuery({ epic: value ?? undefined }),
});
const assigneeId = computed<string | null>({
  get: () => (typeof route.query.assignee === "string" ? route.query.assignee : null),
  set: (value) => void updateQuery({ assignee: value ?? undefined }),
});
const filters = computed(() => ({
  search: typeof route.query.search === "string" ? route.query.search : undefined,
  priorities: priority.value ? [priority.value] : undefined,
  epicId: epicId.value,
  assigneeId: assigneeId.value,
}));

const query = useBoardQuery(workspaceSlug, projectId, filters);
const payload = computed(() => query.data.value);
const project = computed(() => payload.value?.project);
const states = computed(() => payload.value?.states ?? []);
const members = computed(() => payload.value?.members ?? []);
const epics = computed(() => payload.value?.epics ?? []);
const columns = computed(() => payload.value?.columns ?? []);
const workItems = computed<Record<UUID, WorkItem>>(() => Object.fromEntries((payload.value?.workItems ?? []).map((item) => [item.id, item])));
const epicMap = computed<Record<UUID, Epic>>(() => Object.fromEntries(epics.value.map((epic) => [epic.id, epic])));
const createMutation = useCreateWorkItem(workspaceSlug, projectId);
const moveMutation = useMoveWorkItem(workspaceSlug, projectId);

const showAssignees = useStorage("board-display-assignees", true);
const showEpic = useStorage("board-display-epic", true);
const showDueDate = useStorage("board-display-due-date", true);

const priorityOptions: SelectOption[] = [
  { value: "urgent", label: "Срочный" },
  { value: "high", label: "Высокий" },
  { value: "medium", label: "Средний" },
  { value: "low", label: "Низкий" },
  { value: "none", label: "Без приоритета" },
];
const epicOptions = computed<SelectOption[]>(() => epics.value.map((epic) => ({ value: epic.id, label: epic.name })));
const memberOptions = computed<SelectOption[]>(() => members.value.map((member) => ({ value: member.id, label: member.displayName })));
const hasFilters = computed(() => Boolean(filters.value.search || priority.value || epicId.value || assigneeId.value));
const readOnly = computed(() => Boolean(project.value?.archivedAt || !project.value?.permissions.canMoveWorkItem));
const selectedMoveItem = computed(() => payload.value?.workItems.find((item) => item.id === moveWorkItemId.value));

watch(
  () => route.query.search,
  (value) => {
    const next = typeof value === "string" ? value : "";
    if (next !== searchInput.value) searchInput.value = next;
  },
);
watchDebounced(searchInput, (value) => void updateQuery({ search: value.trim() || undefined }), { debounce: 300, maxWait: 700 });

function updateQuery(patch: Record<string, string | undefined>): Promise<void> {
  return router.replace({ query: { ...route.query, ...patch } });
}

function clearFilters(): void {
  searchInput.value = "";
  void router.replace({ query: {} });
}

async function quickCreate(stateId: UUID, title: string): Promise<void> {
  try {
    const workItem = await createMutation.mutateAsync({ title, stateId });
    toast.success(`${workItem.identifier} создана`);
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

async function moveWorkItem(command: MoveCommand): Promise<void> {
  const targetState = states.value.find((state) => state.id === command.toStateId);
  try {
    await moveMutation.mutateAsync(command);
    announcement.value = `Карточка перемещена в «${targetState?.name ?? "колонку"}»`;
    if (moveOpen.value) moveOpen.value = false;
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

function requestMove(workItemId: UUID): void {
  moveWorkItemId.value = workItemId;
  moveOpen.value = true;
}

function openWorkItem(workItemId: UUID): void {
  void router.push({
    name: routeNames.workItem,
    params: { workspaceSlug: workspaceSlug.value, projectId: projectId.value, workItemId },
    state: { backgroundRoute: route.fullPath, backgroundName: "board" },
  });
}
</script>

<template>
  <div class="flex h-screen min-h-[640px] flex-col overflow-hidden">
    <header class="flex min-h-16 items-center justify-between gap-4 border-b border-border bg-card px-4 sm:px-6">
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <KanbanSquare class="size-4 text-primary" />
          <h1 class="truncate text-base font-semibold">Доска</h1>
          <AppBadge v-if="project?.archivedAt" variant="outline">Только чтение</AppBadge>
        </div>
        <p class="mt-0.5 truncate text-xs text-muted-foreground">{{ project?.name ?? "Загрузка проекта…" }}</p>
      </div>
      <div class="flex items-center gap-2">
        <AppButton variant="outline" size="sm" @click="displayOpen = true"><SlidersHorizontal class="size-3.5" /> Вид</AppButton>
      </div>
    </header>

    <div class="flex flex-wrap items-center gap-2 border-b border-border bg-card/80 px-4 py-2.5 sm:px-6">
      <div class="relative min-w-52 flex-1 sm:max-w-sm">
        <Search class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <AppInput v-model="searchInput" class="pl-9" placeholder="Поиск карточек" aria-label="Поиск карточек" />
      </div>
      <AppSelect v-model="priority" :options="priorityOptions" placeholder="Приоритет" class="w-36" />
      <AppSelect v-model="epicId" :options="epicOptions" placeholder="Эпик" class="w-40" />
      <AppSelect v-model="assigneeId" :options="memberOptions" placeholder="Исполнитель" class="hidden w-40 xl:block" />
      <AppButton v-if="hasFilters" variant="ghost" size="sm" @click="clearFilters"><FilterX class="size-3.5" /> Сбросить</AppButton>
    </div>

    <div v-if="readOnly" class="border-b border-amber-200 bg-amber-50 px-5 py-2 text-xs text-amber-800 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-200">
      Проект доступен только для чтения. Перемещение и создание карточек отключены.
    </div>

    <div v-if="query.isPending.value" class="flex min-h-0 flex-1 gap-3 overflow-hidden p-4 sm:p-6">
      <AppSkeleton v-for="index in 4" :key="index" class="h-full w-[310px] shrink-0 rounded-xl" />
    </div>
    <div v-else-if="query.isError.value" class="flex-1 p-6">
      <AppEmptyState title="Не удалось загрузить доску" :description="getErrorMessage(query.error.value)">
        <AppButton variant="outline" @click="query.refetch()">Повторить</AppButton>
      </AppEmptyState>
    </div>
    <KanbanBoard
      v-else
      class="min-h-0 flex-1"
      :states="states"
      :columns="columns"
      :work-items="workItems"
      :epics="epicMap"
      :members="members"
      :read-only="readOnly"
      :quick-add-pending="createMutation.isPending.value"
      :show-assignees="showAssignees"
      :show-epic="showEpic"
      :show-due-date="showDueDate"
      @open-work-item="openWorkItem"
      @move-work-item="moveWorkItem"
      @request-move="requestMove"
      @quick-create="quickCreate"
    />
    <p class="sr-only" aria-live="polite">{{ announcement }}</p>
  </div>

  <AppDialog v-model:open="displayOpen" title="Отображение карточек" description="Настройки сохраняются в этом браузере." width="sm">
    <div class="space-y-4">
      <AppToggle v-model="showAssignees" label="Исполнители" description="Показывать аватары внизу карточки." />
      <AppToggle v-model="showEpic" label="Эпик" description="Показывать название связанного эпика." />
      <AppToggle v-model="showDueDate" label="Срок" description="Показывать дату завершения и просрочку." />
      <div class="flex justify-end pt-2"><AppButton @click="displayOpen = false"><LayoutTemplate class="size-4" /> Готово</AppButton></div>
    </div>
  </AppDialog>

  <MoveWorkItemDialog
    v-model:open="moveOpen"
    :work-item="selectedMoveItem"
    :states="states"
    :columns="columns"
    :pending="moveMutation.isPending.value"
    @submit="moveWorkItem"
  />
</template>
