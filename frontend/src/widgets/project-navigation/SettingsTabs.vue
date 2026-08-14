<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { Columns3, Settings2, ShieldCheck } from "@lucide/vue";

import { canManageProjectAccess, projectRoleFor, useAuthzSessionQuery } from "@/entities/authz";
import { routeNames } from "@/shared/routes";

const route = useRoute();
const workspaceSlug = computed(() => String(route.params.workspaceSlug));
const projectId = computed(() => String(route.params.projectId));
const sessionQuery = useAuthzSessionQuery();
const canManageAccess = computed(() =>
  canManageProjectAccess(projectRoleFor(sessionQuery.data.value, projectId.value)),
);
const tabs = computed(() => [
  { name: routeNames.projectSettings, label: "Основное", icon: Settings2 },
  { name: routeNames.stateSettings, label: "Состояния", icon: Columns3 },
  ...(canManageAccess.value ? [{ name: routeNames.projectAccess, label: "Доступ", icon: ShieldCheck }] : []),
]);
</script>

<template>
  <nav class="flex gap-1 border-b border-border px-4 sm:px-7">
    <RouterLink
      v-for="tab in tabs"
      :key="tab.name"
      :to="{ name: tab.name, params: { workspaceSlug, projectId } }"
      class="focus-ring flex h-11 items-center gap-2 border-b-2 border-transparent px-3 text-sm text-muted-foreground hover:text-foreground"
      active-class="!border-primary !text-foreground font-medium"
    >
      <component :is="tab.icon" class="size-4" /> {{ tab.label }}
    </RouterLink>
  </nav>
</template>
