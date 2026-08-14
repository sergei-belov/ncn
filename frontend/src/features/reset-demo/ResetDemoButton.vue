<script setup lang="ts">
import { RotateCcw } from "@lucide/vue";
import { toast } from "vue-sonner";

import { env } from "@/shared/config/env";
import { useRuntimeControls } from "@/shared/config/runtime-controls";
import { AppButton } from "@/shared/ui";

const props = defineProps<{ workspaceSlug: string; collapsed?: boolean }>();
const controls = useRuntimeControls();

function resetDemo(): void {
  controls.resetDemoData();
  toast.success("Демо-данные восстановлены");
  window.location.assign(`/${props.workspaceSlug}/projects`);
}
</script>

<template>
  <AppButton
    v-if="env.VITE_API_MODE === 'mock'"
    variant="ghost"
    class="w-full justify-start"
    :size="props.collapsed ? 'icon' : 'default'"
    @click="resetDemo"
  >
    <RotateCcw class="size-4" />
    <span v-if="!props.collapsed">Сбросить демо</span>
  </AppButton>
</template>
