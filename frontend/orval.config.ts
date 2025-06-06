import { defineConfig } from 'orval'
import dotenv from 'dotenv'

// .env.local 파일 로드
dotenv.config({ path: '.env.local' })

export default defineConfig({
  careerhi: {
    input: {
      target: `${process.env.NEXT_PUBLIC_API_URL}/openapi.json`
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