<script setup lang="ts">
import { cn } from "@/shared/lib/cn";

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

const model = defineModel<string | null>({ default: null });
const props = withDefaults(
  defineProps<{ id?: string; options: SelectOption[]; placeholder?: string; disabled?: boolean; class?: string }>(),
  { id: undefined, placeholder: "Выберите значение", disabled: false, class: "" },
);
</script>

<template>
  <select
    :id="props.id"
    :value="model ?? ''"
    :disabled="props.disabled"
    :class="cn('focus-ring h-9 w-full rounded-md border border-input bg-card px-3 text-sm disabled:cursor-not-allowed disabled:opacity-50', props.class)"
    @change="model = ($event.target as HTMLSelectElement).value || null"
  >
    <option value="">{{ props.placeholder }}</option>
    <option v-for="option in props.options" :key="option.value" :value="option.value" :disabled="option.disabled">
      {{ option.label }}
    </option>
  </select>
</template>
