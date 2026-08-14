<script setup lang="ts">
import { cn } from "@/shared/lib/cn";

const model = defineModel<string>({ default: "" });
const props = withDefaults(
  defineProps<{ id?: string; placeholder?: string; disabled?: boolean; rows?: number; class?: string }>(),
  { id: undefined, placeholder: "", disabled: false, rows: 4, class: "" },
);
</script>

<template>
  <textarea
    :id="props.id"
    v-model="model"
    :rows="props.rows"
    :placeholder="props.placeholder"
    :disabled="props.disabled"
    :class="cn('focus-ring w-full resize-y rounded-md border border-input bg-card px-3 py-2 text-sm placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50', props.class)"
  />
</template>
