<script setup lang="ts">
import { cn } from "@/shared/lib/cn";

const props = withDefaults(
  defineProps<{ variant?: "default" | "secondary" | "outline" | "danger"; class?: string }>(),
  { variant: "secondary", class: "" },
);

const variants = {
  default: "border-transparent bg-primary text-primary-foreground",
  secondary: "border-transparent bg-secondary text-secondary-foreground",
  outline: "border-border bg-card text-foreground",
  danger: "border-transparent bg-destructive/10 text-destructive",
};
</script>

<template>
  <span :class="cn('inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium', variants[props.variant], props.class)">
    <slot />
  </span>
</template>
