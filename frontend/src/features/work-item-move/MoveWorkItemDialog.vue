<script setup lang="ts">
import { computed, ref, watch } from "vue";

import type { BoardColumn, MoveCommand } from "@/entities/board";
import type { WorkItem } from "@/entities/work-item";
import type { WorkflowState } from "@/entities/workflow-state";
import type { UUID } from "@/shared/lib/domain-primitives";
import { AppButton, AppDialog, AppFormField, AppSelect, type SelectOption } from "@/shared/ui";

const open = defineModel<boolean>("open", { default: false });
const props = defineProps<{
  workItem?: WorkItem;
  states: WorkflowState[];
  columns: BoardColumn[];
  pending?: boolean;
}>();
const emit = defineEmits<{ submit: [command: MoveCommand] }>();

const targetStateId = ref<UUID | null>(null);
const placement = ref<"start" | "end">("end");
const stateOptions = computed<SelectOption[]>(() => props.states.map((state) => ({ value: state.id, label: state.name })));

watch(open, (value) => {
  if (value) {
    targetStateId.value = props.workItem?.stateId ?? props.states[0]?.id ?? null;
    placement.value = "end";
  }
});

function submit(): void {
  if (!props.workItem || !targetStateId.value) return;
  const targetIds = (props.columns.find((column) => column.stateId === targetStateId.value)?.workItemIds ?? []).filter(
    (id) => id !== props.workItem?.id,
  );
  const command: MoveCommand = {
    workItemId: props.workItem.id,
    fromStateId: props.workItem.stateId,
    toStateId: targetStateId.value,
    beforeWorkItemId: placement.value === "start" ? targetIds[0] : undefined,
    afterWorkItemId: placement.value === "end" ? targetIds.at(-1) : undefined,
  };
  emit("submit", command);
}
</script>

<template>
  <AppDialog v-model:open="open" title="Переместить карточку" :description="props.workItem?.identifier ?? ''" width="sm">
    <div class="space-y-4">
      <AppFormField label="Колонка">
        <AppSelect v-model="targetStateId" :options="stateOptions" />
      </AppFormField>
      <AppFormField label="Позиция">
        <select v-model="placement" class="focus-ring h-9 w-full rounded-md border border-input bg-card px-3 text-sm">
          <option value="start">В начало колонки</option>
          <option value="end">В конец колонки</option>
        </select>
      </AppFormField>
      <div class="flex justify-end gap-2">
        <AppButton variant="outline" @click="open = false">Отмена</AppButton>
        <AppButton :loading="props.pending" :disabled="!targetStateId" @click="submit">Переместить</AppButton>
      </div>
    </div>
  </AppDialog>
</template>
