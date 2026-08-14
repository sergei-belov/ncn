import { createRouter, createWebHistory } from "vue-router";

import { routes } from "./routes";

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    if (to.path === from.path) return false;
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  if (typeof to.params.workspaceSlug === "string" && !to.params.workspaceSlug.trim()) return { path: "/" };
  return true;
});
