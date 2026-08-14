<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { ArrowLeft, Bot, KanbanSquare, ListTree, MessageSquareText, Settings } from "@lucide/vue";

import { useProjectQuery } from "@/entities/project";
import { routeNames } from "@/shared/routes";
import { AppBadge, AppSkeleton } from "@/shared/ui";

const route = useRoute();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const projectQuery = useProjectQuery(workspaceSlug, projectId);
const project = computed(() => projectQuery.data.value);

const sections = computed(() => [
  {
    label: "Агент",
    links: [
      { name: routeNames.agents, label: "Ассистенты", icon: Bot },
      { name: routeNames.sessions, label: "Сессии", icon: MessageSquareText },
    ],
  },
  {
    label: "Управление",
    links: [
      { name: routeNames.board, label: "Доска", icon: KanbanSquare },
      { name: routeNames.epics, label: "Эпики", icon: ListTree },
      ...(project.value?.permissions.canEditProject ? [{ name: routeNames.projectSettings, label: "Настройки", icon: Settings }] : []),
    ],
  },
]);
</script>

<template>
  <div class="flex min-h-screen min-w-0">
    <aside class="sticky top-0 hidden h-screen w-52 shrink-0 flex-col border-r border-border bg-card/70 lg:flex">
      <div class="border-b border-border p-3">
        <RouterLink
          :to="{ name: routeNames.projects, params: { workspaceSlug } }"
          class="focus-ring mb-3 flex items-center gap-2 rounded-md px-2 py-1.5 text-xs text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          <ArrowLeft class="size-3.5" /> Все проекты
        </RouterLink>
        <div v-if="project" class="flex items-center gap-2.5 px-2">
          <span class="flex size-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold text-white" :style="{ background: project.color }">
            {{ project.identifier.slice(0, 2) }}
          </span>
          <div class="min-w-0">
            <p class="truncate text-sm font-semibold">{{ project.name }}</p>
            <AppBadge v-if="project.archivedAt" variant="outline" class="mt-1">Архив</AppBadge>
            <p v-else class="text-[11px] text-muted-foreground">{{ project.identifier }}</p>
          </div>
        </div>
        <AppSkeleton v-else-if="projectQuery.isPending.value" class="h-9" />
      </div>

      <nav class="space-y-4 p-2" aria-label="Разделы проекта">
        <section v-for="section in sections" :key="section.label">
          <h2 class="px-3 pb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{{ section.label }}</h2>
          <div class="space-y-1">
            <RouterLink
              v-for="link in section.links"
              :key="link.name"
              :to="{ name: link.name, params: { workspaceSlug, projectId } }"
              class="focus-ring flex h-9 items-center gap-3 rounded-md px-3 text-sm text-muted-foreground hover:bg-muted hover:text-foreground"
              active-class="bg-accent !text-accent-foreground font-medium"
            >
              <component :is="link.icon" class="size-4" />
              {{ link.label }}
            </RouterLink>
          </div>
        </section>
      </nav>
    </aside>

    <section class="min-w-0 flex-1">
      <header class="sticky top-0 z-30 border-b border-border bg-background/95 px-3 py-2 backdrop-blur lg:hidden">
        <div class="flex min-w-0 items-center gap-2">
          <RouterLink
            :to="{ name: routeNames.projects, params: { workspaceSlug } }"
            class="focus-ring flex size-9 shrink-0 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
            aria-label="Вернуться ко всем проектам"
          >
            <ArrowLeft class="size-4" />
          </RouterLink>
          <span
            v-if="project"
            class="flex size-8 shrink-0 items-center justify-center rounded-lg text-[11px] font-bold text-white"
            :style="{ background: project.color }"
          >
            {{ project.identifier.slice(0, 2) }}
          </span>
          <p class="min-w-0 flex-1 truncate text-sm font-semibold">{{ project?.name ?? "Проект" }}</p>
        </div>

        <nav class="mt-2 space-y-1.5" aria-label="Разделы проекта">
          <section v-for="section in sections" :key="section.label" class="grid grid-cols-[72px_1fr] items-center gap-1">
            <h2 class="truncate px-1 text-[9px] font-semibold uppercase tracking-wide text-muted-foreground">{{ section.label }}</h2>
            <div class="grid grid-flow-col auto-cols-fr gap-1">
              <RouterLink
                v-for="link in section.links"
                :key="link.name"
                :to="{ name: link.name, params: { workspaceSlug, projectId } }"
                class="focus-ring flex h-8 min-w-0 items-center justify-center gap-1.5 rounded-md px-2 text-xs text-muted-foreground hover:bg-muted hover:text-foreground"
                active-class="bg-accent !text-accent-foreground font-medium"
              >
                <component :is="link.icon" class="size-3.5 shrink-0" />
                <span class="truncate">{{ link.label }}</span>
              </RouterLink>
            </div>
          </section>
        </nav>
      </header>

      <div v-if="projectQuery.isError.value" class="p-8 text-sm text-destructive">Не удалось загрузить проект.</div>
      <RouterView v-else />
    </section>
  </div>
</template>
