# Fund Admin UI

React + TypeScript frontend built with Vite.

## Environment Configuration

All environment-specific settings are defined in a single file:

```
src/config/constants.ts
```

### How it works

Vite sets `import.meta.env.MODE` automatically based on how the app is started:

| Command | Mode | `import.meta.env.MODE` |
|---|---|---|
| `vite` (dev server) | development | `"development"` |
| `vite --mode test` | test | `"test"` |
| `vite build` | production | `"production"` |
| `vite build --mode test` | test | `"test"` |

The `constants.ts` file reads this mode and selects the matching config:

```typescript
const ENV: Environment = (import.meta.env.MODE as Environment) || 'development';
```

### Config values per environment

| Setting | Development | Test | Production |
|---|---|---|---|
| `API_URL` | `http://localhost:5000` | `http://localhost:5001` | `https://api.fundadmin.com` |
| `APP_TITLE` | Fund Admin (Dev) | Fund Admin (Test) | Fund Admin |

### Usage in code

```typescript
import { API_URL, APP_TITLE, IS_DEV } from '../config/constants';

fetch(`${API_URL}/api/endpoint`);
```

### Running in different modes

```bash
# Development (default)
npm run dev

# Test mode
npx vite --mode test

# Production build
npm run build

# Production build with test config
npx vite build --mode test
```

## Scripts

- `npm run dev` — Start dev server
- `npm run build` — Type check + production build
- `npm run preview` — Preview production build locally
- `npm run type-check` — Run TypeScript type checking
