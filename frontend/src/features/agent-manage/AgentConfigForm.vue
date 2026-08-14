<script setup lang="ts">
import { watch } from "vue";
import { Save } from "@lucide/vue";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";

import type { Agent, CreateAgentInput } from "@/entities/agent";
import { AppButton, AppFormField, AppInput, AppSelect, AppTextarea, type SelectOption } from "@/shared/ui";

import { agentSchema, defaultAgentValues, toAgentInput, valuesForAgent, type AgentFormValues } from "./agent-schema";

const props = withDefaults(
  defineProps<{ agent?: Agent; disabled?: boolean; pending?: boolean; submitLabel?: string }>(),
  { agent: undefined, disabled: false, pending: false, submitLabel: "Сохранить" },
);
const emit = defineEmits<{ submit: [input: CreateAgentInput] }>();

const modelOptions: SelectOption[] = [
  { value: "qwen3:14b", label: "Qwen 3 · 14B" },
  { value: "qwen3:32b", label: "Qwen 3 · 32B" },
  { value: "llama3.3:70b", label: "Llama 3.3 · 70B" },
];
const memoryOptions: SelectOption[] = [
  { value: "project", label: "Проект и текущая сессия" },
  { value: "session", label: "Только текущая сессия" },
  { value: "none", label: "Не использовать память" },
];
const limitOptions: SelectOption[] = [
  { value: "10", label: "10 шагов" },
  { value: "25", label: "25 шагов" },
  { value: "50", label: "50 шагов" },
];
const approvalOptions: SelectOption[] = [
  { value: "project", label: "По правилам проекта" },
  { value: "always", label: "Для каждого изменяющего действия" },
];

const { errors, defineField, handleSubmit, resetForm } = useForm<AgentFormValues>({
  validationSchema: toTypedSchema(agentSchema),
  initialValues: props.agent ? valuesForAgent(props.agent) : defaultAgentValues,
});
const [name, nameAttrs] = defineField("name");
const [description, descriptionAttrs] = defineField("description");
const [instructions, instructionsAttrs] = defineField("instructions");
const [model] = defineField("model");
const [memoryPolicy] = defineField("memoryPolicy");
const [maxStepsPerRun] = defineField("maxStepsPerRun");
const [approvalMode] = defineField("approvalMode");

watch(
  () => props.agent,
  (agent) => resetForm({ values: agent ? valuesForAgent(agent) : defaultAgentValues }),
);

const submit = handleSubmit((values) => emit("submit", toAgentInput(values)));
</script>

<template>
  <form class="space-y-5" @submit="submit">
    <div class="grid gap-4 sm:grid-cols-2">
      <AppFormField label="Название" for="agent-name" required :error="errors.name">
        <AppInput id="agent-name" v-model="name" v-bind="nameAttrs" placeholder="Например, Аналитик рисков" :disabled="props.disabled" autofocus />
      </AppFormField>
      <AppFormField label="Модель" for="agent-model" required :error="errors.model">
        <AppSelect id="agent-model" v-model="model" :options="modelOptions" :disabled="props.disabled" />
      </AppFormField>
    </div>

    <AppFormField label="Краткое описание" for="agent-description" :error="errors.description" hint="Пользователи увидят его в списке ассистентов.">
      <AppInput id="agent-description" v-model="description" v-bind="descriptionAttrs" placeholder="Чем помогает этот ассистент" :disabled="props.disabled" />
    </AppFormField>

    <AppFormField label="Инструкции" for="agent-instructions" required :error="errors.instructions" hint="Опишите роль, ожидаемый результат и ограничения. Системные политики проекта применяются отдельно.">
      <AppTextarea id="agent-instructions" v-model="instructions" v-bind="instructionsAttrs" :rows="8" :disabled="props.disabled" placeholder="Анализируй риски проекта, проверяй сроки и формируй рекомендации…" />
    </AppFormField>

    <div class="grid gap-4 sm:grid-cols-3">
      <AppFormField label="Память" for="agent-memory" :error="errors.memoryPolicy">
        <AppSelect id="agent-memory" v-model="memoryPolicy" :options="memoryOptions" :disabled="props.disabled" />
      </AppFormField>
      <AppFormField label="Лимит запуска" for="agent-limit" :error="errors.maxStepsPerRun">
        <AppSelect id="agent-limit" v-model="maxStepsPerRun" :options="limitOptions" :disabled="props.disabled" />
      </AppFormField>
      <AppFormField label="Подтверждения" for="agent-approval" :error="errors.approvalMode">
        <AppSelect id="agent-approval" v-model="approvalMode" :options="approvalOptions" :disabled="props.disabled" />
      </AppFormField>
    </div>

    <div v-if="!props.disabled" class="flex justify-end border-t border-border pt-5">
      <AppButton type="submit" :loading="props.pending"><Save class="size-4" /> {{ props.submitLabel }}</AppButton>
    </div>
  </form>
</template>
