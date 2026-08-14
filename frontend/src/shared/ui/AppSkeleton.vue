<script setup lang="ts">
import { cn } from "@/shared/lib/cn";
const props = withDefaults(defineProps<{ class?: string }>(), { class: "" });
</script>

<template>
  <div :class="cn('animate-pulse rounded-md bg-muted', props.class)" />
</template>
