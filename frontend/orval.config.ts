import { defineConfig } from 'orval'

export default defineConfig({
  careerhi: {
    input: {
      target: 'http://localhost:8000/openapi.json'
    },
    output: {
      mode: 'tags-split',
      target: 'lib/api/generated',
      schemas: 'lib/api/generated/model',
      client: 'react-query',
      override: {
        mutator: {
          path: 'lib/api/mutator.ts',
          name: 'customInstance'
        }
      }
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write'
    }
  }
}) 