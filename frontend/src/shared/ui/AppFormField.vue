<script setup lang="ts">
const props = withDefaults(
  defineProps<{ label: string; for?: string; error?: string; hint?: string; required?: boolean }>(),
  { for: undefined, error: "", hint: "", required: false },
);
</script>

<template>
  <div class="space-y-1.5">
    <label :for="props.for" class="text-sm font-medium">
      {{ props.label }} <span v-if="props.required" class="text-destructive">*</span>
    </label>
    <slot />
    <p v-if="props.error" class="text-xs text-destructive">{{ props.error }}</p>
    <p v-else-if="props.hint" class="text-xs text-muted-foreground">{{ props.hint }}</p>
  </div>
</template>
