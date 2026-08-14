<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { CalendarDays, Pencil, Plus, Trash2 } from "@lucide/vue";
import { toast } from "vue-sonner";

import type { Epic } from "@/entities/epic";
import type { WorkItem } from "@/entities/work-item";
import type { WorkflowState } from "@/entities/workflow-state";
import { EpicFormDialog, useEpicMutations, type EpicFormValues } from "@/features/epic-create";
import { AddWorkItemsToEpicDialog } from "@/features/epic-work-items-manage";
import { getErrorMessage } from "@/shared/api/api-error";
import { formatDate } from "@/shared/lib/date";
import type { UUID } from "@/shared/lib/domain-primitives";
import { routeNames } from "@/shared/routes";
import { AppBadge, AppButton, AppDialog, AppProgress } from "@/shared/ui";

const props = defineProps<{
  workspaceSlug: string;
  projectId: UUID;
  epic: Epic;
  epics: Epic[];
  workItems: WorkItem[];
  states: WorkflowState[];
  readOnly?: boolean;
}>();
const emit = defineEmits<{ deleted: [] }>();
const router = useRouter();
const editOpen = ref(false);
const manageOpen = ref(false);
const deleteOpen = ref(false);
const mutations = useEpicMutations(() => props.workspaceSlug, () => props.projectId);
const current = computed(() => props.epic);
const stateMap = computed(() => Object.fromEntries(props.states.map((state) => [state.id, state])));
const epicMap = computed(() => Object.fromEntries(props.epics.map((epic) => [epic.id, epic])));
const linkedItems = computed(() => props.workItems.filter((item) => current.value.workItemIds.includes(item.id)));

async function update(values: EpicFormValues): Promise<void> {
  try {
    await mutations.update.mutateAsync({ epic: current.value, input: values });
    editOpen.value = false;
    toast.success("Эпик обновлён");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

async function setWorkItems(ids: UUID[]): Promise<void> {
  try {
    await mutations.setWorkItems.mutateAsync({ epicId: current.value.id, workItemIds: ids });
    manageOpen.value = false;
    toast.success("Состав эпика обновлён");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

async function remove(): Promise<void> {
  try {
    await mutations.remove.mutateAsync(current.value);
    deleteOpen.value = false;
    toast.success("Эпик удалён, карточки отвязаны");
    emit("deleted");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

function openWorkItem(workItemId: UUID): void {
  void router.push({
    name: routeNames.workItem,
    params: { workspaceSlug: props.workspaceSlug, projectId: props.projectId, workItemId },
  });
}
</script>

<template>
  <div class="p-5 sm:p-7">
    <div class="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
      <div class="min-w-0">
        <div class="flex items-center gap-2">
          <span class="size-3 rounded-full" :style="{ background: current.color }" />
          <AppBadge variant="outline">Эпик</AppBadge>
        </div>
        <h1 class="mt-3 text-2xl font-semibold tracking-tight">{{ current.name }}</h1>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{{ current.description || "Описание эпика пока не добавлено." }}</p>
      </div>
      <div v-if="!props.readOnly" class="flex shrink-0 gap-2">
        <AppButton variant="outline" size="sm" @click="editOpen = true"><Pencil class="size-3.5" /> Изменить</AppButton>
        <AppButton variant="ghost" size="icon" class="text-destructive hover:bg-destructive/10" aria-label="Удалить эпик" @click="deleteOpen = true">
          <Trash2 class="size-4" />
        </AppButton>
      </div>
    </div>

    <section class="mt-7 rounded-xl border border-border bg-muted/35 p-4">
      <div class="flex items-end justify-between gap-4">
        <div>
          <p class="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">Прогресс</p>
          <p class="mt-1 text-2xl font-semibold">{{ current.progress.percentage }}%</p>
        </div>
        <p class="text-sm text-muted-foreground">{{ current.progress.completed }} из {{ current.progress.total }} готово</p>
      </div>
      <AppProgress class="mt-3" :value="current.progress.percentage" :label="`Прогресс эпика ${current.name}`" />
      <div class="mt-4 flex flex-wrap gap-2 text-xs text-muted-foreground">
        <AppBadge v-if="current.startDate" variant="outline"><CalendarDays class="size-3" /> {{ formatDate(current.startDate) }}</AppBadge>
        <span v-if="current.startDate && current.targetDate">→</span>
        <AppBadge v-if="current.targetDate" variant="outline"><CalendarDays class="size-3" /> {{ formatDate(current.targetDate) }}</AppBadge>
      </div>
    </section>

    <section class="mt-7">
      <div class="mb-3 flex items-center justify-between">
        <div>
          <h2 class="text-sm font-semibold">Карточки</h2>
          <p class="mt-0.5 text-xs text-muted-foreground">Прогресс рассчитывается backend по завершённым состояниям.</p>
        </div>
        <AppButton v-if="!props.readOnly" variant="outline" size="sm" @click="manageOpen = true"><Plus class="size-3.5" /> Управлять</AppButton>
      </div>
      <div class="overflow-hidden rounded-xl border border-border bg-card">
        <button
          v-for="workItem in linkedItems"
          :key="workItem.id"
          type="button"
          class="focus-ring flex w-full items-center gap-3 border-b border-border px-4 py-3 text-left last:border-b-0 hover:bg-muted/60"
          @click="openWorkItem(workItem.id)"
        >
          <span class="w-16 shrink-0 text-xs font-medium text-muted-foreground">{{ workItem.identifier }}</span>
          <span class="min-w-0 flex-1 truncate text-sm">{{ workItem.title }}</span>
          <span class="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span class="size-2 rounded-full" :style="{ background: stateMap[workItem.stateId]?.color }" />
            {{ stateMap[workItem.stateId]?.name }}
          </span>
        </button>
        <p v-if="linkedItems.length === 0" class="p-8 text-center text-sm text-muted-foreground">В эпике пока нет карточек.</p>
      </div>
    </section>
  </div>

  <EpicFormDialog v-model:open="editOpen" :epic="current" :pending="mutations.update.isPending.value" @submit="update" />
  <AddWorkItemsToEpicDialog
    v-model:open="manageOpen"
    :epic="current"
    :work-items="props.workItems"
    :epic-map="epicMap"
    :pending="mutations.setWorkItems.isPending.value"
    @submit="setWorkItems"
  />
  <AppDialog v-model:open="deleteOpen" title="Удалить эпик?" description="Карточки сохранятся, но связь с эпиком будет удалена." width="sm">
    <p class="text-sm text-muted-foreground">Удалить «{{ current.name }}»?</p>
    <div class="mt-5 flex justify-end gap-2">
      <AppButton variant="outline" @click="deleteOpen = false">Отмена</AppButton>
      <AppButton variant="destructive" :loading="mutations.remove.isPending.value" @click="remove"><Trash2 class="size-4" /> Удалить</AppButton>
    </div>
  </AppDialog>
</template>
