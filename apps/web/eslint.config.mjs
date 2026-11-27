import { defineConfig, globalIgnores } from 'eslint/config'
import nextVitals from 'eslint-config-next/core-web-vitals'
import nextTs from 'eslint-config-next/typescript'

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  {
    rules: {
      // Existing code reads a ref during render (components/before-after-slider.tsx).
      // Kept as a warning so the dependency upgrade does not change UI behaviour.
      'react-hooks/refs': 'warn',
    },
  },
  {
    // CommonJS config files
    files: ['*.config.js', 'jest.setup.js'],
    rules: { '@typescript-eslint/no-require-imports': 'off' },
  },
  globalIgnores(['.next/**', 'out/**', 'build/**', 'coverage/**', 'next-env.d.ts']),
])
