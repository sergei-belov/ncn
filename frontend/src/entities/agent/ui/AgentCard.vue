<script setup lang="ts">
import { Bot, BrainCircuit, LockKeyhole, Settings2 } from "@lucide/vue";

import { AppBadge, AppButton } from "@/shared/ui";

import type { Agent } from "../model/types";

const props = defineProps<{ agent: Agent; canManage?: boolean }>();
const emit = defineEmits<{ open: [] }>();

const statusLabels = {
  active: "Активен",
  disabled: "Отключён",
  archived: "В архиве",
} as const;
</script>

<template>
  <article class="flex h-full flex-col rounded-xl border border-border bg-card p-5 surface-shadow">
    <div class="flex items-start gap-3">
      <div class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
        <BrainCircuit v-if="props.agent.kind === 'coordinator'" class="size-5" />
        <Bot v-else class="size-5" />
      </div>
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <h2 class="truncate font-semibold">{{ props.agent.name }}</h2>
          <AppBadge :variant="props.agent.kind === 'coordinator' ? 'default' : 'secondary'">
            {{ props.agent.kind === "coordinator" ? "Координатор" : "Ассистент" }}
          </AppBadge>
          <AppBadge :variant="props.agent.status === 'active' ? 'outline' : 'secondary'">
            {{ statusLabels[props.agent.status] }}
          </AppBadge>
        </div>
        <p class="mt-1 line-clamp-2 text-sm leading-5 text-muted-foreground">
          {{ props.agent.description || "Специализированный помощник проекта" }}
        </p>
      </div>
    </div>

    <dl class="mt-5 grid grid-cols-2 gap-3 border-t border-border pt-4 text-xs">
      <div>
        <dt class="text-muted-foreground">Модель</dt>
        <dd class="mt-1 truncate font-medium">{{ props.agent.model }}</dd>
      </div>
      <div>
        <dt class="text-muted-foreground">Лимит запуска</dt>
        <dd class="mt-1 font-medium">{{ props.agent.maxStepsPerRun }} шагов</dd>
      </div>
    </dl>

    <div class="mt-auto flex items-center justify-between gap-3 pt-5">
      <span v-if="props.agent.kind === 'coordinator'" class="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
        <LockKeyhole class="size-3.5" /> Системная роль
      </span>
      <span v-else class="text-xs text-muted-foreground">Память: {{ props.agent.memoryPolicy === "project" ? "проект" : props.agent.memoryPolicy === "session" ? "сессия" : "выключена" }}</span>
      <AppButton variant="outline" size="sm" @click="emit('open')">
        <Settings2 class="size-3.5" /> {{ props.canManage ? "Настроить" : "Просмотреть" }}
      </AppButton>
    </div>
  </article>
</template>
