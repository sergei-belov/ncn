import { createI18n } from "vue-i18n";

export const i18n = createI18n({
  legacy: false,
  locale: "ru",
  fallbackLocale: "ru",
  messages: {
    ru: {
      common: {
        save: "Сохранить",
        cancel: "Отмена",
        delete: "Удалить",
      },
    },
  },
});
