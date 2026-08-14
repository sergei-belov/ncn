<script setup lang="ts">
const model = defineModel<boolean>({ default: false });
const props = defineProps<{ label: string; description?: string; disabled?: boolean }>();
</script>

<template>
  <label class="flex items-start gap-3" :class="props.disabled ? 'opacity-60' : 'cursor-pointer'">
    <input
      v-model="model"
      type="checkbox"
      role="switch"
      :aria-checked="model"
      :disabled="props.disabled"
      class="peer sr-only"
    />
    <span
      aria-hidden="true"
      class="relative mt-0.5 h-5 w-9 shrink-0 rounded-full transition-colors peer-focus-visible:outline-none peer-focus-visible:ring-2 peer-focus-visible:ring-ring peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-background"
      :class="model ? 'bg-primary' : 'bg-input'"
    >
      <span class="absolute top-0.5 size-4 rounded-full bg-white shadow transition-transform" :class="model ? 'translate-x-4' : 'translate-x-0.5'" />
    </span>
    <span>
      <span class="block text-sm font-medium">{{ props.label }}</span>
      <span v-if="props.description" class="mt-0.5 block text-xs leading-5 text-muted-foreground">{{ props.description }}</span>
    </span>
  </label>
</template>
