import { z } from "zod";

import { mapEpic, wireEpicSchema } from "@/entities/epic/@x/board-api";
import { mapMember, wireMemberSchema } from "@/entities/member/@x/board-api";
import { mapProject, wireProjectSchema } from "@/entities/project/@x/board-api";
import { mapWorkItem, wireWorkItemSchema } from "@/entities/work-item/@x/board-api";
import { mapState, wireStateSchema } from "@/entities/workflow-state/@x/board-api";

import type { BoardPayload } from "../model/types";

export const wireColumnSchema = z.object({
  state_id: z.string(),
  work_item_ids: z.array(z.string()),
  total_count: z.number(),
  next_cursor: z.string().nullable(),
});

export const wireBoardSchema = z.object({
  data: z.object({
    project: wireProjectSchema,
    states: z.array(wireStateSchema),
    work_items: z.array(wireWorkItemSchema),
    epics: z.array(wireEpicSchema),
    members: z.array(wireMemberSchema),
    columns: z.array(wireColumnSchema),
    board_version: z.number(),
  }),
});

export function mapBoard(value: z.infer<typeof wireBoardSchema>): BoardPayload {
  return {
    project: mapProject(value.data.project),
    states: value.data.states.map(mapState),
    workItems: value.data.work_items.map(mapWorkItem),
    epics: value.data.epics.map(mapEpic),
    members: value.data.members.map(mapMember),
    columns: value.data.columns.map((column) => ({
      stateId: column.state_id,
      workItemIds: column.work_item_ids,
      totalCount: column.total_count,
      nextCursor: column.next_cursor,
    })),
    boardVersion: value.data.board_version,
  };
}
