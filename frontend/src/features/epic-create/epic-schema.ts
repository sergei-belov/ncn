import { z } from "zod";

export const epicSchema = z
  .object({
    name: z.string().trim().min(2, "Введите не менее двух символов").max(100, "Максимум 100 символов"),
    description: z.string().trim().max(1000, "Максимум 1000 символов").default(""),
    color: z.string().regex(/^#[0-9a-fA-F]{6}$/, "Некорректный цвет"),
    startDate: z.string().nullable(),
    targetDate: z.string().nullable(),
  })
  .refine((value) => !value.startDate || !value.targetDate || value.targetDate >= value.startDate, {
    path: ["targetDate"],
    message: "Дата завершения не может быть раньше начала",
  });

export type EpicFormValues = z.infer<typeof epicSchema>;
