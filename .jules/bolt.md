## 2024-05-23 - Frontend Linter and Lockfile
**Learning:** The frontend project was missing a lockfile (`package-lock.json` or `pnpm-lock.yaml`) and the `.eslintrc.cjs` configuration, despite having `lint` script and `eslint` dependencies. This caused initial attempts to lint to fail and implied a non-reproducible environment.
**Action:** Always check for configuration files and lockfiles before assuming a standard environment. When missing, minimal configuration might be needed to proceed with verification.
