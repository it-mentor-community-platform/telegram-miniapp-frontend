FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite mode: local-stack | staging | prod. CI picks it from the pushed branch.
ARG APP_MODE=local-stack
RUN npm run typecheck && npx vite build --mode "$APP_MODE"

FROM nginx:1.29-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
