# Stage 1: Build React assets
FROM node:20-alpine AS builder

WORKDIR /app

# Copy manifests first for layer-cache efficiency
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve via nginx
# Static assets are baked in — no shared volume, no race condition.
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html/dashboard
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
