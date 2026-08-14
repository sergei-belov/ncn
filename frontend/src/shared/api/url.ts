export function projectBase(workspaceSlug: string, projectId?: string): string {
  const root = `/workspaces/${encodeURIComponent(workspaceSlug)}/projects`;
  return projectId ? `${root}/${encodeURIComponent(projectId)}` : root;
}

export function queryString(values: Record<string, string | string[] | boolean | null | undefined>): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) {
    if (value === undefined || value === null || value === "" || value === false) continue;
    if (Array.isArray(value)) value.forEach((item) => params.append(key, item));
    else params.set(key, String(value));
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}
