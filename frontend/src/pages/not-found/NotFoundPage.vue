<script setup lang="ts">
import { RouterLink } from "vue-router";
import { Compass } from "@lucide/vue";
import { env } from "@/shared/config/env";
</script>

<template>
  <main class="flex min-h-screen items-center justify-center p-6">
    <div class="text-center">
      <Compass class="mx-auto size-10 text-muted-foreground" />
      <h1 class="mt-4 text-2xl font-semibold">Страница не найдена</h1>
      <p class="mt-2 text-sm text-muted-foreground">Проверьте адрес или вернитесь к проектам.</p>
      <RouterLink :to="`/${env.VITE_WORKSPACE_SLUG}/projects`" class="mt-5 inline-block text-sm font-medium text-primary hover:underline">
        Открыть проекты
      </RouterLink>
    </div>
  </main>
</template>
