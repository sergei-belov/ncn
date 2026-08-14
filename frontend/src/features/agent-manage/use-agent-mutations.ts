import { toValue, type MaybeRefOrGetter } from "vue";
import { useMutation, useQueryClient } from "@tanstack/vue-query";

import {
  agentKeys,
  replaceAgentInList,
  useAgentApi,
  withAgentStatus,
  type Agent,
  type CreateAgentInput,
  type UpdateAgentInput,
} from "@/entities/agent";
import type { UUID } from "@/shared/lib/domain-primitives";

export function useAgentMutations(
  workspaceSlug: MaybeRefOrGetter<string>,
  projectId: MaybeRefOrGetter<UUID>,
) {
  const api = useAgentApi();
  const queryClient = useQueryClient();

  function cacheAgent(agent: Agent): void {
    const workspace = toValue(workspaceSlug);
    const project = toValue(projectId);
    queryClient.setQueryData(agentKeys.detail(workspace, project, agent.id), agent);
    queryClient.setQueryData<Agent[]>(agentKeys.list(workspace, project), (agents) => replaceAgentInList(agents, agent));
  }

  async function saveAgent(agent: Agent): Promise<void> {
    cacheAgent(agent);
    await queryClient.invalidateQueries({ queryKey: agentKeys.all(toValue(workspaceSlug), toValue(projectId)) });
  }

  const create = useMutation({
    mutationFn: (input: CreateAgentInput) => api.createAgent(toValue(workspaceSlug), toValue(projectId), input),
    onSuccess: saveAgent,
  });
  const update = useMutation({
    mutationFn: ({ agent, input }: { agent: Agent; input: UpdateAgentInput }) =>
      api.updateAgent(toValue(workspaceSlug), toValue(projectId), agent.id, input, agent.version),
    onSuccess: saveAgent,
  });
  const setEnabled = useMutation({
    mutationFn: ({ agent, enabled }: { agent: Agent; enabled: boolean }) =>
      api.setAgentEnabled(toValue(workspaceSlug), toValue(projectId), agent.id, enabled, agent.version),
    onMutate: async ({ agent, enabled }) => {
      const workspace = toValue(workspaceSlug);
      const project = toValue(projectId);
      const detailKey = agentKeys.detail(workspace, project, agent.id);
      const listKey = agentKeys.list(workspace, project);
      await queryClient.cancelQueries({ queryKey: agentKeys.all(workspace, project) });
      const previousDetail = queryClient.getQueryData<Agent>(detailKey);
      const previousList = queryClient.getQueryData<Agent[]>(listKey);
      cacheAgent(withAgentStatus(agent, enabled ? "active" : "disabled"));
      return { detailKey, listKey, previousDetail, previousList };
    },
    onError: (_error, _variables, context) => {
      if (!context) return;
      if (context.previousDetail) queryClient.setQueryData(context.detailKey, context.previousDetail);
      else queryClient.removeQueries({ queryKey: context.detailKey, exact: true });
      if (context.previousList) queryClient.setQueryData(context.listKey, context.previousList);
      else queryClient.removeQueries({ queryKey: context.listKey, exact: true });
    },
    onSuccess: cacheAgent,
    onSettled: async () => {
      await queryClient.invalidateQueries({ queryKey: agentKeys.all(toValue(workspaceSlug), toValue(projectId)) });
    },
  });
  const archive = useMutation({
    mutationFn: (agent: Agent) => api.archiveAgent(toValue(workspaceSlug), toValue(projectId), agent.id, agent.version),
    onSuccess: saveAgent,
  });

  return { create, update, setEnabled, archive };
}
