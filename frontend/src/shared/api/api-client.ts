import type { ZodType } from "zod";

import { env } from "@/shared/config/env";

import { ApiError } from "./api-error";

interface RequestOptions<T> {
  schema: ZodType<T>;
  signal?: AbortSignal;
  headers?: HeadersInit;
  idempotencyKey?: string;
  version?: number;
}

interface WireApiError {
  error?: {
    code?: string;
    message?: string;
    request_id?: string;
    field_errors?: Record<string, Array<{ message?: string }>>;
  };
}

async function request<T>(method: string, path: string, body: unknown, options: RequestOptions<T>): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  headers.set("X-Request-ID", crypto.randomUUID());
  if (body !== undefined) headers.set("Content-Type", "application/json");
  if (options.idempotencyKey) headers.set("Idempotency-Key", options.idempotencyKey);
  if (options.version !== undefined) headers.set("If-Match", `"${options.version}"`);

  const response = await fetch(`${env.VITE_API_BASE_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: options.signal,
    credentials: "include",
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as WireApiError;
    const fieldErrors = Object.fromEntries(
      Object.entries(payload.error?.field_errors ?? {}).map(([field, errors]) => [
        field,
        errors.map((error) => error.message ?? "Некорректное значение"),
      ]),
    );
    throw new ApiError({
      status: response.status,
      code: payload.error?.code ?? "REQUEST_FAILED",
      message: payload.error?.message ?? `HTTP ${response.status}`,
      requestId: payload.error?.request_id,
      fieldErrors,
    });
  }

  if (response.status === 204) return options.schema.parse(undefined);
  return options.schema.parse(await response.json());
}

export const apiClient = {
  get<T>(path: string, options: RequestOptions<T>): Promise<T> {
    return request("GET", path, undefined, options);
  },
  post<T>(path: string, body: unknown, options: RequestOptions<T>): Promise<T> {
    return request("POST", path, body, options);
  },
  patch<T>(path: string, body: unknown, options: RequestOptions<T>): Promise<T> {
    return request("PATCH", path, body, options);
  },
  delete<T>(path: string, options: RequestOptions<T>): Promise<T> {
    return request("DELETE", path, undefined, options);
  },
};
