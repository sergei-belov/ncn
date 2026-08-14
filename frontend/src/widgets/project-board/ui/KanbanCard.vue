<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { CalendarDays, CircleAlert, GripVertical, Layers3, MoveRight } from "@lucide/vue";
import { combine } from "@atlaskit/pragmatic-drag-and-drop/combine";
import { draggable as makeDraggable, dropTargetForElements } from "@atlaskit/pragmatic-drag-and-drop/element/adapter";
import { attachClosestEdge, extractClosestEdge, type Edge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge";

import type { Epic } from "@/entities/epic";
import type { MemberSummary } from "@/entities/member";
import { priorityMeta, type WorkItem } from "@/entities/work-item";
import { formatDate, isOverdue } from "@/shared/lib/date";
import type { UUID } from "@/shared/lib/domain-primitives";
import { AppAvatar, AppBadge, AppButton } from "@/shared/ui";

const props = withDefaults(
  defineProps<{
    workItem: WorkItem;
    members: MemberSummary[];
    epic?: Epic;
    draggable?: boolean;
    showAssignees?: boolean;
    showEpic?: boolean;
    showDueDate?: boolean;
  }>(),
  { epic: undefined, draggable: true, showAssignees: true, showEpic: true, showDueDate: true },
);
const emit = defineEmits<{
  open: [];
  move: [];
  drop: [payload: { workItemId: UUID; fromStateId: UUID; targetWorkItemId: UUID; edge: "top" | "bottom" }];
}>();

const cardRef = ref<HTMLElement>();
const dragHandleRef = ref<HTMLElement>();
const isDragging = ref(false);
const closestEdge = ref<Edge | null>(null);
let cleanup: (() => void) | undefined;

const assignees = computed(() => props.members.filter((member) => props.workItem.assigneeIds.includes(member.id)));
const priority = computed(() => priorityMeta[props.workItem.priority]);

onMounted(() => {
  const element = cardRef.value;
  const dragHandle = dragHandleRef.value;
  if (!element || !dragHandle) return;
  cleanup = combine(
    makeDraggable({
      element,
      dragHandle,
      canDrag: () => props.draggable,
      getInitialData: () => ({ type: "work-item", workItemId: props.workItem.id, stateId: props.workItem.stateId }),
      onDragStart: () => (isDragging.value = true),
      onDrop: () => (isDragging.value = false),
    }),
    dropTargetForElements({
      element,
      canDrop: ({ source }) => source.data.type === "work-item" && props.draggable,
      getData: ({ input, element: target }) =>
        attachClosestEdge(
          { type: "work-item", workItemId: props.workItem.id, stateId: props.workItem.stateId },
          { input, element: target, allowedEdges: ["top", "bottom"] },
        ),
      onDragEnter: ({ self }) => (closestEdge.value = extractClosestEdge(self.data)),
      onDrag: ({ self }) => (closestEdge.value = extractClosestEdge(self.data)),
      onDragLeave: () => (closestEdge.value = null),
      onDrop: ({ source, self }) => {
        closestEdge.value = null;
        const workItemId = source.data.workItemId;
        const fromStateId = source.data.stateId;
        const edge = extractClosestEdge(self.data);
        if (
          typeof workItemId !== "string" ||
          typeof fromStateId !== "string" ||
          workItemId === props.workItem.id ||
          (edge !== "top" && edge !== "bottom")
        ) {
          return;
        }
        emit("drop", { workItemId, fromStateId, targetWorkItemId: props.workItem.id, edge });
      },
    }),
  );
});

onBeforeUnmount(() => cleanup?.());
</script>

<template>
  <div ref="cardRef" class="relative pb-2 last:pb-0" :data-work-item-id="props.workItem.id">
    <div v-if="closestEdge === 'top'" class="absolute -top-px left-1 right-1 z-10 h-0.5 rounded-full bg-primary" />
    <article
      class="surface-shadow group relative rounded-lg border border-border bg-card p-3 transition hover:border-primary/25"
      :class="isDragging ? 'opacity-40' : ''"
    >
      <div class="flex items-start gap-2">
        <button
          ref="dragHandleRef"
          type="button"
          class="focus-ring -ml-1 mt-0.5 flex size-6 shrink-0 items-center justify-center rounded text-muted-foreground opacity-0 transition hover:bg-muted group-hover:opacity-100 group-focus-within:opacity-100"
          :class="props.draggable ? 'cursor-grab' : 'cursor-not-allowed'"
          :aria-label="`Перетащить ${props.workItem.identifier}`"
        >
          <GripVertical class="size-3.5" />
        </button>
        <button type="button" class="focus-ring min-w-0 flex-1 rounded text-left" @click="emit('open')">
          <p class="text-[11px] font-medium text-muted-foreground">{{ props.workItem.identifier }}</p>
          <h3 class="mt-1 text-sm font-medium leading-5 text-card-foreground">{{ props.workItem.title }}</h3>
        </button>
        <AppButton size="icon" variant="ghost" class="-mr-1 size-7 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100" aria-label="Переместить" @click="emit('move')">
          <MoveRight class="size-3.5" />
        </AppButton>
      </div>

      <div class="mt-3 flex flex-wrap items-center gap-1.5 pl-7">
        <AppBadge v-if="props.workItem.priority !== 'none'" variant="outline" :class="priority.className">
          <CircleAlert class="size-3" /> {{ priority.label }}
        </AppBadge>
        <AppBadge v-if="props.showEpic && props.epic" variant="secondary" class="max-w-full">
          <Layers3 class="size-3 shrink-0" /> <span class="truncate">{{ props.epic.name }}</span>
        </AppBadge>
        <AppBadge
          v-if="props.showDueDate && props.workItem.dueDate"
          variant="outline"
          :class="isOverdue(props.workItem.dueDate) ? 'border-destructive/30 text-destructive' : ''"
        >
          <CalendarDays class="size-3" /> {{ formatDate(props.workItem.dueDate) }}
        </AppBadge>
        <div v-if="props.showAssignees && assignees.length" class="ml-auto flex -space-x-1.5">
          <AppAvatar
            v-for="member in assignees.slice(0, 3)"
            :key="member.id"
            size="sm"
            :src="member.avatarUrl"
            :initials="member.initials"
            :title="member.displayName"
            class="ring-2 ring-card"
          />
        </div>
      </div>
    </article>
    <div v-if="closestEdge === 'bottom'" class="absolute bottom-0.5 left-1 right-1 z-10 h-0.5 rounded-full bg-primary" />
  </div>
</template>
