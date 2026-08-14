import { inject, type InjectionKey } from "vue";

export interface RuntimeControls {
  resetDemoData(): void;
}

export const runtimeControlsKey: InjectionKey<RuntimeControls> = Symbol("runtime-controls");

export function useRuntimeControls(): RuntimeControls {
  const controls = inject(runtimeControlsKey);
  if (!controls) throw new Error("Runtime controls are not configured");
  return controls;
}
