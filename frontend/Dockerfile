# Build stage
FROM node:18-slim as builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Set TypeScript environment
ENV NODE_ENV=production \
    VITE_API_URL=https://billybobai-production.up.railway.app

# Copy source code
COPY . .

# Build the app with explicit TypeScript path
RUN npm run build || (echo "Build failed" && cat /app/tsconfig.json && exit 1)

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]