<script setup lang="ts">
import { cn } from "@/shared/lib/cn";

const props = withDefaults(
  defineProps<{ src?: string | null; initials: string; title?: string; size?: "sm" | "md"; class?: string }>(),
  { src: null, title: "", size: "md", class: "" },
);
</script>

<template>
  <span
    :title="props.title"
    :class="cn('inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full border border-card bg-primary/12 font-semibold text-primary', props.size === 'sm' ? 'size-6 text-[9px]' : 'size-8 text-[11px]', props.class)"
  >
    <img v-if="props.src" :src="props.src" :alt="props.title" class="size-full object-cover" />
    <span v-else>{{ props.initials }}</span>
  </span>
</template>
