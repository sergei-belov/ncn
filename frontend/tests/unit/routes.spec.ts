import { describe, expect, it } from "vitest";
import type { RouteRecordRaw } from "vue-router";

import { routes } from "@/app/router/routes";
import { routeNames } from "@/shared/routes";

function flatten(records: readonly RouteRecordRaw[]): RouteRecordRaw[] {
  return records.flatMap((record) => [record, ...flatten(record.children ?? [])]);
}

describe("agent routes", () => {
  it("registers project-scoped assistants, settings, and sessions routes", () => {
    const byName = new Map(flatten(routes).map((route) => [route.name, route]));

    expect(byName.get(routeNames.agents)?.path).toBe("agents");
    expect(byName.get(routeNames.agentSettings)?.path).toBe("agents/:agentId/settings");
    expect(byName.get(routeNames.sessions)?.path).toBe("sessions");
  });
});
