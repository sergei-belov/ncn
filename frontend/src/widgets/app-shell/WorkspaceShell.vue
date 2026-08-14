<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { FolderKanban, Moon, PanelLeftClose, PanelLeftOpen, Sun } from "@lucide/vue";
import { useColorMode } from "@vueuse/core";

import { ResetDemoButton } from "@/features/reset-demo";
import { routeNames } from "@/shared/routes";
import { AppButton } from "@/shared/ui";

const route = useRoute();
const collapsed = ref(false);
const mode = useColorMode({ attribute: "class", modes: { light: "light", dark: "dark" } });
const workspaceSlug = computed(() => String(route.params.workspaceSlug ?? "demo"));

function toggleMode(): void {
  mode.value = mode.value === "dark" ? "light" : "dark";
}

</script>

<template>
  <div class="flex min-h-screen bg-background">
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
      </nav>

      <div class="space-y-1 border-t border-border p-2">
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

    <main class="min-w-0 flex-1"><RouterView /></main>
  </div>
</template>
