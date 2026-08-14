<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { Check, Search } from "@lucide/vue";

import type { Epic } from "@/entities/epic";
import type { WorkItem } from "@/entities/work-item";
import type { UUID } from "@/shared/lib/domain-primitives";
import { AppBadge, AppButton, AppDialog, AppInput } from "@/shared/ui";

const open = defineModel<boolean>("open", { default: false });
const props = defineProps<{
  epic: Epic;
  workItems: WorkItem[];
  epicMap: Record<UUID, Epic>;
  pending?: boolean;
}>();
const emit = defineEmits<{ submit: [workItemIds: UUID[]] }>();

const search = ref("");
const selected = ref<Set<UUID>>(new Set());
const filtered = computed(() => {
  const value = search.value.trim().toLocaleLowerCase("ru");
  return props.workItems.filter((item) => !value || `${item.identifier} ${item.title}`.toLocaleLowerCase("ru").includes(value));
});

watch(open, (value) => {
  if (value) {
    selected.value = new Set(props.epic.workItemIds);
    search.value = "";
  }
});

function toggle(id: UUID): void {
  const next = new Set(selected.value);
  if (next.has(id)) next.delete(id);
  else next.add(id);
  selected.value = next;
}
</script>

<template>
  <AppDialog v-model:open="open" title="Карточки эпика" description="Карточка может принадлежать только одному эпику." width="lg">
    <div class="relative">
      <Search class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <AppInput v-model="search" class="pl-9" placeholder="Поиск по названию или идентификатору" />
    </div>
    <div class="mt-3 max-h-[430px] space-y-1 overflow-y-auto rounded-lg border border-border p-1">
      <button
        v-for="workItem in filtered"
        :key="workItem.id"
        type="button"
        class="focus-ring flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-left hover:bg-muted"
        @click="toggle(workItem.id)"
      >
        <span
          class="flex size-5 shrink-0 items-center justify-center rounded border"
          :class="selected.has(workItem.id) ? 'border-primary bg-primary text-primary-foreground' : 'border-input bg-card'"
        >
          <Check v-if="selected.has(workItem.id)" class="size-3.5" />
        </span>
        <span class="w-16 shrink-0 text-xs font-medium text-muted-foreground">{{ workItem.identifier }}</span>
        <span class="min-w-0 flex-1 truncate text-sm">{{ workItem.title }}</span>
        <AppBadge v-if="workItem.epicId && workItem.epicId !== props.epic.id" variant="outline" class="max-w-40">
          <span class="truncate">{{ props.epicMap[workItem.epicId]?.name ?? "Другой эпик" }}</span>
        </AppBadge>
      </button>
      <p v-if="filtered.length === 0" class="p-8 text-center text-sm text-muted-foreground">Карточки не найдены.</p>
    </div>
    <div class="mt-4 flex items-center justify-between">
      <span class="text-xs text-muted-foreground">Выбрано: {{ selected.size }}</span>
      <div class="flex gap-2">
        <AppButton variant="outline" @click="open = false">Отмена</AppButton>
        <AppButton :loading="props.pending" @click="emit('submit', [...selected])">Сохранить</AppButton>
      </div>
    </div>
  </AppDialog>
</template>
