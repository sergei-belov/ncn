<script setup lang="ts">
import { ref } from "vue";

import { cn } from "@/shared/lib/cn";

const model = defineModel<string>({ default: "" });
const props = withDefaults(
  defineProps<{
    id?: string;
    type?: string;
    placeholder?: string;
    disabled?: boolean;
    ariaLabel?: string;
    autocomplete?: string;
    class?: string;
  }>(),
  { id: undefined, type: "text", placeholder: "", disabled: false, ariaLabel: undefined, autocomplete: undefined, class: "" },
);
const inputRef = ref<HTMLInputElement>();

function focus(): void {
  inputRef.value?.focus();
}

defineExpose({ focus });
</script>

<template>
  <input
    :id="props.id"
    ref="inputRef"
    v-model="model"
    :type="props.type"
    :placeholder="props.placeholder"
    :disabled="props.disabled"
    :aria-label="props.ariaLabel"
    :autocomplete="props.autocomplete"
    :class="cn('focus-ring h-9 w-full rounded-md border border-input bg-card px-3 text-sm placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50', props.class)"
  />
</template>
