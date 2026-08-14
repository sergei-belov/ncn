export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly requestId: string;
  readonly fieldErrors: Record<string, string[]>;

  constructor(options: {
    status: number;
    code: string;
    message: string;
    requestId?: string;
    fieldErrors?: Record<string, string[]>;
  }) {
    super(options.message);
    this.name = "ApiError";
    this.status = options.status;
    this.code = options.code;
    this.requestId = options.requestId ?? crypto.randomUUID();
    this.fieldErrors = options.fieldErrors ?? {};
  }
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError || error instanceof Error) return error.message;
  return "Неизвестная ошибка";
}
