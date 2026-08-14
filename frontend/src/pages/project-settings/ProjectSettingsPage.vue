<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Archive, RotateCcw, Save, Settings2 } from "@lucide/vue";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { toast } from "vue-sonner";
import { z } from "zod";

import { useProjectQuery } from "@/entities/project";
import { useArchiveProject, useUpdateProject } from "@/features/project-create";
import { getErrorMessage } from "@/shared/api/api-error";
import { routeNames } from "@/shared/routes";
import { AppBadge, AppButton, AppDialog, AppFormField, AppInput, AppTextarea } from "@/shared/ui";
import { SettingsTabs } from "@/widgets/project-navigation";

const schema = z.object({
  name: z.string().trim().min(2, "Введите не менее двух символов").max(80),
  description: z.string().trim().max(500),
  access: z.enum(["private", "workspace"]),
});
type Values = z.infer<typeof schema>;

const route = useRoute();
const router = useRouter();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const query = useProjectQuery(workspaceSlug, projectId);
const project = computed(() => query.data.value);
const updateMutation = useUpdateProject(workspaceSlug);
const archiveMutation = useArchiveProject(workspaceSlug);
const archiveOpen = ref(false);

const { errors, defineField, handleSubmit, resetForm } = useForm<Values>({ validationSchema: toTypedSchema(schema) });
const [name, nameAttrs] = defineField("name");
const [description, descriptionAttrs] = defineField("description");
const [access, accessAttrs] = defineField("access");

watch(
  project,
  (value) => {
    if (value) resetForm({ values: { name: value.name, description: value.description, access: value.access } });
  },
  { immediate: true },
);

const save = handleSubmit(async (values) => {
  if (!project.value) return;
  try {
    await updateMutation.mutateAsync({ project: project.value, input: values });
    toast.success("Настройки сохранены");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
});

async function toggleArchive(): Promise<void> {
  if (!project.value) return;
  try {
    const restore = Boolean(project.value.archivedAt);
    await archiveMutation.mutateAsync({ project: project.value, restore });
    archiveOpen.value = false;
    toast.success(restore ? "Проект восстановлен" : "Проект архивирован");
    if (!restore) await router.push({ name: routeNames.projects, params: { workspaceSlug: workspaceSlug.value } });
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="flex h-16 items-center gap-3 border-b border-border bg-card px-4 sm:px-7">
      <Settings2 class="size-4 text-primary" />
      <div><h1 class="text-base font-semibold">Настройки проекта</h1><p class="text-xs text-muted-foreground">{{ project?.name }}</p></div>
    </header>
    <SettingsTabs />

    <div class="mx-auto max-w-3xl p-4 sm:p-7">
      <div v-if="query.isPending.value" class="text-sm text-muted-foreground">Загрузка…</div>
      <form v-else-if="project" class="space-y-6" @submit="save">
        <section class="rounded-xl border border-border bg-card p-5 sm:p-6">
          <div class="mb-5 flex items-center justify-between">
            <div><h2 class="font-semibold">Основное</h2><p class="mt-1 text-sm text-muted-foreground">Название, описание и доступ к проекту.</p></div>
            <AppBadge variant="outline">{{ project.identifier }}</AppBadge>
          </div>
          <div class="space-y-4">
            <AppFormField label="Название" required :error="errors.name">
              <AppInput v-model="name" v-bind="nameAttrs" :disabled="!project.permissions.canEditProject" />
            </AppFormField>
            <AppFormField label="Описание" :error="errors.description">
              <AppTextarea v-model="description" v-bind="descriptionAttrs" :rows="4" :disabled="!project.permissions.canEditProject" />
            </AppFormField>
            <AppFormField label="Доступ" :error="errors.access">
              <select v-model="access" v-bind="accessAttrs" class="focus-ring h-9 w-full rounded-md border border-input bg-card px-3 text-sm" :disabled="!project.permissions.canEditProject">
                <option value="workspace">Весь workspace</option>
                <option value="private">Только участники проекта</option>
              </select>
            </AppFormField>
          </div>
          <div class="mt-5 flex justify-end">
            <AppButton v-if="project.permissions.canEditProject" type="submit" :loading="updateMutation.isPending.value"><Save class="size-4" /> Сохранить</AppButton>
          </div>
        </section>

        <section class="rounded-xl border border-destructive/25 bg-card p-5 sm:p-6">
          <h2 class="font-semibold text-destructive">Опасная зона</h2>
          <div class="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div><p class="text-sm font-medium">{{ project.archivedAt ? "Восстановить проект" : "Архивировать проект" }}</p><p class="mt-1 text-xs leading-5 text-muted-foreground">{{ project.archivedAt ? "Проект снова станет доступен для редактирования." : "Проект станет доступен только для чтения." }}</p></div>
            <AppButton v-if="project.permissions.canArchiveProject" :variant="project.archivedAt ? 'outline' : 'destructive'" @click="archiveOpen = true">
              <RotateCcw v-if="project.archivedAt" class="size-4" /><Archive v-else class="size-4" />
              {{ project.archivedAt ? "Восстановить" : "Архивировать" }}
            </AppButton>
          </div>
        </section>
      </form>
    </div>
  </div>

  <AppDialog v-model:open="archiveOpen" :title="project?.archivedAt ? 'Восстановить проект?' : 'Архивировать проект?'" width="sm">
    <p class="text-sm text-muted-foreground">{{ project?.archivedAt ? "Пользователи снова смогут изменять карточки и эпики." : "Карточки и эпики сохранятся, но изменения будут запрещены до восстановления." }}</p>
    <div class="mt-5 flex justify-end gap-2">
      <AppButton variant="outline" @click="archiveOpen = false">Отмена</AppButton>
      <AppButton :variant="project?.archivedAt ? 'default' : 'destructive'" :loading="archiveMutation.isPending.value" @click="toggleArchive">
        {{ project?.archivedAt ? "Восстановить" : "Архивировать" }}
      </AppButton>
    </div>
  </AppDialog>
</template>
