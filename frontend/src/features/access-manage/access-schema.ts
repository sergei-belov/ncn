import { z } from "zod";

export const workspaceMembershipFormSchema = z.object({
  userId: z.string().trim().min(1, "Укажите UUID пользователя").max(128, "UUID слишком длинный"),
  role: z.enum(["admin", "member"], { message: "Выберите роль workspace" }),
});

export const projectMembershipFormSchema = z.object({
  userId: z.string().trim().min(1, "Укажите UUID пользователя").max(128, "UUID слишком длинный"),
  role: z.enum(["admin", "member", "viewer"], { message: "Выберите роль проекта" }),
});

export const serviceRestrictionFormSchema = z.object({
  serviceId: z
    .string()
    .trim()
    .min(1, "Укажите идентификатор сервиса")
    .max(100, "Идентификатор слишком длинный")
    .regex(/^[a-z0-9][a-z0-9._-]*$/, "Используйте строчные латинские буквы, цифры, точку, дефис или подчёркивание"),
  role: z.enum(["admin", "member", "viewer"], { message: "Выберите роль сервиса" }),
});

export type WorkspaceMembershipFormValues = z.infer<typeof workspaceMembershipFormSchema>;
export type ProjectMembershipFormValues = z.infer<typeof projectMembershipFormSchema>;
export type ServiceRestrictionFormValues = z.infer<typeof serviceRestrictionFormSchema>;
