# Build stage
FROM node:16-alpine as build
WORKDIR /app

# Copy package files and install dependencies
COPY package.json ./
# Use npm install instead of npm ci since we might not have package-lock.json
RUN npm install

# Copy app source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from build stage to nginx
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx config if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]