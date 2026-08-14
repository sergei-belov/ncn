<script setup lang="ts">
import { nextTick, ref } from "vue";
import { Plus } from "@lucide/vue";

import { AppButton, AppInput } from "@/shared/ui";

const props = withDefaults(defineProps<{ disabled?: boolean; pending?: boolean }>(), { disabled: false, pending: false });
const emit = defineEmits<{ submit: [title: string] }>();
const active = ref(false);
const title = ref("");
const inputRef = ref<{ focus: () => void }>();

async function activate(): Promise<void> {
  if (props.disabled) return;
  active.value = true;
  await nextTick();
  inputRef.value?.focus();
}

function cancel(): void {
  active.value = false;
  title.value = "";
}

function submit(): void {
  const value = title.value.trim();
  if (!value || props.pending) return;
  emit("submit", value);
  title.value = "";
}
</script>

<template>
  <div v-if="active" class="rounded-lg border border-primary/30 bg-card p-2 shadow-sm">
    <AppInput
      ref="inputRef"
      v-model="title"
      placeholder="Название карточки"
      aria-label="Название новой карточки"
      @keydown.enter.prevent="submit"
      @keydown.escape.prevent="cancel"
    />
    <div class="mt-2 flex items-center justify-between">
      <span class="text-[10px] text-muted-foreground">Enter — создать · Esc — отмена</span>
      <AppButton size="sm" :loading="props.pending" :disabled="!title.trim()" @click="submit">Добавить</AppButton>
    </div>
  </div>
  <AppButton v-else variant="ghost" size="sm" class="w-full justify-start text-muted-foreground" :disabled="props.disabled" @click="activate">
    <Plus class="size-3.5" /> Добавить карточку
  </AppButton>
</template>
