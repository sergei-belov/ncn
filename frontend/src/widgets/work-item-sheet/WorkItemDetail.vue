<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { CalendarDays, Check, CircleAlert, Layers3, Save, Trash2, UserRound } from "@lucide/vue";
import { toast } from "vue-sonner";

import type { Epic } from "@/entities/epic";
import type { MemberSummary } from "@/entities/member";
import { priorityMeta, type Priority, type WorkItem } from "@/entities/work-item";
import type { WorkflowState } from "@/entities/workflow-state";
import { useDeleteWorkItem, useUpdateWorkItem } from "@/features/work-item-create";
import { getErrorMessage } from "@/shared/api/api-error";
import type { UUID } from "@/shared/lib/domain-primitives";
import {
  AppAvatar,
  AppBadge,
  AppButton,
  AppDialog,
  AppFormField,
  AppInput,
  AppSelect,
  RichTextEditor,
  type SelectOption,
} from "@/shared/ui";

const props = defineProps<{
  workspaceSlug: string;
  projectId: UUID;
  workItem: WorkItem;
  states: WorkflowState[];
  epics: Epic[];
  members: MemberSummary[];
  readOnly?: boolean;
}>();
const emit = defineEmits<{ deleted: []; saved: [workItem: WorkItem] }>();

const title = ref(props.workItem.title);
const descriptionHtml = ref(props.workItem.descriptionHtml);
const deleteOpen = ref(false);
const saveState = ref<"idle" | "saving" | "saved" | "error">("idle");
const updateMutation = useUpdateWorkItem(() => props.workspaceSlug, () => props.projectId);
const deleteMutation = useDeleteWorkItem(() => props.workspaceSlug, () => props.projectId);

const current = computed(() => props.workItem);
const stateOptions = computed<SelectOption[]>(() => props.states.map((state) => ({ value: state.id, label: state.name })));
const epicOptions = computed<SelectOption[]>(() => props.epics.map((epic) => ({ value: epic.id, label: epic.name })));
const priorityOptions = Object.entries(priorityMeta).map(([value, meta]) => ({ value, label: meta.label }));

watch(
  () => current.value,
  (value) => {
    title.value = value.title;
    descriptionHtml.value = value.descriptionHtml;
  },
  { deep: true },
);

async function patch(input: Parameters<typeof updateMutation.mutateAsync>[0]["input"]): Promise<void> {
  if (props.readOnly) return;
  saveState.value = "saving";
  try {
    const saved = await updateMutation.mutateAsync({ workItem: current.value, input });
    saveState.value = "saved";
    emit("saved", saved);
    window.setTimeout(() => {
      if (saveState.value === "saved") saveState.value = "idle";
    }, 1600);
  } catch (error) {
    saveState.value = "error";
    toast.error(getErrorMessage(error));
  }
}

function saveTitle(): void {
  const value = title.value.trim();
  if (value && value !== current.value.title) void patch({ title: value });
}

function toggleAssignee(memberId: UUID): void {
  const next = current.value.assigneeIds.includes(memberId)
    ? current.value.assigneeIds.filter((id) => id !== memberId)
    : [...current.value.assigneeIds, memberId];
  void patch({ assigneeIds: next });
}

async function remove(): Promise<void> {
  try {
    await deleteMutation.mutateAsync(current.value);
    deleteOpen.value = false;
    toast.success(`${current.value.identifier} удалена`);
    emit("deleted");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}
</script>

<template>
  <div class="grid min-h-full lg:grid-cols-[minmax(0,1fr)_280px]">
    <main class="min-w-0 p-5 sm:p-7">
      <div class="mb-5 flex items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <AppBadge variant="outline">{{ current.identifier }}</AppBadge>
          <span v-if="saveState === 'saving'" class="text-xs text-muted-foreground">Сохранение…</span>
          <span v-else-if="saveState === 'saved'" class="flex items-center gap-1 text-xs text-emerald-600"><Check class="size-3" /> Сохранено</span>
          <span v-else-if="saveState === 'error'" class="text-xs text-destructive">Не сохранено</span>
        </div>
        <AppButton v-if="!props.readOnly" variant="ghost" size="sm" class="text-destructive hover:bg-destructive/10" @click="deleteOpen = true">
          <Trash2 class="size-3.5" /> Удалить
        </AppButton>
      </div>

      <AppInput
        v-model="title"
        class="h-auto border-transparent px-1 py-2 text-xl font-semibold shadow-none hover:border-input focus:border-input"
        :disabled="props.readOnly"
        aria-label="Название карточки"
        @blur="saveTitle"
        @keydown.enter.prevent="($event.target as HTMLInputElement).blur()"
      />

      <section class="mt-7">
        <div class="mb-2 flex items-center justify-between">
          <h2 class="text-sm font-semibold">Описание</h2>
          <AppButton
            v-if="!props.readOnly"
            size="sm"
            variant="outline"
            :loading="updateMutation.isPending.value"
            :disabled="descriptionHtml === current.descriptionHtml"
            @click="patch({ descriptionHtml })"
          >
            <Save class="size-3.5" /> Сохранить
          </AppButton>
        </div>
        <RichTextEditor v-model="descriptionHtml" :disabled="props.readOnly" />
      </section>
    </main>

    <aside class="border-t border-border bg-muted/25 p-5 lg:border-l lg:border-t-0">
      <h2 class="mb-5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Свойства</h2>
      <div class="space-y-5">
        <AppFormField label="Состояние">
          <AppSelect
            :model-value="current.stateId"
            :options="stateOptions"
            :disabled="props.readOnly"
            @update:model-value="$event && patch({ stateId: $event })"
          />
        </AppFormField>
        <AppFormField label="Приоритет">
          <AppSelect
            :model-value="current.priority"
            :options="priorityOptions"
            :disabled="props.readOnly"
            @update:model-value="$event && patch({ priority: $event as Priority })"
          />
        </AppFormField>
        <AppFormField label="Эпик">
          <AppSelect
            :model-value="current.epicId"
            :options="epicOptions"
            placeholder="Без эпика"
            :disabled="props.readOnly"
            @update:model-value="patch({ epicId: $event })"
          />
        </AppFormField>

        <div>
          <div class="mb-2 flex items-center gap-2 text-sm font-medium"><UserRound class="size-4 text-muted-foreground" /> Исполнители</div>
          <div class="space-y-1">
            <button
              v-for="member in props.members"
              :key="member.id"
              type="button"
              class="focus-ring flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm hover:bg-muted"
              :disabled="props.readOnly"
              @click="toggleAssignee(member.id)"
            >
              <AppAvatar size="sm" :src="member.avatarUrl" :initials="member.initials" :title="member.displayName" />
              <span class="min-w-0 flex-1 truncate">{{ member.displayName }}</span>
              <Check v-if="current.assigneeIds.includes(member.id)" class="size-3.5 text-primary" />
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <AppFormField label="Начало">
            <AppInput
              :model-value="current.startDate ?? ''"
              type="date"
              :disabled="props.readOnly"
              @update:model-value="patch({ startDate: $event || null })"
            />
          </AppFormField>
          <AppFormField label="Срок">
            <AppInput
              :model-value="current.dueDate ?? ''"
              type="date"
              :disabled="props.readOnly"
              @update:model-value="patch({ dueDate: $event || null })"
            />
          </AppFormField>
        </div>

        <div class="rounded-lg border border-border bg-card p-3 text-xs leading-5 text-muted-foreground">
          <p class="flex items-center gap-1.5"><CircleAlert class="size-3.5" /> Версия {{ current.version }}</p>
          <p class="mt-1 flex items-center gap-1.5"><CalendarDays class="size-3.5" /> Даты хранятся без времени</p>
          <p v-if="current.epicId" class="mt-1 flex items-center gap-1.5"><Layers3 class="size-3.5" /> Связана с эпиком</p>
        </div>
      </div>
    </aside>
  </div>

  <AppDialog v-model:open="deleteOpen" title="Удалить карточку?" description="Действие нельзя отменить." width="sm">
    <p class="text-sm text-muted-foreground">Будет удалена карточка {{ current.identifier }} «{{ current.title }}».</p>
    <div class="mt-5 flex justify-end gap-2">
      <AppButton variant="outline" @click="deleteOpen = false">Отмена</AppButton>
      <AppButton variant="destructive" :loading="deleteMutation.isPending.value" @click="remove"><Trash2 class="size-4" /> Удалить</AppButton>
    </div>
  </AppDialog>
</template>
