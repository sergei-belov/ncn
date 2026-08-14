<script setup lang="ts">
const props = defineProps<{ value: number; label?: string }>();
</script>

<template>
  <div class="w-full" :aria-label="props.label" role="progressbar" :aria-valuenow="props.value" aria-valuemin="0" aria-valuemax="100">
    <div class="h-1.5 overflow-hidden rounded-full bg-muted">
      <div class="h-full rounded-full bg-primary transition-[width]" :style="{ width: `${Math.max(0, Math.min(100, props.value))}%` }" />
    </div>
  </div>
</template>
