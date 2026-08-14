<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import { AccessManagementView } from "@/widgets/access-management";

const route = useRoute();
const workspaceId = computed(() => String(route.params.workspaceSlug));
</script>

<template>
  <AccessManagementView
    scope="workspace"
    :workspace-id="workspaceId"
    :scope-name="`workspace ${workspaceId}`"
  />
</template>

