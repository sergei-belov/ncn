import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import pluginVue from "eslint-plugin-vue";
import vueParser from "vue-eslint-parser";

export default tseslint.config(
  { ignores: ["dist", "node_modules", "playwright-report", "test-results"] },
  eslint.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  ...pluginVue.configs["flat/recommended"],
  {
    files: ["**/*.{ts,vue}"],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tseslint.parser,
        projectService: true,
        extraFileExtensions: [".vue"],
      },
    },
    rules: {
      "no-undef": "off",
      "vue/multi-word-component-names": "off",
      "vue/attribute-hyphenation": ["error", "always"],
      "vue/html-self-closing": "off",
      "vue/max-attributes-per-line": "off",
      "vue/singleline-html-element-content-newline": "off",
      "@typescript-eslint/consistent-type-imports": "error"
    }
  },
  {
    files: ["src/shared/**/*.{ts,vue}"],
    rules: {
      "no-restricted-imports": ["error", { patterns: [{ group: ["@/app/**", "@/pages/**", "@/widgets/**", "@/features/**", "@/entities/**"], message: "shared must stay business-neutral" }] }]
    }
  },
  {
    files: ["src/entities/**/*.{ts,vue}"],
    rules: {
      "no-restricted-imports": ["error", { patterns: [{ group: ["@/app/**", "@/pages/**", "@/widgets/**", "@/features/**"], message: "entities may depend only on explicit entity cross-APIs and shared" }] }]
    }
  },
  {
    files: ["src/features/**/*.{ts,vue}"],
    rules: {
      "no-restricted-imports": ["error", { patterns: [{ group: ["@/app/**", "@/pages/**", "@/widgets/**"], message: "features may depend only on entities and shared" }] }]
    }
  },
  {
    files: ["src/widgets/**/*.{ts,vue}"],
    rules: {
      "no-restricted-imports": ["error", { patterns: [{ group: ["@/app/**", "@/pages/**", "@/widgets/**"], message: "widgets may depend only on features, entities, shared, and relative files in their own slice" }] }]
    }
  },
  {
    files: ["src/pages/**/*.{ts,vue}"],
    rules: {
      "no-restricted-imports": ["error", { patterns: [{ group: ["@/app/**", "@/pages/**"], message: "pages may not depend on app or other page slices" }] }]
    }
  }
);
