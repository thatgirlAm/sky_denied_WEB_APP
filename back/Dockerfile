FROM php:8.2-fpm-alpine AS laravel-base

# Dependencies install
RUN apk update && apk add --no-cache \
    git \
    curl \
    zip \
    unzip \
    libzip-dev \
    icu-dev \
    oniguruma-dev \
    libxml2-dev \
    postgresql-dev \
    mariadb-dev

# PHP extensions
RUN docker-php-ext-install -j$(nproc) \
    pdo pdo_mysql pdo_pgsql zip intl mbstring xml opcache

# Composer install
COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer

# Repo
WORKDIR /var/www/html

# Copy application file
COPY . .
RUN rm -rf vendor node_modules

# Install of PHP dependencies
RUN composer install --optimize-autoloader --no-dev

# Copying conf files
COPY .env.example .env
# Generating key
RUN php artisan key:generate

# Optimizing the application
RUN php artisan config:cache && php artisan route:cache && php artisan view:cache

FROM nginx:stable-alpine


COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# Copying Laravel files
COPY --from=laravel-base /var/www/html /var/www/html

# Exposing 80
EXPOSE 80

# User
 USER  www-data

# Start
CMD ["sh", "-c", "php-fpm && nginx -g 'daemon off;'"]