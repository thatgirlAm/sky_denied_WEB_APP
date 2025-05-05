# Image with phph-fpm and laravel extensions
FROM php:8.4-fpm AS base

# Install dependencies 
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq-dev \
    libzip-dev zip unzip \
    libxml2-dev \
    libpng-dev \
    libonig-dev \
# Cleaning cache for lighter image
&& rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install \
    pdo_pgsql\
    mbstring \
    xml \
    zip \
    gd 


# Copying composer from official image (lighter multi-stage)
COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer

# Defining working repo
WORKDIR /var/www
COPY . .


# Installing php packages 
RUN composer install --no-dev --optimize-autoloader --no-interaction --prefer-dist \
# Including the new files 
    && composer dump-autoload --optimize \
    && php artisan package:discover --ansi


# Permissions for cache storing
RUN chown -R www-data:www-data storage bootstrap/cache 

# Exposing port 
EXPOSE 9000

# Launch php-fpm
CMD ["php-fpm"]