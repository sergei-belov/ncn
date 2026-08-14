import { z } from "zod";

const envSchema = z.object({
  VITE_API_MODE: z.enum(["mock", "http"]).default("mock"),
  VITE_API_BASE_URL: z.string().default("/api/v1"),
  VITE_WORKSPACE_SLUG: z.string().min(1).default("demo"),
  VITE_APP_ENV: z.enum(["local", "staging", "production"]).default("local"),
});

export const env = envSchema.parse(import.meta.env);
