<script setup lang="ts">
import { MessageSquareText, Play, ShieldCheck } from "@lucide/vue";

import { AppEmptyState } from "@/shared/ui";
</script>

<template>
  <div class="min-h-screen bg-background">
    <header class="flex min-h-16 items-center gap-3 border-b border-border bg-card px-4 py-3 sm:px-7">
      <MessageSquareText class="size-4 text-primary" />
      <div>
        <h1 class="text-base font-semibold">Сессии</h1>
        <p class="text-xs text-muted-foreground">Диалоги и запуски агентов проекта</p>
      </div>
    </header>

    <main class="mx-auto max-w-4xl p-4 sm:p-7">
      <AppEmptyState title="Сессий пока нет" description="Здесь появятся ручные диалоги и системные сессии, созданные правилами автоматизации.">
        <template #icon><MessageSquareText class="size-5" /></template>
      </AppEmptyState>

      <div class="mt-5 grid gap-4 sm:grid-cols-2">
        <section class="rounded-xl border border-border bg-card p-5">
          <Play class="size-4 text-primary" />
          <h2 class="mt-3 text-sm font-semibold">Один активный запуск</h2>
          <p class="mt-1 text-xs leading-5 text-muted-foreground">Внутри одной сессии выполняется не более одного Run. Новый независимый запрос требует отдельной сессии.</p>
        </section>
        <section class="rounded-xl border border-border bg-card p-5">
          <ShieldCheck class="size-4 text-primary" />
          <h2 class="mt-3 text-sm font-semibold">Действия под контролем</h2>
          <p class="mt-1 text-xs leading-5 text-muted-foreground">Изменяющие и рискованные действия будут ожидать подтверждения согласно политике проекта.</p>
        </section>
      </div>
    </main>
  </div>
</template>
