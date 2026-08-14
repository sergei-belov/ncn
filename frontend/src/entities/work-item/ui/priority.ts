import type { Priority } from "../model/types";

export const priorityMeta: Record<Priority, { label: string; className: string }> = {
  none: { label: "Без приоритета", className: "text-muted-foreground" },
  low: { label: "Низкий", className: "text-sky-600 dark:text-sky-400" },
  medium: { label: "Средний", className: "text-amber-600 dark:text-amber-400" },
  high: { label: "Высокий", className: "text-orange-600 dark:text-orange-400" },
  urgent: { label: "Срочный", className: "text-destructive" },
};
