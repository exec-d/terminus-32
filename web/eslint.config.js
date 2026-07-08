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
      globals: {
        fetch: 'readonly',
        process: 'readonly',
        window: 'readonly',
        document: 'readonly',
        requestAnimationFrame: 'readonly'
      }
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
    languageOptions: { parserOptions: { parser: ts.parser } }
  },
  {
    ignores: ['build/', '.svelte-kit/', 'package/', 'node_modules/']
  }
];
