<script setup lang="ts">
import type { CreateAgentInput } from "@/entities/agent";
import { AppDialog } from "@/shared/ui";

import AgentConfigForm from "./AgentConfigForm.vue";

const open = defineModel<boolean>("open", { default: false });
const props = defineProps<{ pending?: boolean }>();
const emit = defineEmits<{ submit: [input: CreateAgentInput] }>();
</script>

<template>
  <AppDialog v-model:open="open" title="Новый ассистент" description="Ассистент работает только внутри текущего проекта." width="lg">
    <AgentConfigForm v-if="open" :pending="props.pending" submit-label="Создать ассистента" @submit="emit('submit', $event)" />
  </AppDialog>
</template>
