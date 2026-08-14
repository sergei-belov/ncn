<script setup lang="ts">
import { computed, ref, watch } from "vue";

import {
  serviceRoleFitsProjectRole,
  type ProjectAccessRole,
  type ProjectMembership,
  type ServiceRestriction,
} from "@/entities/authz";
import { ApiError } from "@/shared/api/api-error";
import { AppButton, AppDialog, AppFormField, AppInput, AppSelect, type SelectOption } from "@/shared/ui";

import { serviceRestrictionFormSchema } from "./access-schema";

const open = defineModel<boolean>("open", { default: false });
const props = withDefaults(
  defineProps<{
    membership?: ProjectMembership;
    restriction?: ServiceRestriction;
    pending?: boolean;
    error?: unknown;
  }>(),
  { membership: undefined, restriction: undefined, pending: false, error: undefined },
);
const emit = defineEmits<{
  submit: [values: { serviceId: string; role: ProjectAccessRole; restriction?: ServiceRestriction }];
  remove: [restriction: ServiceRestriction];
}>();

const serviceId = ref("");
const role = ref<string | null>(null);
const fieldErrors = ref<Record<string, string>>({});
const errorMessage = computed(() => (props.error instanceof Error ? props.error.message : ""));
const requestId = computed(() => (props.error instanceof ApiError ? props.error.requestId : ""));
const roleOptions = computed<SelectOption[]>(() => {
  const projectRole = props.membership?.role ?? "viewer";
  return (["admin", "member", "viewer"] as const)
    .filter((candidate) => serviceRoleFitsProjectRole(candidate, projectRole))
    .map((value) => ({
      value,
      label: value === "admin" ? "Администратор" : value === "member" ? "Участник" : "Наблюдатель",
    }));
});

watch(
  [open, () => props.restriction, () => props.membership],
  ([isOpen]) => {
    if (!isOpen) return;
    serviceId.value = props.restriction?.serviceId ?? "";
    role.value = props.restriction?.role ?? props.membership?.role ?? "viewer";
    fieldErrors.value = {};
  },
  { immediate: true },
);

function submit(): void {
  const result = serviceRestrictionFormSchema.safeParse({ serviceId: serviceId.value, role: role.value });
  if (!result.success) {
    fieldErrors.value = Object.fromEntries(result.error.issues.map((issue) => [String(issue.path[0]), issue.message]));
    return;
  }
  fieldErrors.value = {};
  emit("submit", { ...result.data, restriction: props.restriction });
}
</script>

<template>
  <AppDialog
    v-model:open="open"
    :title="restriction ? 'Изменить доступ к сервису' : 'Ограничить доступ к сервису'"
    description="Ограничение может только сузить роль проекта. Без ограничения роль наследуется."
    width="sm"
  >
    <form class="space-y-4" @submit.prevent="submit">
      <div v-if="errorMessage" class="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive" role="alert">
        <p>{{ errorMessage }}</p>
        <p v-if="requestId" class="mt-1 text-xs">Код обращения: <code>{{ requestId }}</code></p>
      </div>
      <AppFormField
        label="Идентификатор сервиса"
        required
        :error="fieldErrors.serviceId"
        hint="Используется стабильный ID; каталог сервисов пока не подключён."
      >
        <AppInput v-model="serviceId" :disabled="Boolean(restriction)" placeholder="ncn-agents" autocomplete="off" />
      </AppFormField>
      <AppFormField label="Роль сервиса" required :error="fieldErrors.role">
        <AppSelect v-model="role" :options="roleOptions" />
      </AppFormField>
      <p class="rounded-lg bg-muted/60 px-3 py-2 text-xs leading-5 text-muted-foreground">
        Роль проекта: <strong class="text-foreground">{{ membership?.role }}</strong>.
        Удаление ограничения восстановит эту наследуемую роль.
      </p>
      <div class="flex flex-col-reverse gap-2 pt-2 sm:flex-row sm:justify-between">
        <AppButton
          v-if="restriction"
          variant="destructive"
          :loading="pending"
          @click="emit('remove', restriction)"
        >
          Восстановить наследование
        </AppButton>
        <span v-else />
        <div class="flex justify-end gap-2">
          <AppButton variant="outline" @click="open = false">Отмена</AppButton>
          <AppButton type="submit" :loading="pending">Сохранить</AppButton>
        </div>
      </div>
    </form>
  </AppDialog>
</template>

