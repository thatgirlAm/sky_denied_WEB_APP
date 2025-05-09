FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json package-lock.json ./

RUN npm install --force @angular/animations @angular/platform-browser ngx-toastr

COPY . .
RUN npm run build -- --configuration=production

# Stage 2: Serve the built application with Nginx
FROM nginx:stable-alpine
COPY --from=builder app/dist/front/browser /usr/share/nginx/html
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]