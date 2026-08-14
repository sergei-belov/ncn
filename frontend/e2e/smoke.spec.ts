import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/demo/projects");
  await page.evaluate(() => window.localStorage.clear());
  await page.reload();
});

test("opens the seeded project board and creates a card", async ({ page }) => {
  await page.getByRole("heading", { name: "Проекты" }).waitFor();
  await page.getByRole("button", { name: /Кабинет клиента/ }).click();
  await expect(page.getByRole("heading", { name: "Доска" })).toBeVisible();

  await page.getByRole("button", { name: "Добавить карточку" }).first().click();
  await page.getByLabel("Название новой карточки").fill("Проверить production smoke");
  await page.getByLabel("Название новой карточки").press("Enter");
  await expect(page.getByText("Проверить production smoke")).toBeVisible();
});

test("opens an epic and shows backend progress", async ({ page }) => {
  await page.getByRole("button", { name: /Кабинет клиента/ }).click();
  await page.getByRole("link", { name: "Эпики" }).click();
  await page.getByRole("button", { name: /Первый запуск пользователя/ }).click();
  await expect(page.getByText("25%")).toBeVisible();
});

test("creates an assistant and saves its settings", async ({ page }) => {
  await page.getByRole("button", { name: /Кабинет клиента/ }).click();
  await page.getByRole("link", { name: "Ассистенты" }).click();
  await expect(page.getByRole("heading", { name: "Координатор проекта" })).toBeVisible();

  await page.getByRole("button", { name: "Новый ассистент" }).click();
  await page.getByLabel("Название *").fill("Аналитик поставщиков");
  await page.getByLabel("Краткое описание").fill("Сравнивает предложения поставщиков");
  await page.getByLabel("Инструкции *").fill("Сравнивай стоимость, сроки и риски поставщиков и возвращай структурированную рекомендацию.");
  await page.getByRole("button", { name: "Создать ассистента" }).click();

  await expect(page.getByRole("heading", { name: "Аналитик поставщиков" })).toBeVisible();
  await page.getByLabel("Краткое описание").fill("Сравнивает предложения, сроки и риски");
  await page.getByRole("button", { name: "Сохранить" }).click();
  await expect(page.getByText("Настройки ассистента сохранены")).toBeVisible();

  const enabledSwitch = page.getByRole("switch", { name: /Ассистент включён/ });
  await expect(enabledSwitch).toBeChecked();
  await page.getByText("Ассистент включён", { exact: true }).click();
  await expect(enabledSwitch).not.toBeChecked();
  await expect(page.getByText("Ассистент отключён")).toBeVisible();
  await page.getByRole("link", { name: "Назад к ассистентам" }).click();
  await expect(page.getByRole("heading", { name: "Аналитик поставщиков" })).toBeVisible();
  await expect(page.getByText("Отключён", { exact: true })).toBeVisible();
});

test("updates project access and restores inherited service access", async ({ page }) => {
  await page.getByRole("button", { name: /Кабинет клиента/ }).click();
  await page.getByRole("link", { name: "Настройки" }).click();
  await page.locator('a[href="/demo/projects/project-web/settings/access"]').click();
  await expect(page.getByRole("heading", { name: "Управление доступом" })).toBeVisible();

  await page.getByRole("button", { name: "Изменить роль Мария Волкова" }).click();
  await page.getByRole("dialog").getByRole("combobox").selectOption("viewer");
  await page.getByRole("dialog").getByRole("button", { name: "Сохранить" }).click();
  await expect(page.getByText("Роль участника обновлена").last()).toBeVisible();

  await page.getByRole("button", { name: "Изменить ограничение ncn-agents" }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Восстановить наследование" }).click();
  await expect(page.locator("p:visible", { hasText: "Наследуется из проекта: Наблюдатель" })).toBeVisible();
});

test("collapses a status into a compact rail and expands it", async ({ page }) => {
  await page.getByRole("button", { name: /Кабинет клиента/ }).click();
  const column = page.locator('[data-state-id="web-todo"]');
  const firstCard = column.locator('[data-work-item-id="wi-web-2"]');
  const expandedBox = await column.boundingBox();
  if (!expandedBox) throw new Error("Kanban column is not visible");

  await expect(column).toHaveAttribute("data-collapsed", "false");
  await column.getByRole("button", { name: "Свернуть колонку К выполнению" }).click();
  await expect(column).toHaveAttribute("data-collapsed", "true");
  await expect(firstCard).not.toBeVisible();
  await expect
    .poll(async () => (await column.boundingBox())?.width)
    .toBeLessThanOrEqual(60);
  await expect
    .poll(async () => (await column.boundingBox())?.height)
    .toBeGreaterThanOrEqual(expandedBox.height - 2);

  await page.reload();
  await expect(column).toHaveAttribute("data-collapsed", "true");
  await expect(firstCard).not.toBeVisible();

  await column.getByRole("button", { name: "Развернуть колонку К выполнению" }).click();
  await expect(column).toHaveAttribute("data-collapsed", "false");
  await expect(firstCard).toBeVisible();
  await expect
    .poll(async () => (await column.boundingBox())?.width)
    .toBeGreaterThanOrEqual(300);
});

test("drops a card into the gap between two cards", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === "mobile", "Precise mouse DnD geometry is covered in the desktop browser project");
  await page.getByRole("button", { name: /Кабинет клиента/ }).click();
  const column = page.locator('[data-state-id="web-todo"]');
  const sourceHandle = column.getByRole("button", { name: "Перетащить WEB-9" });
  const precedingCard = column.locator('[data-work-item-id="wi-web-2"]');
  const sourceBox = await sourceHandle.boundingBox();
  const targetBox = await precedingCard.boundingBox();
  if (!sourceBox || !targetBox) throw new Error("DnD cards are not visible");

  await page.mouse.move(sourceBox.x + sourceBox.width / 2, sourceBox.y + sourceBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(sourceBox.x + sourceBox.width / 2 + 8, sourceBox.y + sourceBox.height / 2 + 8, { steps: 4 });
  await page.mouse.move(targetBox.x + targetBox.width / 2, targetBox.y + targetBox.height - 4, { steps: 16 });
  await page.mouse.up();

  await expect
    .poll(() =>
      column.locator("[data-work-item-id]").evaluateAll((cards) =>
        cards.map((card) => card.getAttribute("data-work-item-id")),
      ),
    )
    .toEqual(["wi-web-2", "wi-web-9", "wi-web-8", "wi-web-12"]);
  await expect(page.getByText("Карточка перемещена в «К выполнению»")).toBeAttached();

  await page.reload();
  await expect
    .poll(() =>
      column.locator("[data-work-item-id]").evaluateAll((cards) =>
        cards.map((card) => card.getAttribute("data-work-item-id")),
      ),
    )
    .toEqual(["wi-web-2", "wi-web-9", "wi-web-8", "wi-web-12"]);
});
