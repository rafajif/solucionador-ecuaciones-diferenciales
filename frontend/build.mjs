import { build } from 'vite'
import react from '@vitejs/plugin-react'

// Production does not need the dev-server proxy. Supplying the plugin directly
// avoids bundling the TypeScript Vite config just to run a production build.
await build({
  configFile: false,
  plugins: [react()],
})
