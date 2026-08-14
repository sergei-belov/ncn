<script setup lang="ts">
import { computed } from "vue";
import { Archive, ArrowUpRight, Globe2, LockKeyhole, RotateCcw } from "@lucide/vue";

import type { Project } from "../model/types";
import { AppBadge, AppButton } from "@/shared/ui";

const props = defineProps<{ project: Project; pending?: boolean }>();
const emit = defineEmits<{ archive: [project: Project, restore: boolean]; open: [project: Project] }>();

const roleLabel = computed(() => ({ admin: "Администратор", member: "Участник", viewer: "Наблюдатель" })[props.project.role]);

</script>

<template>
  <article
    class="surface-shadow group flex min-h-56 flex-col rounded-xl border border-border bg-card p-5 transition hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-lg"
  >
    <button type="button" class="focus-ring flex flex-1 flex-col text-left" @click="emit('open', props.project)">
      <div class="flex items-start justify-between gap-4">
        <span class="flex size-11 items-center justify-center rounded-xl text-sm font-bold text-white" :style="{ background: props.project.color }">
          {{ props.project.identifier.slice(0, 2) }}
        </span>
        <ArrowUpRight class="size-4 text-muted-foreground transition group-hover:text-primary" />
      </div>
      <h2 class="mt-4 text-base font-semibold">{{ props.project.name }}</h2>
      <p class="mt-1 line-clamp-2 text-sm leading-6 text-muted-foreground">
        {{ props.project.description || "Описание проекта пока не добавлено." }}
      </p>
      <div class="mt-auto flex flex-wrap items-center gap-2 pt-4">
        <AppBadge variant="outline">{{ props.project.identifier }}</AppBadge>
        <AppBadge>
          <Globe2 v-if="props.project.access === 'workspace'" class="size-3" />
          <LockKeyhole v-else class="size-3" />
          {{ props.project.access === "workspace" ? "Workspace" : "Приватный" }}
        </AppBadge>
        <AppBadge v-if="props.project.archivedAt" variant="outline">Архив</AppBadge>
      </div>
    </button>
    <div class="mt-4 flex items-center justify-between border-t border-border pt-3">
      <span class="text-xs text-muted-foreground">{{ roleLabel }}</span>
      <AppButton
        v-if="props.project.permissions.canArchiveProject"
        size="sm"
        variant="ghost"
        :loading="props.pending"
        @click="emit('archive', props.project, Boolean(props.project.archivedAt))"
      >
        <RotateCcw v-if="props.project.archivedAt" class="size-3.5" />
        <Archive v-else class="size-3.5" />
        {{ props.project.archivedAt ? "Восстановить" : "В архив" }}
      </AppButton>
    </div>
  </article>
</template>
