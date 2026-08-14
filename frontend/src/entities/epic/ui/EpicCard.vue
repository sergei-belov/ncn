<script setup lang="ts">
import { ArrowUpRight, CalendarDays, Layers3 } from "@lucide/vue";

import { formatDate } from "@/shared/lib/date";
import type { Epic } from "../model/types";
import { AppBadge, AppProgress } from "@/shared/ui";

const props = defineProps<{ epic: Epic }>();
const emit = defineEmits<{ open: [] }>();
</script>

<template>
  <button
    type="button"
    class="surface-shadow focus-ring group flex w-full flex-col rounded-xl border border-border bg-card p-5 text-left transition hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-lg"
    @click="emit('open')"
  >
    <div class="flex w-full items-start justify-between gap-4">
      <span class="flex size-10 items-center justify-center rounded-xl text-white" :style="{ background: props.epic.color }"><Layers3 class="size-4" /></span>
      <ArrowUpRight class="size-4 text-muted-foreground transition group-hover:text-primary" />
    </div>
    <h2 class="mt-4 text-base font-semibold">{{ props.epic.name }}</h2>
    <p class="mt-1 line-clamp-2 min-h-10 text-sm leading-5 text-muted-foreground">{{ props.epic.description || "Описание не добавлено." }}</p>
    <div class="mt-5 w-full">
      <div class="mb-2 flex items-center justify-between text-xs">
        <span class="text-muted-foreground">{{ props.epic.progress.completed }} из {{ props.epic.progress.total }} готово</span>
        <span class="font-semibold">{{ props.epic.progress.percentage }}%</span>
      </div>
      <AppProgress :value="props.epic.progress.percentage" :label="`Прогресс эпика ${props.epic.name}`" />
    </div>
    <div class="mt-4 flex flex-wrap gap-2">
      <AppBadge variant="outline">{{ props.epic.progress.total }} карточек</AppBadge>
      <AppBadge v-if="props.epic.targetDate" variant="secondary"><CalendarDays class="size-3" /> {{ formatDate(props.epic.targetDate) }}</AppBadge>
    </div>
  </button>
</template>
