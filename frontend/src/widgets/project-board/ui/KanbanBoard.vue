<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { autoScrollForElements } from "@atlaskit/pragmatic-drag-and-drop-auto-scroll/element";

import type { BoardColumn, MoveCommand } from "@/entities/board";
import type { Epic } from "@/entities/epic";
import type { MemberSummary } from "@/entities/member";
import type { WorkItem } from "@/entities/work-item";
import type { WorkflowState } from "@/entities/workflow-state";
import type { UUID } from "@/shared/lib/domain-primitives";

import KanbanColumn from "./KanbanColumn.vue";

const props = withDefaults(
  defineProps<{
    states: WorkflowState[];
    columns: BoardColumn[];
    workItems: Record<UUID, WorkItem>;
    epics: Record<UUID, Epic>;
    members: MemberSummary[];
    readOnly?: boolean;
    quickAddPending?: boolean;
    showAssignees?: boolean;
    showEpic?: boolean;
    showDueDate?: boolean;
  }>(),
  { readOnly: false, quickAddPending: false, showAssignees: true, showEpic: true, showDueDate: true },
);

const emit = defineEmits<{
  openWorkItem: [workItemId: UUID];
  moveWorkItem: [command: MoveCommand];
  requestMove: [workItemId: UUID];
  quickCreate: [stateId: UUID, title: string];
}>();

const boardRef = ref<HTMLElement>();
let cleanup: (() => void) | undefined;

function idsFor(stateId: UUID): UUID[] {
  return props.columns.find((column) => column.stateId === stateId)?.workItemIds ?? [];
}

onMounted(() => {
  if (boardRef.value) cleanup = autoScrollForElements({ element: boardRef.value });
});
onBeforeUnmount(() => cleanup?.());
</script>

<template>
  <div ref="boardRef" class="flex h-full min-h-0 gap-3 overflow-x-auto overflow-y-hidden px-4 pb-4 pt-3 sm:px-6">
    <KanbanColumn
      v-for="state in props.states"
      :key="state.id"
      :state="state"
      :work-item-ids="idsFor(state.id)"
      :work-items="props.workItems"
      :epics="props.epics"
      :members="props.members"
      :read-only="props.readOnly"
      :quick-add-pending="props.quickAddPending"
      :show-assignees="props.showAssignees"
      :show-epic="props.showEpic"
      :show-due-date="props.showDueDate"
      @open="emit('openWorkItem', $event)"
      @move="emit('moveWorkItem', $event)"
      @request-move="emit('requestMove', $event)"
      @quick-create="emit('quickCreate', state.id, $event)"
    />
  </div>
</template>
