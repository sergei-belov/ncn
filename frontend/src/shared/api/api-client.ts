import type { ZodType } from "zod";

import { env } from "@/shared/config/env";

import { ApiError } from "./api-error";

interface RequestOptions<T> {
  schema: ZodType<T>;
  signal?: AbortSignal;
  headers?: HeadersInit;
  idempotencyKey?: string;
  version?: number;
  body?: unknown;
}

interface WireErrorDetails {
  code?: string;
  message?: string;
  request_id?: string;
  correlation_id?: string;
  field_errors?: Record<string, unknown>;
  current?: unknown;
}

interface WireApiError extends WireErrorDetails {
  error?: WireErrorDetails;
}

function fieldErrorMessages(value: unknown): string[] {
  if (typeof value === "string") return [value];
  if (!Array.isArray(value)) return ["Некорректное значение"];
  return (value as unknown[]).map((entry) => {
    if (typeof entry === "string") return entry;
    if (typeof entry === "object" && entry) {
      const candidate = entry as Record<string, unknown>;
      if (typeof candidate.message === "string") return candidate.message;
    }
    return "Некорректное значение";
  });
}

async function request<T>(method: string, path: string, body: unknown, options: RequestOptions<T>): Promise<T> {
  const headers = new Headers(options.headers);
  const correlationId = crypto.randomUUID();
  headers.set("Accept", "application/json");
  headers.set("X-Correlation-ID", correlationId);
  headers.set("X-Request-ID", correlationId);
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
    const details: WireErrorDetails = payload.error ?? payload;
    const fieldErrors = Object.fromEntries(
      Object.entries(details.field_errors ?? {}).map(([field, errors]) => [field, fieldErrorMessages(errors)]),
    );
    throw new ApiError({
      status: response.status,
      code: details.code ?? "REQUEST_FAILED",
      message: details.message ?? `HTTP ${response.status}`,
      requestId: details.request_id ?? details.correlation_id ?? response.headers.get("X-Correlation-ID") ?? undefined,
      fieldErrors,
      current: details.current,
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
  put<T>(path: string, body: unknown, options: RequestOptions<T>): Promise<T> {
    return request("PUT", path, body, options);
  },
  delete<T>(path: string, options: RequestOptions<T>): Promise<T> {
    return request("DELETE", path, options.body, options);
  },
};
