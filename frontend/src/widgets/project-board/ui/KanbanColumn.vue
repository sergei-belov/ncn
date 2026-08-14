<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { ChevronDown, ChevronRight, MoreHorizontal } from "@lucide/vue";
import { combine } from "@atlaskit/pragmatic-drag-and-drop/combine";
import { dropTargetForElements } from "@atlaskit/pragmatic-drag-and-drop/element/adapter";
import { autoScrollForElements } from "@atlaskit/pragmatic-drag-and-drop-auto-scroll/element";
import { useStorage } from "@vueuse/core";

import { placementForCardEdge, type MoveCommand } from "@/entities/board";
import type { Epic } from "@/entities/epic";
import type { MemberSummary } from "@/entities/member";
import type { WorkItem } from "@/entities/work-item";
import type { WorkflowState } from "@/entities/workflow-state";
import type { UUID } from "@/shared/lib/domain-primitives";
import { AppBadge, AppButton } from "@/shared/ui";

import KanbanCard from "./KanbanCard.vue";
import QuickAddWorkItem from "./QuickAddWorkItem.vue";

const props = withDefaults(
  defineProps<{
    state: WorkflowState;
    workItemIds: UUID[];
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
  open: [workItemId: UUID];
  move: [command: MoveCommand];
  requestMove: [workItemId: UUID];
  quickCreate: [title: string];
}>();

const columnRef = ref<HTMLElement>();
const scrollRef = ref<HTMLElement>();
const isDragOver = ref(false);
const collapsed = useStorage(`board-column-collapsed:${props.state.id}`, false);
let cleanup: (() => void) | undefined;

const cards = computed(() => props.workItemIds.map((id) => props.workItems[id]).filter(Boolean) as WorkItem[]);
const contentId = computed(() => `kanban-column-${props.state.id}`);

function moveAtCard(payload: {
  workItemId: UUID;
  fromStateId: UUID;
  targetWorkItemId: UUID;
  edge: "top" | "bottom";
}): void {
  emit("move", {
    workItemId: payload.workItemId,
    fromStateId: payload.fromStateId,
    toStateId: props.state.id,
    ...placementForCardEdge(payload.targetWorkItemId, payload.edge),
  });
}

onMounted(() => {
  const element = columnRef.value;
  const scrollElement = scrollRef.value;
  if (!element || !scrollElement) return;
  cleanup = combine(
    dropTargetForElements({
      element,
      canDrop: ({ source }) => source.data.type === "work-item" && !props.readOnly,
      getData: () => ({ type: "column", stateId: props.state.id }),
      onDragEnter: () => (isDragOver.value = true),
      onDragStart: () => (isDragOver.value = true),
      onDragLeave: () => (isDragOver.value = false),
      onDrop: ({ source, location }) => {
        isDragOver.value = false;
        const workItemId = source.data.workItemId;
        const fromStateId = source.data.stateId;
        if (typeof workItemId !== "string" || typeof fromStateId !== "string") return;
        const cardTarget = location.current.dropTargets.find((target) => target.data.type === "work-item");
        if (cardTarget) return;
        const targetIds = props.workItemIds.filter((id) => id !== workItemId);
        emit("move", {
          workItemId,
          fromStateId,
          toStateId: props.state.id,
          afterWorkItemId: targetIds.at(-1),
        });
      },
    }),
    autoScrollForElements({ element: scrollElement }),
  );
});

onBeforeUnmount(() => cleanup?.());
</script>

<template>
  <section
    ref="columnRef"
    class="flex h-full max-h-full shrink-0 flex-col overflow-hidden rounded-xl border bg-muted/45 transition-[width,background-color,border-color] duration-200"
    :class="[
      collapsed ? 'w-14' : 'w-[310px]',
      isDragOver ? 'border-primary/50 bg-accent/60' : 'border-border',
    ]"
    :aria-label="`Статус ${props.state.name}`"
    :data-state-id="props.state.id"
    :data-collapsed="collapsed"
  >
    <header class="flex items-center gap-2" :class="collapsed ? 'h-full flex-col px-1.5 py-2' : 'h-12 px-3'">
      <button
        type="button"
        class="focus-ring flex min-w-0 flex-1 rounded text-left"
        :class="collapsed ? 'h-full w-full flex-col items-center gap-2 py-1' : 'items-center gap-2'"
        :aria-expanded="!collapsed"
        :aria-controls="contentId"
        :aria-label="collapsed ? `Развернуть колонку ${props.state.name}` : `Свернуть колонку ${props.state.name}`"
        @click="collapsed = !collapsed"
      >
        <template v-if="collapsed">
          <ChevronRight class="size-4 shrink-0 text-muted-foreground" />
          <span class="size-2.5 shrink-0 rounded-full" :style="{ background: props.state.color }" />
          <span class="min-h-0 flex-1 whitespace-nowrap py-1 text-sm font-semibold [writing-mode:vertical-rl] rotate-180">{{ props.state.name }}</span>
          <AppBadge variant="outline" class="shrink-0 px-1.5">{{ props.workItemIds.length }}</AppBadge>
        </template>
        <template v-else>
          <span class="size-2.5 rounded-full" :style="{ background: props.state.color }" />
          <span class="truncate text-sm font-semibold">{{ props.state.name }}</span>
          <AppBadge variant="outline" class="ml-1">{{ props.workItemIds.length }}</AppBadge>
          <ChevronDown class="ml-auto size-3.5 text-muted-foreground" />
        </template>
      </button>
      <AppButton v-if="!collapsed" size="icon" variant="ghost" class="size-7" aria-label="Действия колонки"><MoreHorizontal class="size-4" /></AppButton>
    </header>

    <div v-show="!collapsed" :id="contentId" class="flex min-h-0 flex-1 flex-col">
      <div ref="scrollRef" class="min-h-16 flex-1 overflow-y-auto px-2 pb-2">
        <KanbanCard
          v-for="workItem in cards"
          :key="workItem.id"
          :work-item="workItem"
          :members="props.members"
          :epic="workItem.epicId ? props.epics[workItem.epicId] : undefined"
          :draggable="!props.readOnly"
          :show-assignees="props.showAssignees"
          :show-epic="props.showEpic"
          :show-due-date="props.showDueDate"
          @open="emit('open', workItem.id)"
          @move="emit('requestMove', workItem.id)"
          @drop="moveAtCard"
        />
        <div v-if="cards.length === 0" class="flex h-20 items-center justify-center rounded-lg border border-dashed border-border text-xs text-muted-foreground">
          Перетащите карточку сюда
        </div>
      </div>
      <div class="border-t border-border p-2">
        <QuickAddWorkItem :disabled="props.readOnly" :pending="props.quickAddPending" @submit="emit('quickCreate', $event)" />
      </div>
    </div>
  </section>
</template>
