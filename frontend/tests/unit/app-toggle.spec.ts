import { defineComponent, ref } from "vue";
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import { AppToggle } from "@/shared/ui";

describe("AppToggle", () => {
  it("toggles exactly once and updates its checked state", async () => {
    const wrapper = mount(
      defineComponent({
        components: { AppToggle },
        setup() {
          return { enabled: ref(false) };
        },
        template: '<AppToggle v-model="enabled" label="Ассистент включён" />',
      }),
    );
    const input = wrapper.get('input[role="switch"]');

    expect(input.attributes("aria-checked")).toBe("false");
    await input.setValue(true);
    expect(input.attributes("aria-checked")).toBe("true");
    await input.setValue(false);
    expect(input.attributes("aria-checked")).toBe("false");
  });

  it("exposes its label and ignores interaction while disabled", async () => {
    const update = vi.fn();
    const wrapper = mount(AppToggle, {
      props: {
        modelValue: false,
        label: "Ассистент включён",
        description: "Управляет доступностью",
        disabled: true,
        "onUpdate:modelValue": update,
      },
    });
    const input = wrapper.get('input[role="switch"]');
    const element = input.element as HTMLInputElement;

    expect(element.labels?.[0]?.textContent).toContain("Ассистент включён");
    expect(element.disabled).toBe(true);
    await input.trigger("click");
    expect(update).not.toHaveBeenCalled();
  });
});
