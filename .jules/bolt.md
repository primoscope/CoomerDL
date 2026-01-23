## 2024-05-24 - Missing ESLint Config in Frontend
**Learning:** The frontend `package.json` contains a `lint` script that references `eslint`, but the configuration file (`.eslintrc.cjs` or similar) is missing from the directory, causing `npm run lint` to fail.
**Action:** When working on the frontend, rely on `npm run build` (which includes `tsc`) for verification, or re-initialize eslint if strict linting is required. Don't assume `npm run lint` works out of the box despite being in `package.json`.
