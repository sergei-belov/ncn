import { createApp, type Component } from "vue";

import App from "./App.vue";
import { i18n } from "./plugins/i18n";
import { VueQueryPlugin, vueQueryOptions } from "./plugins/query-client";
import { projectManagementApiPlugin } from "./providers/project-management-api";
import { router } from "./router";
import "./styles/globals.css";

const app = createApp(App as Component);

app.config.errorHandler = (error, _instance, info) => {
  console.error("Vue error", { error, info });
};

app.use(VueQueryPlugin, vueQueryOptions);
app.use(projectManagementApiPlugin);
app.use(i18n);
app.use(router);
app.mount("#app");
