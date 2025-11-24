<?php
// Simple SePay checkout generator using sepay/sepay-pg SDK.
// Requirements:
//   composer require sepay/sepay-pg
//   env: SEPAY_MERCHANT_ID, SEPAY_SECRET_KEY, SEPAY_ENV (sandbox|production)
//
// Usage (CLI or php -S 0.0.0.0:9000):
//   curl -X POST http://localhost:9000/checkout.php \
//     -H "Content-Type: application/json" \
//     -d '{"invoice_id":"32","amount":50000,"description":"Thanh toan don dat san #32","success_url":"https://example.com/success","error_url":"https://example.com/error","cancel_url":"https://example.com/cancel"}'
//
// Response: {"form_html":"<form ...>...</form><script>...</script>","payload":{...}}

require_once __DIR__ . '/../vendor/autoload.php';
// Load env from Billing/core/.env if present (useful when running php -S)
if (class_exists(\Dotenv\Dotenv::class)) {
    $dotenv = \Dotenv\Dotenv::createImmutable(dirname(__DIR__) . '/core');
    $dotenv->safeLoad();
}

use SePay\Builders\CheckoutBuilder;
use SePay\SePayClient;

header('Content-Type: application/json');

function error_out($msg, $code = 400) {
    http_response_code($code);
    echo json_encode(['error' => $msg]);
    exit;
}

$merchantId = getenv('SEPAY_MERCHANT_ID') ?: ($_ENV['SEPAY_MERCHANT_ID'] ?? null);
$secretKey  = getenv('SEPAY_SECRET_KEY')  ?: ($_ENV['SEPAY_SECRET_KEY'] ?? null);
$env        = getenv('SEPAY_ENV') ?: ($_ENV['SEPAY_ENV'] ?? 'sandbox');

if (!$merchantId || !$secretKey) {
    error_out("Missing SEPAY_MERCHANT_ID or SEPAY_SECRET_KEY env", 500);
}

$raw = file_get_contents('php://input');
$input = json_decode($raw, true);
if (!$input) {
    error_out("Invalid JSON input");
}

$amount = isset($input['amount']) ? intval($input['amount']) : null;
$invoiceId = $input['invoice_id'] ?? null;
$description = $input['description'] ?? ("Thanh toan #" . $invoiceId);
$operation = $input['operation'] ?? (getenv('SEPAY_OPERATION') ?: 'PURCHASE');
$successUrl = $input['success_url'] ?? (getenv('SEPAY_SUCCESS_URL') ?: null);
$errorUrl = $input['error_url'] ?? (getenv('SEPAY_ERROR_URL') ?: null);
$cancelUrl = $input['cancel_url'] ?? (getenv('SEPAY_CANCEL_URL') ?: null);
$paymentMethod = $input['payment_method'] ?? (getenv('SEPAY_PAYMENT_METHOD') ?: null); // optional, e.g. ATM/QRCODE
$customerId = $input['customer_id'] ?? null;

if (!$amount || !$invoiceId) {
    error_out("Missing amount or invoice_id");
}

$sepay = new SePayClient($merchantId, $secretKey, $env);

$builder = CheckoutBuilder::make()
    ->currency('VND')
    ->orderInvoiceNumber((string)$invoiceId)
    ->orderAmount($amount)
    ->operation($operation)
    ->orderDescription($description);

if ($successUrl) $builder->successUrl($successUrl);
if ($errorUrl) $builder->errorUrl($errorUrl);
if ($cancelUrl) $builder->cancelUrl($cancelUrl);
if ($paymentMethod) {
    // Map alias ATM -> BANK_TRANSFER, NAPAS -> NAPAS_BANK_TRANSFER
    $map = [
        'ATM' => 'BANK_TRANSFER',
        'BANK' => 'BANK_TRANSFER',
        'NAPAS' => 'NAPAS_BANK_TRANSFER',
    ];
    $normalized = strtoupper($paymentMethod);
    if (isset($map[$normalized])) {
        $normalized = $map[$normalized];
    }
    $builder->paymentMethod($normalized);
}
if ($customerId) $builder->customerId($customerId);

$checkoutData = $builder->build();
$formHtml = $sepay->checkout()->generateFormHtml($checkoutData);

echo json_encode([
    'form_html' => $formHtml,
    'payload' => $checkoutData,
]);
