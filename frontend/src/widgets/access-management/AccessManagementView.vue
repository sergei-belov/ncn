<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AlertTriangle, Pencil, Plus, RefreshCw, Search, ShieldCheck, Trash2 } from "@lucide/vue";
import { useOnline } from "@vueuse/core";
import { toast } from "vue-sonner";

import {
  canManageProjectAccess,
  canManageWorkspaceAccess,
  isProjectMembership,
  projectRoleFor,
  useAuthzSessionQuery,
  useProjectMembershipsQuery,
  useWorkspaceMembershipsQuery,
  workspaceRoleFor,
  type AccessMembership,
  type ProjectAccessRole,
  type ProjectMembership,
  type ServiceRestriction,
  type WorkspaceRole,
} from "@/entities/authz";
import {
  AccessMemberDialog,
  RevokeAccessDialog,
  ServiceRestrictionDialog,
  useAccessMutations,
} from "@/features/access-manage";
import { ApiError, getErrorMessage } from "@/shared/api/api-error";
import {
  AppAvatar,
  AppBadge,
  AppButton,
  AppEmptyState,
  AppInput,
  AppSkeleton,
} from "@/shared/ui";

const props = withDefaults(
  defineProps<{
    scope: "workspace" | "project";
    workspaceId: string;
    projectId?: string;
    scopeName: string;
    readOnly?: boolean;
  }>(),
  { projectId: undefined, readOnly: false },
);

const route = useRoute();
const router = useRouter();
const online = useOnline();
const sessionQuery = useAuthzSessionQuery();
const workspaceRole = computed(() => workspaceRoleFor(sessionQuery.data.value, props.workspaceId));
const projectRole = computed(() => projectRoleFor(sessionQuery.data.value, props.projectId ?? ""));
const canManage = computed(() =>
  props.scope === "workspace"
    ? canManageWorkspaceAccess(workspaceRole.value)
    : canManageProjectAccess(projectRole.value),
);

const cursorHistory = ref<Array<string | undefined>>([]);
const search = computed({
  get: () => (typeof route.query.accessSearch === "string" ? route.query.accessSearch : ""),
  set: (value: string) => {
    cursorHistory.value = [];
    void router.replace({
      query: { ...route.query, accessSearch: value || undefined, accessCursor: undefined },
    });
  },
});
const cursor = computed(() => (typeof route.query.accessCursor === "string" ? route.query.accessCursor : undefined));
const filters = computed(() => ({ search: search.value || undefined, cursor: cursor.value, limit: 20 }));
const workspaceQuery = useWorkspaceMembershipsQuery(
  () => props.workspaceId,
  filters,
  computed(() => props.scope === "workspace" && canManage.value),
);
const projectQuery = useProjectMembershipsQuery(
  () => props.projectId ?? "",
  filters,
  computed(() => props.scope === "project" && Boolean(props.projectId) && canManage.value),
);
const members = computed<AccessMembership[]>(() =>
  props.scope === "workspace"
    ? (workspaceQuery.data.value?.items ?? [])
    : (projectQuery.data.value?.items ?? []),
);
const nextCursor = computed(() =>
  props.scope === "workspace"
    ? workspaceQuery.data.value?.nextCursor
    : projectQuery.data.value?.nextCursor,
);
const isPending = computed(() =>
  props.scope === "workspace" ? workspaceQuery.isPending.value : projectQuery.isPending.value,
);
const isFetching = computed(() =>
  props.scope === "workspace" ? workspaceQuery.isFetching.value : projectQuery.isFetching.value,
);
const queryError = computed(() =>
  props.scope === "workspace" ? workspaceQuery.error.value : projectQuery.error.value,
);
const canMutate = computed(
  () => canManage.value && online.value && !props.readOnly && !queryError.value && !isFetching.value,
);
const isPermissionError = computed(() => queryError.value instanceof ApiError && queryError.value.status === 403);

const mutations = useAccessMutations(() => props.workspaceId, () => props.projectId);
const memberDialogOpen = ref(false);
const revokeDialogOpen = ref(false);
const serviceDialogOpen = ref(false);
const selectedMembership = ref<AccessMembership>();
const selectedRestriction = ref<ServiceRestriction>();
const announcement = ref("");

watch(members, (canonicalMembers) => {
  if (!selectedMembership.value) return;
  const canonical = canonicalMembers.find((membership) => membership.id === selectedMembership.value?.id);
  if (!canonical) return;
  selectedMembership.value = canonical;
  if (selectedRestriction.value && isProjectMembership(canonical)) {
    selectedRestriction.value = canonical.serviceRestrictions.find(
      (restriction) => restriction.serviceId === selectedRestriction.value?.serviceId,
    );
  }
});

const memberMutation = computed(() => {
  if (props.scope === "workspace") {
    return selectedMembership.value ? mutations.updateWorkspace : mutations.addWorkspace;
  }
  return selectedMembership.value ? mutations.updateProject : mutations.addProject;
});
const revokeMutation = computed(() =>
  props.scope === "workspace" ? mutations.revokeWorkspace : mutations.revokeProject,
);
const servicePending = computed(
  () => mutations.setServiceRestriction.isPending.value || mutations.removeServiceRestriction.isPending.value,
);
const serviceError = computed(
  () => mutations.setServiceRestriction.error.value ?? mutations.removeServiceRestriction.error.value,
);

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

function roleLabel(role: WorkspaceRole | ProjectAccessRole): string {
  return {
    owner: "Владелец",
    admin: "Администратор",
    member: "Участник",
    viewer: "Наблюдатель",
  }[role];
}

function openAdd(): void {
  selectedMembership.value = undefined;
  mutations.addWorkspace.reset();
  mutations.addProject.reset();
  memberDialogOpen.value = true;
}

function openEdit(membership: AccessMembership): void {
  selectedMembership.value = membership;
  mutations.updateWorkspace.reset();
  mutations.updateProject.reset();
  memberDialogOpen.value = true;
}

function openRevoke(membership: AccessMembership): void {
  selectedMembership.value = membership;
  mutations.revokeWorkspace.reset();
  mutations.revokeProject.reset();
  revokeDialogOpen.value = true;
}

function openService(membership: ProjectMembership, restriction?: ServiceRestriction): void {
  selectedMembership.value = membership;
  selectedRestriction.value = restriction;
  mutations.setServiceRestriction.reset();
  mutations.removeServiceRestriction.reset();
  serviceDialogOpen.value = true;
}

function handlePermissionLoss(error: unknown): void {
  if (!(error instanceof ApiError) || error.status !== 403) return;
  memberDialogOpen.value = false;
  revokeDialogOpen.value = false;
  serviceDialogOpen.value = false;
  announcement.value = "Права на управление доступом изменились. Данные обновлены.";
}

async function saveMembership(values: { userId: string; role: WorkspaceRole | ProjectAccessRole }): Promise<void> {
  try {
    if (props.scope === "workspace") {
      if (selectedMembership.value && !isProjectMembership(selectedMembership.value)) {
        await mutations.updateWorkspace.mutateAsync({
          membership: selectedMembership.value,
          role: values.role as WorkspaceRole,
        });
      } else {
        await mutations.addWorkspace.mutateAsync({ userId: values.userId, role: values.role as WorkspaceRole });
      }
    } else if (selectedMembership.value && isProjectMembership(selectedMembership.value)) {
      await mutations.updateProject.mutateAsync({
        membership: selectedMembership.value,
        role: values.role as ProjectAccessRole,
      });
    } else {
      await mutations.addProject.mutateAsync({ userId: values.userId, role: values.role as ProjectAccessRole });
    }
    memberDialogOpen.value = false;
    announcement.value = selectedMembership.value ? "Роль участника обновлена" : "Доступ участника добавлен";
    toast.success(announcement.value);
  } catch (error) {
    handlePermissionLoss(error);
  }
}

async function revokeMembership(): Promise<void> {
  const membership = selectedMembership.value;
  if (!membership) return;
  try {
    if (isProjectMembership(membership)) await mutations.revokeProject.mutateAsync(membership);
    else await mutations.revokeWorkspace.mutateAsync(membership);
    revokeDialogOpen.value = false;
    announcement.value = `Доступ пользователя ${membership.user.name} удалён`;
    toast.success(announcement.value);
  } catch (error) {
    handlePermissionLoss(error);
  }
}

async function saveService(values: {
  serviceId: string;
  role: ProjectAccessRole;
  restriction?: ServiceRestriction;
}): Promise<void> {
  const membership = selectedMembership.value;
  if (!membership || !isProjectMembership(membership)) return;
  try {
    await mutations.setServiceRestriction.mutateAsync({ membership, ...values });
    serviceDialogOpen.value = false;
    announcement.value = `Ограничение сервиса ${values.serviceId} сохранено`;
    toast.success(announcement.value);
  } catch (error) {
    handlePermissionLoss(error);
  }
}

async function removeService(restriction: ServiceRestriction): Promise<void> {
  const membership = selectedMembership.value;
  if (!membership || !isProjectMembership(membership)) return;
  try {
    await mutations.removeServiceRestriction.mutateAsync({ membership, restriction });
    serviceDialogOpen.value = false;
    announcement.value = `Для сервиса ${restriction.serviceId} восстановлено наследование роли проекта`;
    toast.success(announcement.value);
  } catch (error) {
    handlePermissionLoss(error);
  }
}

function refetch(): void {
  if (props.scope === "workspace") void workspaceQuery.refetch();
  else void projectQuery.refetch();
}

function nextPage(): void {
  if (!nextCursor.value) return;
  cursorHistory.value.push(cursor.value);
  void router.replace({ query: { ...route.query, accessCursor: nextCursor.value } });
}

function previousPage(): void {
  const previous = cursorHistory.value.pop();
  void router.replace({ query: { ...route.query, accessCursor: previous } });
}
</script>

<template>
  <section class="mx-auto max-w-6xl p-4 sm:p-7" aria-labelledby="access-heading">
    <header class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <div class="flex items-center gap-2">
          <ShieldCheck class="size-5 text-primary" />
          <h1 id="access-heading" class="text-xl font-semibold">Управление доступом</h1>
        </div>
        <p class="mt-1 max-w-2xl text-sm leading-6 text-muted-foreground">
          {{ scope === "workspace" ? "Роли workspace определяют административный доступ в его границах." : "Роль проекта задаёт предел доступа, а ограничения сервисов могут только сузить её." }}
        </p>
      </div>
      <AppButton v-if="canManage" :disabled="!canMutate" @click="openAdd">
        <Plus class="size-4" /> Добавить участника
      </AppButton>
    </header>

    <div
      v-if="!online || readOnly"
      class="mt-5 flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm"
      role="status"
    >
      <AlertTriangle class="mt-0.5 size-4 shrink-0 text-amber-600 dark:text-amber-400" />
      <p>
        {{ !online ? "Нет подключения к сети. Загруженные данные доступны только для чтения; изменения возобновятся после обновления." : "Архивный проект доступен только для чтения." }}
      </p>
    </div>

    <AppEmptyState
      v-if="!sessionQuery.isPending.value && !canManage"
      class="mt-6"
      title="Недостаточно прав"
      description="Управление доступом доступно только владельцам и администраторам соответствующей области."
    >
      <template #icon><ShieldCheck class="size-5" /></template>
    </AppEmptyState>

    <template v-else>
      <div class="mt-6 flex items-center gap-3 rounded-xl border border-border bg-card p-3">
        <div class="relative flex-1">
          <Search class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <AppInput
            v-model="search"
            class="pl-9"
            placeholder="Имя, email или UUID"
            aria-label="Поиск участников доступа"
          />
        </div>
        <AppButton
          size="icon"
          variant="outline"
          :disabled="isFetching"
          aria-label="Обновить список участников"
          @click="refetch"
        >
          <RefreshCw class="size-4" :class="{ 'animate-spin': isFetching }" />
        </AppButton>
      </div>

      <div
        v-if="queryError && members.length > 0"
        class="mt-4 rounded-xl border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive"
        role="alert"
      >
        Не удалось обновить список. Показаны ранее загруженные данные только для чтения. {{ getErrorMessage(queryError) }}
      </div>

      <div v-if="isPending" class="mt-5 space-y-2" role="status" aria-label="Загрузка участников">
        <AppSkeleton v-for="index in 5" :key="index" class="h-20 rounded-xl" />
        <span class="sr-only">Загрузка списка участников</span>
      </div>

      <AppEmptyState
        v-else-if="queryError && members.length === 0"
        class="mt-5"
        :title="isPermissionError ? 'Доступ изменился' : 'Не удалось загрузить участников'"
        :description="isPermissionError ? 'У вас больше нет прав на просмотр этого списка.' : getErrorMessage(queryError)"
      >
        <AppButton v-if="!isPermissionError" variant="outline" @click="refetch">Повторить</AppButton>
      </AppEmptyState>

      <AppEmptyState
        v-else-if="members.length === 0"
        class="mt-5"
        :title="search ? 'Участники не найдены' : 'Список участников пуст'"
        :description="search ? 'Измените поисковый запрос.' : 'Добавьте существующего пользователя NCN по его UUID.'"
      >
        <AppButton v-if="!search && canMutate" @click="openAdd"><Plus class="size-4" /> Добавить участника</AppButton>
      </AppEmptyState>

      <div v-else class="mt-5 overflow-hidden rounded-xl border border-border bg-card">
        <div class="hidden overflow-x-auto md:block">
          <table class="w-full border-collapse text-left text-sm">
            <thead class="bg-muted/60 text-xs text-muted-foreground">
              <tr>
                <th scope="col" class="px-4 py-3 font-medium">Пользователь</th>
                <th scope="col" class="px-4 py-3 font-medium">{{ scope === "workspace" ? "Роль workspace" : "Роль проекта" }}</th>
                <th v-if="scope === 'project'" scope="col" class="px-4 py-3 font-medium">Доступ к сервисам</th>
                <th scope="col" class="px-4 py-3 text-right font-medium">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="membership in members" :key="membership.id" class="border-t border-border align-top">
                <td class="px-4 py-4">
                  <div class="flex items-center gap-3">
                    <AppAvatar :initials="initials(membership.user.name)" :title="membership.user.name" size="sm" />
                    <div class="min-w-0">
                      <p class="font-medium">{{ membership.user.name }}</p>
                      <p class="truncate text-xs text-muted-foreground">{{ membership.user.email }} · {{ membership.userId }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-4">
                  <AppBadge variant="outline">{{ roleLabel(membership.role) }}</AppBadge>
                  <p v-if="isProjectMembership(membership) && membership.source === 'bootstrap'" class="mt-1 text-xs text-muted-foreground">
                    Создан с проектом
                  </p>
                </td>
                <td v-if="scope === 'project'" class="max-w-sm px-4 py-4">
                  <template v-if="isProjectMembership(membership)">
                    <p v-if="membership.serviceRestrictions.length === 0" class="text-xs text-muted-foreground">
                      Наследуется из проекта: {{ roleLabel(membership.role) }}
                    </p>
                    <div v-else class="flex flex-wrap gap-1.5">
                      <button
                        v-for="restriction in membership.serviceRestrictions"
                        :key="restriction.id"
                        type="button"
                        class="focus-ring rounded-full"
                        :disabled="!canMutate"
                        :aria-label="`Изменить ограничение ${restriction.serviceId}`"
                        @click="openService(membership, restriction)"
                      >
                        <AppBadge variant="secondary">{{ restriction.serviceId }}: {{ roleLabel(restriction.role) }}</AppBadge>
                      </button>
                    </div>
                  </template>
                </td>
                <td class="px-4 py-4">
                  <div class="flex justify-end gap-1">
                    <AppButton
                      v-if="scope === 'project' && isProjectMembership(membership)"
                      size="sm"
                      variant="ghost"
                      :disabled="!canMutate"
                      :aria-label="`Ограничить сервис для ${membership.user.name}`"
                      @click="openService(membership)"
                    >
                      Сервис
                    </AppButton>
                    <AppButton
                      v-if="scope === 'project' || membership.role !== 'owner'"
                      size="icon"
                      variant="ghost"
                      class="size-8"
                      :disabled="!canMutate"
                      :aria-label="`Изменить роль ${membership.user.name}`"
                      @click="openEdit(membership)"
                    >
                      <Pencil class="size-4" />
                    </AppButton>
                    <AppButton
                      v-if="scope === 'project' || membership.role !== 'owner'"
                      size="icon"
                      variant="ghost"
                      class="size-8 text-destructive hover:bg-destructive/10"
                      :disabled="!canMutate"
                      :aria-label="`Удалить доступ ${membership.user.name}`"
                      @click="openRevoke(membership)"
                    >
                      <Trash2 class="size-4" />
                    </AppButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <ul class="divide-y divide-border md:hidden" aria-label="Участники доступа">
          <li v-for="membership in members" :key="membership.id" class="space-y-3 p-4">
            <div class="flex items-start gap-3">
              <AppAvatar :initials="initials(membership.user.name)" :title="membership.user.name" size="sm" />
              <div class="min-w-0 flex-1">
                <p class="font-medium">{{ membership.user.name }}</p>
                <p class="truncate text-xs text-muted-foreground">{{ membership.user.email }}</p>
                <p class="mt-1 break-all text-[11px] text-muted-foreground">{{ membership.userId }}</p>
              </div>
              <AppBadge variant="outline">{{ roleLabel(membership.role) }}</AppBadge>
            </div>
            <div v-if="isProjectMembership(membership)" class="text-xs text-muted-foreground">
              <p v-if="membership.source === 'bootstrap'">Создан с проектом</p>
              <p v-if="membership.serviceRestrictions.length === 0">Наследуется из проекта: {{ roleLabel(membership.role) }}</p>
              <div v-else class="mt-1 flex flex-wrap gap-1.5">
                <button
                  v-for="restriction in membership.serviceRestrictions"
                  :key="restriction.id"
                  type="button"
                  class="focus-ring rounded-full"
                  :disabled="!canMutate"
                  :aria-label="`Изменить ограничение ${restriction.serviceId}`"
                  @click="openService(membership, restriction)"
                >
                  <AppBadge variant="secondary">{{ restriction.serviceId }}: {{ roleLabel(restriction.role) }}</AppBadge>
                </button>
              </div>
            </div>
            <div class="flex flex-wrap justify-end gap-1">
              <AppButton
                v-if="isProjectMembership(membership)"
                size="sm"
                variant="ghost"
                :disabled="!canMutate"
                :aria-label="`Ограничить сервис для ${membership.user.name}`"
                @click="openService(membership)"
              >
                Ограничить сервис
              </AppButton>
              <AppButton
                v-if="scope === 'project' || membership.role !== 'owner'"
                size="sm"
                variant="ghost"
                :disabled="!canMutate"
                :aria-label="`Изменить роль ${membership.user.name}`"
                @click="openEdit(membership)"
              >
                <Pencil class="size-3.5" /> Изменить
              </AppButton>
              <AppButton
                v-if="scope === 'project' || membership.role !== 'owner'"
                size="sm"
                variant="ghost"
                class="text-destructive"
                :disabled="!canMutate"
                :aria-label="`Удалить доступ ${membership.user.name}`"
                @click="openRevoke(membership)"
              >
                <Trash2 class="size-3.5" /> Удалить
              </AppButton>
            </div>
          </li>
        </ul>
      </div>

      <div v-if="members.length > 0" class="mt-4 flex items-center justify-between">
        <p class="text-xs text-muted-foreground">Показано: {{ members.length }}</p>
        <div class="flex gap-2">
          <AppButton variant="outline" size="sm" :disabled="cursorHistory.length === 0" @click="previousPage">Назад</AppButton>
          <AppButton variant="outline" size="sm" :disabled="!nextCursor" @click="nextPage">Далее</AppButton>
        </div>
      </div>
    </template>

    <p class="sr-only" aria-live="polite">{{ announcement }}</p>

    <AccessMemberDialog
      v-model:open="memberDialogOpen"
      :scope="scope"
      :membership="selectedMembership"
      :pending="memberMutation.isPending.value"
      :error="memberMutation.error.value"
      @submit="saveMembership"
    />
    <RevokeAccessDialog
      v-model:open="revokeDialogOpen"
      :membership="selectedMembership"
      :scope-name="scopeName"
      :pending="revokeMutation.isPending.value"
      :error="revokeMutation.error.value"
      @confirm="revokeMembership"
    />
    <ServiceRestrictionDialog
      v-if="scope === 'project'"
      v-model:open="serviceDialogOpen"
      :membership="selectedMembership && isProjectMembership(selectedMembership) ? selectedMembership : undefined"
      :restriction="selectedRestriction"
      :pending="servicePending"
      :error="serviceError"
      @submit="saveService"
      @remove="removeService"
    />
  </section>
</template>
