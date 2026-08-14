<script setup lang="ts">
import { ref } from "vue";
import { Archive, LockKeyhole } from "@lucide/vue";
import { toast } from "vue-sonner";

import type { Agent, CreateAgentInput } from "@/entities/agent";
import { getErrorMessage } from "@/shared/api/api-error";
import { AppBadge, AppButton, AppDialog, AppToggle } from "@/shared/ui";

import AgentConfigForm from "./AgentConfigForm.vue";
import { useAgentMutations } from "./use-agent-mutations";

const props = defineProps<{ workspaceSlug: string; projectId: string; agent: Agent; readOnly?: boolean }>();
const emit = defineEmits<{ archived: [] }>();
const mutations = useAgentMutations(() => props.workspaceSlug, () => props.projectId);
const archiveOpen = ref(false);

async function save(input: CreateAgentInput): Promise<void> {
  try {
    await mutations.update.mutateAsync({ agent: props.agent, input });
    toast.success("Настройки ассистента сохранены");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

async function toggleEnabled(enabled: boolean): Promise<void> {
  try {
    await mutations.setEnabled.mutateAsync({ agent: props.agent, enabled });
    toast.success(enabled ? "Ассистент включён" : "Ассистент отключён");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}

async function archive(): Promise<void> {
  try {
    await mutations.archive.mutateAsync(props.agent);
    archiveOpen.value = false;
    toast.success("Ассистент перемещён в архив");
    emit("archived");
  } catch (error) {
    toast.error(getErrorMessage(error));
  }
}
</script>

<template>
  <div class="space-y-6">
    <section class="rounded-xl border border-border bg-card p-5 sm:p-6">
      <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="font-semibold">Конфигурация</h2>
          <p class="mt-1 text-sm text-muted-foreground">Модель, инструкции, память и ограничения одного запуска.</p>
        </div>
        <AppBadge :variant="props.agent.kind === 'coordinator' ? 'default' : 'secondary'">
          {{ props.agent.kind === "coordinator" ? "Координатор" : "Ассистент" }}
        </AppBadge>
      </div>
      <AgentConfigForm
        :agent="props.agent"
        :disabled="props.readOnly || props.agent.status === 'archived'"
        :pending="mutations.update.isPending.value"
        @submit="save"
      />
    </section>

    <section class="rounded-xl border border-border bg-card p-5 sm:p-6">
      <h2 class="font-semibold">Доступность</h2>
      <div v-if="props.agent.kind === 'coordinator'" class="mt-4 flex items-start gap-3 rounded-lg bg-muted p-4">
        <LockKeyhole class="mt-0.5 size-4 shrink-0 text-primary" />
        <div>
          <p class="text-sm font-medium">Координатор всегда активен</p>
          <p class="mt-1 text-xs leading-5 text-muted-foreground">Обязательный task-management MCP, project constraints и политики безопасности изменить или отключить нельзя.</p>
        </div>
      </div>
      <AppToggle
        v-else
        :model-value="props.agent.status === 'active'"
        label="Ассистент включён"
        description="Отключённый ассистент сохраняет настройки, но координатор не делегирует ему работу."
        :disabled="props.readOnly || props.agent.status === 'archived' || mutations.setEnabled.isPending.value"
        @update:model-value="toggleEnabled"
      />
    </section>

    <section v-if="props.agent.kind === 'worker'" class="rounded-xl border border-destructive/25 bg-card p-5 sm:p-6">
      <h2 class="font-semibold text-destructive">Опасная зона</h2>
      <div class="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-medium">Архивировать ассистента</p>
          <p class="mt-1 text-xs leading-5 text-muted-foreground">Ассистент исчезнет из выбора для новых запусков. Его история сохранится.</p>
        </div>
        <AppButton
          variant="destructive"
          :disabled="props.readOnly || props.agent.status === 'archived'"
          @click="archiveOpen = true"
        >
          <Archive class="size-4" /> Архивировать
        </AppButton>
      </div>
    </section>
  </div>

  <AppDialog v-model:open="archiveOpen" title="Архивировать ассистента?" description="Координатор больше не сможет выбирать его для новых делегаций." width="sm">
    <p class="text-sm text-muted-foreground">Настройки и история запусков сохранятся, но вернуть ассистента из архива в этом интерфейсе пока нельзя.</p>
    <div class="mt-5 flex justify-end gap-2">
      <AppButton variant="outline" @click="archiveOpen = false">Отмена</AppButton>
      <AppButton variant="destructive" :loading="mutations.archive.isPending.value" @click="archive">
        <Archive class="size-4" /> Архивировать
      </AppButton>
    </div>
  </AppDialog>
</template>
