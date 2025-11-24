FROM php:8.2-apache

WORKDIR /var/www/html

# Copy code and vendor (SDK đã được cài ở Billing/vendor)
COPY Billing/php/checkout.php checkout.php
COPY Billing/vendor vendor
COPY Billing/core/.env .env

# Lưu ý: Apache listen mặc định 80, map ra 9000 trong docker-compose
