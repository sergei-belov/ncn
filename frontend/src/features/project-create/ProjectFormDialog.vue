<script setup lang="ts">
import { watch } from "vue";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import { toast } from "vue-sonner";

import { ApiError } from "@/shared/api/api-error";
import { AppButton, AppDialog, AppFormField, AppInput, AppTextarea } from "@/shared/ui";

import { projectSchema, type ProjectFormValues } from "./project-schema";

const open = defineModel<boolean>("open", { default: false });
const props = defineProps<{ pending?: boolean }>();
const emit = defineEmits<{ submit: [values: ProjectFormValues] }>();

const { errors, defineField, handleSubmit, resetForm, setErrors } = useForm<ProjectFormValues>({
  validationSchema: toTypedSchema(projectSchema),
  initialValues: { name: "", identifier: "", description: "", access: "workspace" },
});

const [name, nameAttrs] = defineField("name");
const [identifier, identifierAttrs] = defineField("identifier");
const [description, descriptionAttrs] = defineField("description");
const [access, accessAttrs] = defineField("access");

const submit = handleSubmit((values) => emit("submit", values));

watch(open, (isOpen) => {
  if (isOpen) resetForm({ values: { name: "", identifier: "", description: "", access: "workspace" } });
});

function applyApiError(error: unknown): void {
  if (error instanceof ApiError && Object.keys(error.fieldErrors).length) {
    setErrors(Object.fromEntries(Object.entries(error.fieldErrors).map(([field, messages]) => [field, messages[0] ?? "Ошибка"])));
  } else {
    toast.error(error instanceof Error ? error.message : "Не удалось создать проект");
  }
}

defineExpose({ applyApiError });
</script>

<template>
  <AppDialog v-model:open="open" title="Новый проект" description="Будут созданы четыре стандартных состояния Kanban.">
    <form class="space-y-4" @submit="submit">
      <AppFormField label="Название" required :error="errors.name">
        <AppInput v-model="name" v-bind="nameAttrs" placeholder="Например, Кабинет клиента" autofocus />
      </AppFormField>
      <AppFormField label="Идентификатор" required :error="errors.identifier" hint="2–10 латинских букв или цифр. Используется в WEB-42.">
        <AppInput
          v-model="identifier"
          v-bind="identifierAttrs"
          placeholder="WEB"
          class="uppercase"
          @input="identifier = identifier.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 10)"
        />
      </AppFormField>
      <AppFormField label="Описание" :error="errors.description">
        <AppTextarea v-model="description" v-bind="descriptionAttrs" placeholder="Коротко опишите цель проекта" :rows="3" />
      </AppFormField>
      <AppFormField label="Доступ" :error="errors.access">
        <select v-model="access" v-bind="accessAttrs" class="focus-ring h-9 w-full rounded-md border border-input bg-card px-3 text-sm">
          <option value="workspace">Весь workspace</option>
          <option value="private">Только участники проекта</option>
        </select>
      </AppFormField>
      <div class="flex justify-end gap-2 pt-2">
        <AppButton variant="outline" @click="open = false">Отмена</AppButton>
        <AppButton type="submit" :loading="props.pending">Создать проект</AppButton>
      </div>
    </form>
  </AppDialog>
</template>
