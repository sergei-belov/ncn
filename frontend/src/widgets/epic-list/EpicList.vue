<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Layers3, Plus, Search } from "@lucide/vue";
import { toast } from "vue-sonner";

import { EpicCard, useEpicsQuery } from "@/entities/epic";
import { useProjectQuery } from "@/entities/project";
import { EpicFormDialog, useEpicMutations, type EpicFormValues } from "@/features/epic-create";
import { getErrorMessage } from "@/shared/api/api-error";
import { routeNames } from "@/shared/routes";
import { AppBadge, AppButton, AppEmptyState, AppInput, AppSkeleton } from "@/shared/ui";

const route = useRoute();
const router = useRouter();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const search = ref("");
const createOpen = ref(false);
const filters = computed(() => ({ search: search.value || undefined }));
const query = useEpicsQuery(workspaceSlug, projectId, filters);
const projectQuery = useProjectQuery(workspaceSlug, projectId);
const epics = computed(() => query.data.value ?? []);
const project = computed(() => projectQuery.data.value);
const mutations = useEpicMutations(workspaceSlug, projectId);

async function createEpic(values: EpicFormValues): Promise<void> {
  try {
    const epic = await mutations.create.mutateAsync(values);
    createOpen.value = false;
    toast.success("Эпик создан");
    openEpic(epic.id);
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

function openEpic(epicId: string): void {
  void router.push({
    name: routeNames.epic,
    params: { workspaceSlug: workspaceSlug.value, projectId: projectId.value, epicId },
    state: { backgroundRoute: route.fullPath, backgroundName: "epics" },
  });
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="flex min-h-16 items-center justify-between gap-4 border-b border-border bg-card px-4 sm:px-7">
      <div>
        <div class="flex items-center gap-2"><Layers3 class="size-4 text-primary" /><h1 class="text-base font-semibold">Эпики</h1></div>
        <p class="mt-0.5 text-xs text-muted-foreground">{{ project?.name }}</p>
      </div>
      <AppButton v-if="project?.permissions.canCreateEpic && !project.archivedAt" @click="createOpen = true"><Plus class="size-4" /> Новый эпик</AppButton>
    </header>

    <div class="mx-auto max-w-6xl p-4 sm:p-7">
      <div class="flex items-center gap-3 rounded-xl border border-border bg-card p-3">
        <div class="relative flex-1">
          <Search class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <AppInput v-model="search" class="pl-9" placeholder="Поиск эпиков" />
        </div>
        <AppBadge variant="outline">{{ epics.length }} всего</AppBadge>
      </div>

      <div v-if="query.isPending.value" class="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <AppSkeleton v-for="index in 6" :key="index" class="h-64 rounded-xl" />
      </div>
      <div v-else-if="query.isError.value" class="mt-5">
        <AppEmptyState title="Не удалось загрузить эпики" :description="getErrorMessage(query.error.value)">
          <AppButton variant="outline" @click="query.refetch()">Повторить</AppButton>
        </AppEmptyState>
      </div>
      <div v-else-if="epics.length === 0" class="mt-5">
        <AppEmptyState :title="search ? 'Эпики не найдены' : 'Создайте первый эпик'" description="Эпики объединяют связанные карточки и показывают прогресс.">
          <template #icon><Layers3 class="size-5" /></template>
          <AppButton v-if="!search && project?.permissions.canCreateEpic" @click="createOpen = true"><Plus class="size-4" /> Новый эпик</AppButton>
        </AppEmptyState>
      </div>
      <div v-else class="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <EpicCard v-for="epic in epics" :key="epic.id" :epic="epic" @open="openEpic(epic.id)" />
      </div>
    </div>
  </div>

  <EpicFormDialog v-model:open="createOpen" :pending="mutations.create.isPending.value" @submit="createEpic" />
</template>
