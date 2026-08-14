import { z } from "zod";

export const projectSchema = z.object({
  name: z.string().trim().min(2, "Введите не менее двух символов").max(80, "Максимум 80 символов"),
  identifier: z
    .string()
    .trim()
    .toUpperCase()
    .regex(/^[A-Z0-9]{2,10}$/, "Используйте 2–10 латинских букв или цифр"),
  description: z.string().trim().max(500, "Максимум 500 символов").default(""),
  access: z.enum(["private", "workspace"]),
});

export type ProjectFormValues = z.infer<typeof projectSchema>;
