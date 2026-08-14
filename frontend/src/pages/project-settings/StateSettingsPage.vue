<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import { ArrowDown, ArrowUp, Check, Columns3, Pencil, Plus, Star, Trash2 } from "@lucide/vue";
import { toast } from "vue-sonner";

import { useProjectQuery } from "@/entities/project";
import { useStatesQuery, type StateGroup, type WorkflowState } from "@/entities/workflow-state";
import { useStateMutations } from "@/features/state-manage";
import { getErrorMessage } from "@/shared/api/api-error";
import type { UUID } from "@/shared/lib/domain-primitives";
import { AppBadge, AppButton, AppDialog, AppFormField, AppInput, AppSelect, AppSkeleton, type SelectOption } from "@/shared/ui";
import { SettingsTabs } from "@/widgets/project-navigation";

const route = useRoute();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const query = useStatesQuery(workspaceSlug, projectId);
const projectQuery = useProjectQuery(workspaceSlug, projectId);
const states = computed(() => query.data.value ?? []);
const project = computed(() => projectQuery.data.value);
const mutations = useStateMutations(workspaceSlug, projectId);
const createOpen = ref(false);
const editedState = ref<WorkflowState>();
const deleteOpen = ref(false);
const deleteStateValue = ref<WorkflowState>();
const replacementStateId = ref<UUID | null>(null);
const name = ref("");
const color = ref("#60a5fa");
const group = ref<StateGroup>("unstarted");

const groupOptions: SelectOption[] = [
  { value: "backlog", label: "Бэклог" },
  { value: "unstarted", label: "Не начато" },
  { value: "started", label: "В работе" },
  { value: "completed", label: "Завершено" },
  { value: "cancelled", label: "Отменено" },
];
const replacementOptions = computed<SelectOption[]>(() =>
  states.value.filter((state) => state.id !== deleteStateValue.value?.id).map((state) => ({ value: state.id, label: state.name })),
);

function openCreate(): void {
  editedState.value = undefined;
  name.value = "";
  color.value = "#60a5fa";
  group.value = "unstarted";
  createOpen.value = true;
}

function openEdit(state: WorkflowState): void {
  editedState.value = state;
  name.value = state.name;
  color.value = state.color;
  group.value = state.group;
  createOpen.value = true;
}

async function saveState(): Promise<void> {
  if (!name.value.trim()) return;
  try {
    const input = { name: name.value.trim(), color: color.value, group: group.value };
    if (editedState.value) await mutations.update.mutateAsync({ state: editedState.value, input });
    else await mutations.create.mutateAsync(input);
    createOpen.value = false;
    toast.success(editedState.value ? "Состояние обновлено" : "Состояние создано");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

async function setDefault(state: WorkflowState): Promise<void> {
  try {
    await mutations.update.mutateAsync({ state, input: { isDefault: true } });
    toast.success(`«${state.name}» назначено состоянием по умолчанию`);
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

async function move(state: WorkflowState, direction: -1 | 1): Promise<void> {
  const ids = states.value.map((item) => item.id);
  const index = ids.indexOf(state.id);
  const nextIndex = index + direction;
  if (nextIndex < 0 || nextIndex >= ids.length) return;
  [ids[index], ids[nextIndex]] = [ids[nextIndex]!, ids[index]!];
  try {
    await mutations.reorder.mutateAsync(ids);
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

function requestDelete(state: WorkflowState): void {
  deleteStateValue.value = state;
  replacementStateId.value = states.value.find((candidate) => candidate.id !== state.id)?.id ?? null;
  deleteOpen.value = true;
}

async function removeState(): Promise<void> {
  if (!deleteStateValue.value || !replacementStateId.value) return;
  try {
    await mutations.remove.mutateAsync({ stateId: deleteStateValue.value.id, replacementStateId: replacementStateId.value });
    deleteOpen.value = false;
    toast.success("Состояние удалено, карточки перенесены");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="flex h-16 items-center justify-between gap-3 border-b border-border bg-card px-4 sm:px-7">
      <div class="flex items-center gap-3"><Columns3 class="size-4 text-primary" /><div><h1 class="text-base font-semibold">Состояния</h1><p class="text-xs text-muted-foreground">Колонки Kanban</p></div></div>
      <AppButton v-if="project?.permissions.canManageStates && !project.archivedAt" @click="openCreate"><Plus class="size-4" /> Добавить</AppButton>
    </header>
    <SettingsTabs />

    <div class="mx-auto max-w-3xl p-4 sm:p-7">
      <div class="mb-5"><h2 class="font-semibold">Workflow проекта</h2><p class="mt-1 text-sm text-muted-foreground">Порядок состояний определяет порядок колонок. При удалении выберите колонку для переноса карточек.</p></div>
      <div v-if="query.isPending.value" class="space-y-2"><AppSkeleton v-for="index in 4" :key="index" class="h-16 rounded-lg" /></div>
      <div v-else class="overflow-hidden rounded-xl border border-border bg-card">
        <div v-for="(state, index) in states" :key="state.id" class="flex items-center gap-3 border-b border-border px-4 py-3 last:border-b-0">
          <span class="size-3 shrink-0 rounded-full" :style="{ background: state.color }" />
          <div class="min-w-0 flex-1"><p class="truncate text-sm font-medium">{{ state.name }}</p><p class="mt-0.5 text-xs text-muted-foreground">{{ groupOptions.find((item) => item.value === state.group)?.label }}</p></div>
          <AppBadge v-if="state.isDefault" variant="secondary"><Star class="size-3" /> По умолчанию</AppBadge>
          <div v-if="project?.permissions.canManageStates && !project.archivedAt" class="flex items-center gap-1">
            <AppButton size="icon" variant="ghost" class="size-8" aria-label="Редактировать состояние" @click="openEdit(state)"><Pencil class="size-4" /></AppButton>
            <AppButton v-if="!state.isDefault" size="icon" variant="ghost" class="size-8" aria-label="Сделать состоянием по умолчанию" @click="setDefault(state)"><Check class="size-4" /></AppButton>
            <AppButton size="icon" variant="ghost" class="size-8" :disabled="index === 0" aria-label="Переместить вверх" @click="move(state, -1)"><ArrowUp class="size-4" /></AppButton>
            <AppButton size="icon" variant="ghost" class="size-8" :disabled="index === states.length - 1" aria-label="Переместить вниз" @click="move(state, 1)"><ArrowDown class="size-4" /></AppButton>
            <AppButton size="icon" variant="ghost" class="size-8 text-destructive hover:bg-destructive/10" :disabled="state.isDefault || states.length <= 1" aria-label="Удалить состояние" @click="requestDelete(state)"><Trash2 class="size-4" /></AppButton>
          </div>
        </div>
      </div>
    </div>
  </div>

  <AppDialog
    v-model:open="createOpen"
    :title="editedState ? 'Редактировать состояние' : 'Новое состояние'"
    :description="editedState ? 'Изменения применятся ко всем представлениям доски.' : 'Состояние будет добавлено в конец Kanban.'"
    width="sm"
  >
    <div class="space-y-4">
      <AppFormField label="Название" required><AppInput v-model="name" placeholder="Например, На проверке" /></AppFormField>
      <div class="grid grid-cols-[120px_1fr] gap-3">
        <AppFormField label="Цвет"><input v-model="color" type="color" class="h-9 w-full rounded-md border border-input bg-card p-1" /></AppFormField>
        <AppFormField label="Группа"><AppSelect v-model="group" :options="groupOptions" /></AppFormField>
      </div>
      <div class="flex justify-end gap-2"><AppButton variant="outline" @click="createOpen = false">Отмена</AppButton><AppButton :loading="mutations.create.isPending.value || mutations.update.isPending.value" :disabled="!name.trim()" @click="saveState">{{ editedState ? "Сохранить" : "Создать" }}</AppButton></div>
    </div>
  </AppDialog>

  <AppDialog v-model:open="deleteOpen" title="Удалить состояние?" description="Все карточки будут транзакционно перемещены." width="sm">
    <AppFormField label="Перенести карточки в"><AppSelect v-model="replacementStateId" :options="replacementOptions" /></AppFormField>
    <div class="mt-5 flex justify-end gap-2"><AppButton variant="outline" @click="deleteOpen = false">Отмена</AppButton><AppButton variant="destructive" :loading="mutations.remove.isPending.value" :disabled="!replacementStateId" @click="removeState"><Trash2 class="size-4" /> Удалить</AppButton></div>
  </AppDialog>
</template>
