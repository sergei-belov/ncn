import { defineComponent } from "vue";
import { QueryClient, VueQueryPlugin } from "@tanstack/vue-query";
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import { agentApiKey, agentKeys, type Agent, type AgentApi } from "@/entities/agent";
import { useAgentMutations } from "@/features/agent-manage";

const worker: Agent = {
  id: "agent-risk",
  projectId: "project-web",
  kind: "worker",
  name: "Аналитик рисков",
  description: "",
  instructions: "Анализируй риски проекта и возвращай рекомендации.",
  model: "qwen3:14b",
  memoryPolicy: "project",
  maxStepsPerRun: 25,
  approvalMode: "project",
  status: "active",
  systemToolNames: [],
  createdAt: "2026-08-01T00:00:00.000Z",
  updatedAt: "2026-08-01T00:00:00.000Z",
  version: 1,
};

describe("agent availability mutation", () => {
  it("updates detail and list caches immediately and rolls both back on failure", async () => {
    let rejectRequest: (reason: Error) => void = () => undefined;
    const api: AgentApi = {
      listAgents: vi.fn(),
      getAgent: vi.fn(),
      createAgent: vi.fn(),
      updateAgent: vi.fn(),
      setAgentEnabled: vi.fn(
        () =>
          new Promise<Agent>((_resolve, reject) => {
            rejectRequest = reject;
          }),
      ),
      archiveAgent: vi.fn(),
    };
    const queryClient = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
    const detailKey = agentKeys.detail("demo", "project-web", worker.id);
    const listKey = agentKeys.list("demo", "project-web");
    queryClient.setQueryData(detailKey, worker);
    queryClient.setQueryData(listKey, [worker]);

    let mutations: ReturnType<typeof useAgentMutations> | undefined;
    const wrapper = mount(
      defineComponent({
        setup() {
          mutations = useAgentMutations("demo", "project-web");
          return () => null;
        },
      }),
      {
        global: {
          plugins: [[VueQueryPlugin, { queryClient }]],
          provide: { [agentApiKey as symbol]: api },
        },
      },
    );

    const request = mutations!.setEnabled.mutateAsync({ agent: worker, enabled: false });
    await vi.waitFor(() => {
      expect(queryClient.getQueryData<Agent>(detailKey)?.status).toBe("disabled");
      expect(queryClient.getQueryData<Agent[]>(listKey)?.[0]?.status).toBe("disabled");
    });

    rejectRequest(new Error("Network unavailable"));
    await expect(request).rejects.toThrow("Network unavailable");
    expect(queryClient.getQueryData<Agent>(detailKey)?.status).toBe("active");
    expect(queryClient.getQueryData<Agent[]>(listKey)?.[0]?.status).toBe("active");

    wrapper.unmount();
    queryClient.clear();
  });
});
