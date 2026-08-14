import { format, isPast, parseISO } from "date-fns";
import { ru } from "date-fns/locale";

export function formatDate(value: string | null): string {
  if (!value) return "Не задано";
  return format(parseISO(value), "d MMM yyyy", { locale: ru });
}

export function isOverdue(value: string | null): boolean {
  if (!value) return false;
  return isPast(parseISO(value));
}
