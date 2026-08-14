<script setup lang="ts">
import { watch } from "vue";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";

import type { Epic } from "@/entities/epic";
import { AppButton, AppDialog, AppFormField, AppInput, AppTextarea } from "@/shared/ui";

import { epicSchema, type EpicFormValues } from "./epic-schema";

const open = defineModel<boolean>("open", { default: false });
const props = withDefaults(defineProps<{ epic?: Epic; pending?: boolean }>(), { epic: undefined, pending: false });
const emit = defineEmits<{ submit: [values: EpicFormValues] }>();

const { errors, defineField, handleSubmit, resetForm } = useForm<EpicFormValues>({
  validationSchema: toTypedSchema(epicSchema),
});
const [name, nameAttrs] = defineField("name");
const [description, descriptionAttrs] = defineField("description");
const [color, colorAttrs] = defineField("color");
const [startDate, startDateAttrs] = defineField("startDate");
const [targetDate, targetDateAttrs] = defineField("targetDate");
const submit = handleSubmit((values) => emit("submit", values));

watch(
  open,
  (value) => {
    if (!value) return;
    resetForm({
      values: {
        name: props.epic?.name ?? "",
        description: props.epic?.description ?? "",
        color: props.epic?.color ?? "#8b5cf6",
        startDate: props.epic?.startDate ?? null,
        targetDate: props.epic?.targetDate ?? null,
      },
    });
  },
  { immediate: true },
);
</script>

<template>
  <AppDialog
    v-model:open="open"
    :title="props.epic ? 'Редактировать эпик' : 'Новый эпик'"
    description="Эпик объединяет карточки и показывает прогресс по завершённым состояниям."
  >
    <form class="space-y-4" @submit="submit">
      <AppFormField label="Название" required :error="errors.name">
        <AppInput v-model="name" v-bind="nameAttrs" placeholder="Например, Первый запуск пользователя" />
      </AppFormField>
      <AppFormField label="Описание" :error="errors.description">
        <AppTextarea v-model="description" v-bind="descriptionAttrs" :rows="3" placeholder="Цель и границы эпика" />
      </AppFormField>
      <div class="grid gap-4 sm:grid-cols-[120px_1fr_1fr]">
        <AppFormField label="Цвет" :error="errors.color">
          <div class="flex h-9 items-center gap-2 rounded-md border border-input bg-card px-2">
            <input v-model="color" v-bind="colorAttrs" type="color" class="size-6 rounded border-0 bg-transparent p-0" />
            <span class="text-xs text-muted-foreground">{{ color }}</span>
          </div>
        </AppFormField>
        <AppFormField label="Начало" :error="errors.startDate">
          <AppInput v-model="startDate" v-bind="startDateAttrs" type="date" />
        </AppFormField>
        <AppFormField label="Завершение" :error="errors.targetDate">
          <AppInput v-model="targetDate" v-bind="targetDateAttrs" type="date" />
        </AppFormField>
      </div>
      <div class="flex justify-end gap-2 pt-2">
        <AppButton variant="outline" @click="open = false">Отмена</AppButton>
        <AppButton type="submit" :loading="props.pending">{{ props.epic ? "Сохранить" : "Создать эпик" }}</AppButton>
      </div>
    </form>
  </AppDialog>
</template>
