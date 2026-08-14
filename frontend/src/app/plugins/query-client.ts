import { QueryClient, VueQueryPlugin, type VueQueryPluginOptions } from "@tanstack/vue-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        const status = typeof error === "object" && error && "status" in error ? Number(error.status) : 0;
        return status >= 400 && status < 500 ? false : failureCount < 2;
      },
      refetchOnReconnect: true,
    },
    mutations: { retry: false },
  },
});

export const vueQueryOptions: VueQueryPluginOptions = { queryClient };
export { VueQueryPlugin };
