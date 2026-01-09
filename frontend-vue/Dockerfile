# Multi-stage build for Vue.js PWA Dashboard

# Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build arguments for environment variables (injected at build time)
ARG VITE_DISTRIBUTOR_IP
ARG VITE_API_PORT=8000
ARG VITE_VENDING_MACHINE_PORT=1500
ARG VITE_APP_TITLE="Dashboard Distributore"
ARG VITE_APP_VERSION="2.0.0"

# Set environment variables for Vite build
ENV VITE_DISTRIBUTOR_IP=${VITE_DISTRIBUTOR_IP}
ENV VITE_API_PORT=${VITE_API_PORT}
ENV VITE_VENDING_MACHINE_PORT=${VITE_VENDING_MACHINE_PORT}
ENV VITE_APP_TITLE=${VITE_APP_TITLE}
ENV VITE_APP_VERSION=${VITE_APP_VERSION}

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built Vue.js app to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Expose port 80 (frontend)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
