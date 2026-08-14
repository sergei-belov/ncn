<script setup lang="ts">
import { watch } from "vue";
import { Bold, List, ListOrdered } from "@lucide/vue";
import StarterKit from "@tiptap/starter-kit";
import { EditorContent, useEditor } from "@tiptap/vue-3";

import AppButton from "./AppButton.vue";

const model = defineModel<string>({ default: "" });
const props = withDefaults(defineProps<{ disabled?: boolean }>(), { disabled: false });

const editor = useEditor({
  content: model.value,
  editable: !props.disabled,
  extensions: [StarterKit],
  editorProps: {
    attributes: { class: "prose prose-sm max-w-none" },
  },
  onUpdate: ({ editor: instance }) => {
    model.value = instance.isEmpty ? "" : instance.getHTML();
  },
});

watch(
  () => model.value,
  (value) => {
    if (editor.value && editor.value.getHTML() !== value) editor.value.commands.setContent(value || "", { emitUpdate: false });
  },
);

watch(
  () => props.disabled,
  (disabled) => editor.value?.setEditable(!disabled),
);
</script>

<template>
  <div class="overflow-hidden rounded-lg border border-input bg-card">
    <div v-if="!props.disabled" class="flex items-center gap-1 border-b border-border bg-muted/50 p-1.5">
      <AppButton
        size="icon"
        variant="ghost"
        class="size-7"
        :class="editor?.isActive('bold') ? 'bg-accent text-accent-foreground' : ''"
        aria-label="Жирный"
        @click="editor?.chain().focus().toggleBold().run()"
      >
        <Bold class="size-3.5" />
      </AppButton>
      <AppButton
        size="icon"
        variant="ghost"
        class="size-7"
        :class="editor?.isActive('bulletList') ? 'bg-accent text-accent-foreground' : ''"
        aria-label="Маркированный список"
        @click="editor?.chain().focus().toggleBulletList().run()"
      >
        <List class="size-3.5" />
      </AppButton>
      <AppButton
        size="icon"
        variant="ghost"
        class="size-7"
        :class="editor?.isActive('orderedList') ? 'bg-accent text-accent-foreground' : ''"
        aria-label="Нумерованный список"
        @click="editor?.chain().focus().toggleOrderedList().run()"
      >
        <ListOrdered class="size-3.5" />
      </AppButton>
    </div>
    <EditorContent :editor="editor" class="editor-content text-sm" />
  </div>
</template>
