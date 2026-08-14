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
const props = withDefaults(
  defineProps<{ title: string; description?: string; width?: "sm" | "md" | "lg" }>(),
  { description: "", width: "md" },
);

const widths = { sm: "max-w-md", md: "max-w-xl", lg: "max-w-3xl" };
</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-50 bg-slate-950/45 backdrop-blur-[2px] data-[state=open]:animate-in data-[state=closed]:animate-out" />
      <DialogContent
        :class="['surface-shadow fixed left-1/2 top-1/2 z-50 max-h-[88vh] w-[calc(100%-2rem)] -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-xl border border-border bg-card p-0', widths[props.width]]"
      >
        <header class="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
          <div>
            <DialogTitle class="text-base font-semibold">{{ props.title }}</DialogTitle>
            <DialogDescription v-if="props.description" class="mt-1 text-sm text-muted-foreground">
              {{ props.description }}
            </DialogDescription>
          </div>
          <DialogClose class="focus-ring flex size-8 shrink-0 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground" aria-label="Закрыть">
            <X class="size-4" />
          </DialogClose>
        </header>
        <div class="p-5"><slot /></div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
