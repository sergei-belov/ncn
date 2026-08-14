<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { FolderKanban, Moon, PanelLeftClose, PanelLeftOpen, ShieldCheck, Sun } from "@lucide/vue";
import { useColorMode } from "@vueuse/core";

import { canManageWorkspaceAccess, useAuthzSessionQuery, workspaceRoleFor } from "@/entities/authz";
import { ResetDemoButton } from "@/features/reset-demo";
import { ApiError } from "@/shared/api/api-error";
import { routeNames } from "@/shared/routes";
import { AppAvatar, AppButton, AppEmptyState, AppSkeleton } from "@/shared/ui";

const route = useRoute();
const collapsed = ref(false);
const mode = useColorMode({ attribute: "class", modes: { light: "light", dark: "dark" } });
const workspaceSlug = computed(() => String(route.params.workspaceSlug ?? "demo"));
const sessionQuery = useAuthzSessionQuery();
const session = computed(() => sessionQuery.data.value);
const workspaceRole = computed(() => workspaceRoleFor(session.value, workspaceSlug.value));
const canManageAccess = computed(() => canManageWorkspaceAccess(workspaceRole.value));
const noAccess = computed(
  () => Boolean(session.value && session.value.workspaceAccess.length === 0 && session.value.projectAccess.length === 0),
);
const sessionError = computed(() => (sessionQuery.error.value instanceof ApiError ? sessionQuery.error.value : undefined));
const sessionErrorTitle = computed(() => {
  if (sessionError.value?.code === "USER_DISABLED") return "Учётная запись отключена";
  if (sessionError.value?.status === 401 || sessionError.value?.code.startsWith("IDENTITY_")) return "Не удалось подтвердить вход";
  return "Сервис доступа временно недоступен";
});
const sessionErrorDescription = computed(() => {
  if (sessionError.value?.code === "USER_DISABLED") return "Обратитесь к администратору NCN или в поддержку.";
  if (sessionError.value?.status === 401 || sessionError.value?.code.startsWith("IDENTITY_")) {
    return "Обновите SSO-сессию и повторите вход. Доступ не был предоставлен автоматически.";
  }
  return "Защищённый контент не показан. Повторите проверку или передайте поддержке код обращения.";
});
const userInitials = computed(() =>
  (session.value?.user.name ?? "")
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join(""),
);

function toggleMode(): void {
  mode.value = mode.value === "dark" ? "light" : "dark";
}
</script>

<template>
  <div v-if="sessionQuery.isPending.value" class="flex min-h-screen items-center justify-center bg-background p-6" role="status">
    <div class="w-full max-w-md space-y-4 text-center">
      <div class="mx-auto flex size-11 items-center justify-center rounded-xl bg-primary text-primary-foreground">
        <ShieldCheck class="size-5" />
      </div>
      <div>
        <h1 class="font-semibold">Проверяем доступ</h1>
        <p class="mt-1 text-sm text-muted-foreground">Подтверждаем защищённую сессию и доступные области.</p>
      </div>
      <AppSkeleton class="h-2 w-full" />
    </div>
  </div>

  <div v-else-if="sessionQuery.isError.value" class="flex min-h-screen items-center justify-center bg-background p-4">
    <AppEmptyState :title="sessionErrorTitle" :description="sessionErrorDescription">
      <template #icon><ShieldCheck class="size-5" /></template>
      <div class="space-y-3">
        <p v-if="sessionError" class="text-xs text-muted-foreground">
          Код обращения: <code class="rounded bg-muted px-1.5 py-0.5">{{ sessionError.requestId }}</code>
        </p>
        <AppButton variant="outline" @click="sessionQuery.refetch()">Повторить проверку</AppButton>
      </div>
    </AppEmptyState>
  </div>

  <div v-else-if="noAccess" class="flex min-h-screen items-center justify-center bg-background p-4">
    <AppEmptyState
      title="Доступ ещё не назначен"
      description="Вход выполнен, но у вашей учётной записи нет ролей workspace или проекта. Обратитесь к администратору NCN."
    >
      <template #icon><ShieldCheck class="size-5" /></template>
      <AppButton variant="outline" @click="sessionQuery.refetch()">Обновить доступ</AppButton>
    </AppEmptyState>
  </div>

  <div v-else class="flex min-h-screen flex-col bg-background md:flex-row">
    <aside
      class="sticky top-0 hidden h-screen shrink-0 flex-col border-r border-border bg-card md:flex"
      :class="collapsed ? 'w-16' : 'w-56'"
    >
      <div class="flex h-16 items-center gap-3 border-b border-border px-4">
        <div class="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <FolderKanban class="size-4" />
        </div>
        <div v-if="!collapsed" class="min-w-0">
          <p class="truncate text-sm font-semibold">Project OS</p>
          <p class="truncate text-[11px] text-muted-foreground">{{ workspaceSlug }}</p>
        </div>
      </div>

      <nav class="flex-1 space-y-1 p-2">
        <RouterLink
          :to="{ name: routeNames.projects, params: { workspaceSlug } }"
          class="focus-ring flex h-9 items-center gap-3 rounded-md px-3 text-sm text-muted-foreground hover:bg-muted hover:text-foreground"
          active-class="bg-accent !text-accent-foreground font-medium"
        >
          <FolderKanban class="size-4 shrink-0" />
          <span v-if="!collapsed">Проекты</span>
        </RouterLink>
        <RouterLink
          v-if="canManageAccess"
          :to="{ name: routeNames.workspaceAccess, params: { workspaceSlug } }"
          class="focus-ring flex h-9 items-center gap-3 rounded-md px-3 text-sm text-muted-foreground hover:bg-muted hover:text-foreground"
          active-class="bg-accent !text-accent-foreground font-medium"
        >
          <ShieldCheck class="size-4 shrink-0" />
          <span v-if="!collapsed">Доступ workspace</span>
        </RouterLink>
      </nav>

      <div class="space-y-1 border-t border-border p-2">
        <div v-if="session && !collapsed" class="mb-2 flex items-center gap-2 rounded-lg bg-muted/60 p-2">
          <AppAvatar :initials="userInitials" :title="session.user.name" size="sm" />
          <div class="min-w-0">
            <p class="truncate text-xs font-medium">{{ session.user.name }}</p>
            <p class="truncate text-[10px] text-muted-foreground">{{ session.user.email }}</p>
          </div>
        </div>
        <AppButton variant="ghost" class="w-full justify-start" :size="collapsed ? 'icon' : 'default'" @click="toggleMode">
          <Sun v-if="mode === 'dark'" class="size-4" />
          <Moon v-else class="size-4" />
          <span v-if="!collapsed">{{ mode === "dark" ? "Светлая тема" : "Тёмная тема" }}</span>
        </AppButton>
        <ResetDemoButton :workspace-slug="workspaceSlug" :collapsed="collapsed" />
        <AppButton variant="ghost" class="w-full justify-start" :size="collapsed ? 'icon' : 'default'" @click="collapsed = !collapsed">
          <PanelLeftOpen v-if="collapsed" class="size-4" />
          <PanelLeftClose v-else class="size-4" />
          <span v-if="!collapsed">Свернуть</span>
        </AppButton>
      </div>
    </aside>

    <div class="min-w-0 flex-1">
      <header class="flex min-h-14 items-center gap-1 border-b border-border bg-card px-2 md:hidden">
        <RouterLink
          :to="{ name: routeNames.projects, params: { workspaceSlug } }"
          class="focus-ring flex h-9 flex-1 items-center justify-center gap-2 rounded-md text-sm text-muted-foreground"
          active-class="bg-accent !text-accent-foreground font-medium"
        >
          <FolderKanban class="size-4" /> Проекты
        </RouterLink>
        <RouterLink
          v-if="canManageAccess"
          :to="{ name: routeNames.workspaceAccess, params: { workspaceSlug } }"
          class="focus-ring flex h-9 flex-1 items-center justify-center gap-2 rounded-md text-sm text-muted-foreground"
          active-class="bg-accent !text-accent-foreground font-medium"
        >
          <ShieldCheck class="size-4" /> Доступ
        </RouterLink>
        <AppButton size="icon" variant="ghost" :aria-label="mode === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему'" @click="toggleMode">
          <Sun v-if="mode === 'dark'" class="size-4" />
          <Moon v-else class="size-4" />
        </AppButton>
      </header>
      <main><RouterView /></main>
    </div>
  </div>
</template>
