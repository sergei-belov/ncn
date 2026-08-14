<script setup lang="ts">
import { CircleDashed } from "@lucide/vue";
const props = defineProps<{ title: string; description: string }>();
</script>

<template>
  <div class="flex min-h-56 flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card/60 px-6 py-10 text-center">
    <div class="mb-3 flex size-10 items-center justify-center rounded-xl bg-muted text-muted-foreground">
      <slot name="icon"><CircleDashed class="size-5" /></slot>
    </div>
    <h3 class="font-semibold">{{ props.title }}</h3>
    <p class="mt-1 max-w-md text-sm leading-6 text-muted-foreground">{{ props.description }}</p>
    <div v-if="$slots.default" class="mt-4"><slot /></div>
  </div>
</template>
