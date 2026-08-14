<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Archive, FolderKanban, Plus, Search } from "@lucide/vue";
import { toast } from "vue-sonner";

import { ProjectCard, useProjectsQuery, type Project } from "@/entities/project";
import { ProjectFormDialog, useArchiveProject, useCreateProject, type ProjectFormValues } from "@/features/project-create";
import { getErrorMessage } from "@/shared/api/api-error";
import { routeNames } from "@/shared/routes";
import { AppButton, AppEmptyState, AppInput, AppSkeleton, AppToggle } from "@/shared/ui";

const route = useRoute();
const router = useRouter();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const search = ref("");
const showArchived = ref(false);
const createOpen = ref(false);
const formRef = ref<{ applyApiError: (error: unknown) => void }>();
const filters = computed(() => ({ search: search.value || undefined, archived: showArchived.value }));
const query = useProjectsQuery(workspaceSlug, filters);
const projects = computed(() => query.data.value ?? []);
const createMutation = useCreateProject(workspaceSlug);
const archiveMutation = useArchiveProject(workspaceSlug);

async function createProject(values: ProjectFormValues): Promise<void> {
  try {
    const project = await createMutation.mutateAsync(values);
    createOpen.value = false;
    toast.success("Проект создан");
    await router.push({ name: routeNames.board, params: { workspaceSlug: workspaceSlug.value, projectId: project.id } });
  } catch (error) {
    formRef.value?.applyApiError(error);
  }
}

async function archiveProject(project: Parameters<typeof archiveMutation.mutateAsync>[0]["project"], restore: boolean): Promise<void> {
  try {
    await archiveMutation.mutateAsync({ project, restore });
    toast.success(restore ? "Проект восстановлен" : "Проект перемещён в архив");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

function openProject(project: Project): void {
  void router.push({
    name: routeNames.board,
    params: { workspaceSlug: workspaceSlug.value, projectId: project.id },
  });
}
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 py-7 sm:px-7 lg:px-10">
    <header class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <p class="text-xs font-medium uppercase tracking-[0.18em] text-primary">Workspace / {{ workspaceSlug }}</p>
        <h1 class="mt-2 text-2xl font-semibold tracking-tight">Проекты</h1>
        <p class="mt-1 text-sm text-muted-foreground">Создавайте проекты и управляйте работой на Kanban-досках.</p>
      </div>
      <AppButton @click="createOpen = true"><Plus class="size-4" /> Новый проект</AppButton>
    </header>

    <div class="mt-7 flex flex-col gap-3 rounded-xl border border-border bg-card p-3 sm:flex-row sm:items-center">
      <div class="relative flex-1">
        <Search class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <AppInput v-model="search" class="pl-9" placeholder="Поиск по названию или идентификатору" aria-label="Поиск проектов" />
      </div>
      <div class="rounded-lg px-2 py-1">
        <AppToggle v-model="showArchived" label="Архивные" />
      </div>
    </div>

    <div v-if="query.isPending.value" class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <AppSkeleton v-for="index in 6" :key="index" class="h-56 rounded-xl" />
    </div>

    <div v-else-if="query.isError.value" class="mt-6">
      <AppEmptyState title="Не удалось загрузить проекты" :description="getErrorMessage(query.error.value)">
        <AppButton variant="outline" @click="query.refetch()">Повторить</AppButton>
      </AppEmptyState>
    </div>

    <div v-else-if="projects.length === 0" class="mt-6">
      <AppEmptyState
        :title="showArchived ? 'Архив пуст' : search ? 'Ничего не найдено' : 'Создайте первый проект'"
        :description="showArchived ? 'Архивированные проекты появятся здесь.' : search ? 'Попробуйте изменить поисковый запрос.' : 'Проект автоматически получит четыре стандартные колонки.'"
      >
        <template #icon><Archive v-if="showArchived" class="size-5" /><FolderKanban v-else class="size-5" /></template>
        <AppButton v-if="!showArchived && !search" @click="createOpen = true"><Plus class="size-4" /> Новый проект</AppButton>
      </AppEmptyState>
    </div>

    <div v-else class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <ProjectCard
        v-for="project in projects"
        :key="project.id"
        :project="project"
        :pending="archiveMutation.isPending.value"
        @open="openProject"
        @archive="archiveProject"
      />
    </div>
  </div>

  <ProjectFormDialog
    ref="formRef"
    v-model:open="createOpen"
    :pending="createMutation.isPending.value"
    @submit="createProject"
  />
</template>
