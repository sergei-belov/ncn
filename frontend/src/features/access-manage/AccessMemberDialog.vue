<script setup lang="ts">
import { computed, ref, watch } from "vue";

import type {
  AccessMembership,
  ProjectAccessRole,
  WorkspaceRole,
} from "@/entities/authz";
import { ApiError } from "@/shared/api/api-error";
import { AppButton, AppDialog, AppFormField, AppInput, AppSelect, type SelectOption } from "@/shared/ui";

import {
  projectMembershipFormSchema,
  workspaceMembershipFormSchema,
} from "./access-schema";

const open = defineModel<boolean>("open", { default: false });
const props = withDefaults(
  defineProps<{
    scope: "workspace" | "project";
    membership?: AccessMembership;
    pending?: boolean;
    error?: unknown;
  }>(),
  { membership: undefined, pending: false, error: undefined },
);
const emit = defineEmits<{
  submit: [values: { userId: string; role: WorkspaceRole | ProjectAccessRole }];
}>();

const userId = ref("");
const role = ref<string | null>(null);
const fieldErrors = ref<Record<string, string>>({});
const isEditing = computed(() => Boolean(props.membership));
const apiError = computed(() => (props.error instanceof ApiError ? props.error : undefined));
const errorMessage = computed(() => {
  if (!props.error) return "";
  return props.error instanceof Error ? props.error.message : "Не удалось сохранить доступ";
});

const roleOptions = computed<SelectOption[]>(() => {
  if (props.scope === "project") {
    return [
      { value: "admin", label: "Администратор" },
      { value: "member", label: "Участник" },
      { value: "viewer", label: "Наблюдатель" },
    ];
  }
  return [
    { value: "admin", label: "Администратор" },
    { value: "member", label: "Участник" },
  ];
});

watch(
  [open, () => props.membership],
  ([isOpen]) => {
    if (!isOpen) return;
    userId.value = props.membership?.userId ?? "";
    role.value = props.membership?.role ?? (props.scope === "workspace" ? "member" : "viewer");
    fieldErrors.value = {};
  },
  { immediate: true },
);

watch(
  () => props.error,
  (error) => {
    if (error instanceof ApiError) {
      fieldErrors.value = Object.fromEntries(
        Object.entries(error.fieldErrors).map(([field, messages]) => [field.replace("user_id", "userId"), messages[0] ?? "Ошибка"]),
      );
    }
  },
);

function submit(): void {
  const schema = props.scope === "workspace" ? workspaceMembershipFormSchema : projectMembershipFormSchema;
  const result = schema.safeParse({ userId: userId.value, role: role.value });
  if (!result.success) {
    fieldErrors.value = Object.fromEntries(result.error.issues.map((issue) => [String(issue.path[0]), issue.message]));
    return;
  }
  fieldErrors.value = {};
  emit("submit", result.data);
}
</script>

<template>
  <AppDialog
    v-model:open="open"
    :title="isEditing ? 'Изменить доступ' : scope === 'workspace' ? 'Добавить доступ к workspace' : 'Добавить доступ к проекту'"
    :description="isEditing ? 'Проверьте актуальную роль перед сохранением.' : 'Доступ назначается существующему активному пользователю NCN.'"
    width="sm"
  >
    <form class="space-y-4" @submit.prevent="submit">
      <div
        v-if="errorMessage"
        class="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive"
        role="alert"
      >
        <p>{{ errorMessage }}</p>
        <p v-if="apiError" class="mt-1 text-xs">Код обращения: <code>{{ apiError.requestId }}</code></p>
      </div>

      <AppFormField
        label="UUID пользователя"
        required
        :error="fieldErrors.userId"
        hint="Поиск по каталогу пользователей не включён: укажите известный UUID."
      >
        <AppInput
          v-model="userId"
          :disabled="isEditing"
          placeholder="Например, member-maria"
          autocomplete="off"
          autofocus
        />
      </AppFormField>

      <div v-if="membership" class="rounded-lg bg-muted/60 px-3 py-2 text-sm">
        <p class="font-medium">{{ membership.user.name }}</p>
        <p class="text-xs text-muted-foreground">{{ membership.user.email }}</p>
      </div>

      <AppFormField
        :label="scope === 'workspace' ? 'Роль workspace' : 'Роль проекта'"
        required
        :error="fieldErrors.role"
      >
        <AppSelect v-model="role" :options="roleOptions" />
      </AppFormField>

      <p v-if="scope === 'workspace'" class="text-xs leading-5 text-muted-foreground">
        Передача роли владельца выполняется отдельной защищённой операцией и недоступна в этом диалоге.
      </p>

      <div class="flex justify-end gap-2 pt-2">
        <AppButton variant="outline" @click="open = false">Отмена</AppButton>
        <AppButton type="submit" :loading="pending">{{ isEditing ? "Сохранить" : "Добавить" }}</AppButton>
      </div>
    </form>
  </AppDialog>
</template>
