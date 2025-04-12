# Build stage
FROM node:18-slim as builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --production

# Set environment to production
ENV NODE_ENV=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Add non-root user
RUN addgroup -g 1001 -S app && \
    adduser -u 1001 -S app -G app && \
    chown -R app:app /var/cache/nginx && \
    chown -R app:app /var/log/nginx && \
    chown -R app:app /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R app:app /var/run/nginx.pid

# Copy built assets from builder stage
COPY --from=builder --chown=app:app /app/dist /usr/share/nginx/html/

# Copy nginx configuration
COPY --chown=app:app nginx.conf /etc/nginx/conf.d/default.conf

# Switch to non-root user
USER app

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
