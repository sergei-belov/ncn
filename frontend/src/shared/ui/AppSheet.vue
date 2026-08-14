<script setup lang="ts">
import { X } from "@lucide/vue";
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from "reka-ui";

const open = defineModel<boolean>("open", { default: false });
const props = withDefaults(defineProps<{ title: string; description?: string }>(), { description: "" });
</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-50 bg-slate-950/35 backdrop-blur-[1px]" />
      <DialogContent class="surface-shadow fixed inset-y-0 right-0 z-50 flex w-full flex-col border-l border-border bg-card sm:max-w-2xl">
        <header class="flex min-h-16 items-start justify-between gap-4 border-b border-border px-5 py-4">
          <div class="min-w-0">
            <DialogTitle class="truncate text-base font-semibold">{{ props.title }}</DialogTitle>
            <DialogDescription v-if="props.description" class="mt-0.5 truncate text-xs text-muted-foreground">
              {{ props.description }}
            </DialogDescription>
          </div>
          <DialogClose class="focus-ring flex size-8 shrink-0 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground" aria-label="Закрыть">
            <X class="size-4" />
          </DialogClose>
        </header>
        <div class="min-h-0 flex-1 overflow-y-auto"><slot /></div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
