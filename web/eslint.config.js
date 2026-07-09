import js from '@eslint/js';
import ts from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';
import prettier from 'eslint-config-prettier';

export default [
  js.configs.recommended,
  ...ts.configs.recommended,
  ...svelte.configs['flat/recommended'],
  prettier,
  ...svelte.configs['flat/prettier'],
  {
    languageOptions: {
      globals: { fetch: 'readonly', process: 'readonly' }
    },
    rules: {
      // Autorise les identifiants préfixés `_` (ex. `{#each items as _, i}` quand
      // seul l'index est utilisé) à rester non utilisés.
      '@typescript-eslint/no-unused-vars': [
        'error',
        { varsIgnorePattern: '^_', argsIgnorePattern: '^_' }
      ]
    }
  },
  {
    files: ['**/*.svelte'],
    languageOptions: { parserOptions: { parser: ts.parser } },
    // `no-undef` est désactivé pour les `.svelte` comme il l'est déjà pour les `.ts`
    // (ts-eslint recommended) : svelte-check fait autorité sur les identifiants non
    // définis dans les `<script>` ; ESLint core ne connaît pas les globals navigateur.
    rules: { 'no-undef': 'off' }
  },
  {
    ignores: ['build/', '.svelte-kit/', 'package/', 'node_modules/']
  }
];
