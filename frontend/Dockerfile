FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Clean install to avoid npm bugs
RUN rm -rf node_modules package-lock.json
RUN npm cache clean --force
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage - serve static files
FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]