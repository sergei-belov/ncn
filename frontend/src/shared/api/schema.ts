import { z } from "zod";

export function dataSchema<T extends z.ZodType>(schema: T) {
  return z.object({ data: schema });
}

export function listSchema<T extends z.ZodType>(schema: T) {
  return z.object({ data: z.array(schema) });
}

export const voidSchema = z.undefined();
