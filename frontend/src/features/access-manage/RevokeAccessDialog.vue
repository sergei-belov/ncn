<script setup lang="ts">
import { computed } from "vue";

import type { AccessMembership } from "@/entities/authz";
import { ApiError } from "@/shared/api/api-error";
import { AppButton, AppDialog } from "@/shared/ui";

const open = defineModel<boolean>("open", { default: false });
const props = withDefaults(
  defineProps<{
    membership?: AccessMembership;
    scopeName: string;
    pending?: boolean;
    error?: unknown;
  }>(),
  { membership: undefined, pending: false, error: undefined },
);
const emit = defineEmits<{ confirm: [] }>();
const errorMessage = computed(() => (props.error instanceof Error ? props.error.message : ""));
const requestId = computed(() => (props.error instanceof ApiError ? props.error.requestId : ""));
</script>

<template>
  <AppDialog v-model:open="open" title="Удалить доступ?" width="sm">
    <div class="space-y-4">
      <p class="text-sm leading-6 text-muted-foreground">
        Удалить <strong class="text-foreground">{{ membership?.user.name }}</strong> из
        <strong class="text-foreground">{{ scopeName }}</strong>? Доступ будет потерян со следующего запроса.
      </p>
      <div v-if="errorMessage" class="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive" role="alert">
        <p>{{ errorMessage }}</p>
        <p v-if="requestId" class="mt-1 text-xs">Код обращения: <code>{{ requestId }}</code></p>
      </div>
      <div class="flex justify-end gap-2">
        <AppButton variant="outline" @click="open = false">Отмена</AppButton>
        <AppButton variant="destructive" :loading="pending" @click="emit('confirm')">Удалить доступ</AppButton>
      </div>
    </div>
  </AppDialog>
</template>

