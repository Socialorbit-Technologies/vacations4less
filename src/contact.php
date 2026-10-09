<?php
/**
 * Vacations4Less — quote request + newsletter handler.
 * Sends an email to the agency inbox, then redirects to thank-you.html.
 * Works on standard DirectAdmin/PHP hosting (uses PHP mail()).
 */

$TO        = 'contact@vacations4less.us';
$FROM      = 'no-reply@vacations4less.us';   // must be an address on this domain for deliverability
$SITE_NAME = 'Vacations4Less website';

function back_with_error($code) {
    $ref  = isset($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : 'contact.html';
    $host = isset($_SERVER['HTTP_HOST']) ? $_SERVER['HTTP_HOST'] : '';
    // Only redirect back to our own pages
    if (parse_url($ref, PHP_URL_HOST) && parse_url($ref, PHP_URL_HOST) !== $host) {
        $ref = 'contact.html';
    }
    $ref = preg_replace('/[?#].*$/', '', $ref);
    // Quote errors are shown on the full contact form
    if (basename(parse_url($ref, PHP_URL_PATH) ?: '') !== 'contact.html') {
        $ref = 'contact.html';
    }
    header('Location: ' . $ref . '?error=' . urlencode($code) . '#form-error', true, 303);
    exit;
}

function clean($key, $max = 500) {
    if (!isset($_POST[$key]) || is_array($_POST[$key])) return '';
    $v = trim((string) $_POST[$key]);
    $v = str_replace(["\r", "\0"], '', $v);
    return mb_substr($v, 0, $max);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: contact.html', true, 303);
    exit;
}

// Honeypot: bots fill the hidden "website" field. Pretend success.
if (!empty($_POST['website'])) {
    header('Location: thank-you.html', true, 303);
    exit;
}

$form  = clean('form', 40);
$email = clean('email', 200);

if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    back_with_error('email');
}

if ($form === 'newsletter') {
    if ($email === '') back_with_error('email');
    $subject = 'Mailing list signup: ' . $email;
    $body    = "New mailing list signup from the website.\n\nEmail: {$email}\nDate: " . date('Y-m-d H:i T') . "\n";
    $redirect = 'thank-you.html#subscribed';
} else {
    $name  = clean('name', 120);
    $phone = clean('phone', 40);
    if ($name === '' || ($phone === '' && $email === '')) {
        back_with_error('missing');
    }

    $needs = [];
    if (isset($_POST['needs']) && is_array($_POST['needs'])) {
        foreach ($_POST['needs'] as $n) {
            $needs[] = mb_substr(trim(str_replace(["\r", "\n"], ' ', (string) $n)), 0, 40);
        }
    }

    $fields = [
        'Name'        => $name,
        'Phone'       => $phone,
        'Email'       => $email,
        'Destination' => clean('destination', 200),
        'Leaving'     => clean('depart', 20),
        'Returning'   => clean('return', 20),
        'Travelers'   => clean('travelers', 10),
        'Adults'      => clean('adults', 10),
        'Children'    => clean('children', 10),
        'Wants'       => implode(', ', $needs),
        'Budget'      => clean('budget', 40),
        'Notes'       => clean('message', 4000),
    ];

    $lines = [];
    foreach ($fields as $label => $value) {
        if ($value !== '') $lines[] = str_pad($label . ':', 13) . $value;
    }
    $source  = $form === 'quote-hero' ? 'home page' : 'contact page';
    $subject = 'Trip quote request: ' . $name . ($fields['Destination'] ? ' — ' . $fields['Destination'] : '');
    $body    = "New quote request from the {$source}.\n\n" . implode("\n", $lines) .
               "\n\nSent " . date('Y-m-d H:i T') . " from " . (isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : 'unknown') . "\n";
    $redirect = 'thank-you.html';
}

// Strip anything that could inject headers
$subject = str_replace(["\r", "\n"], ' ', $subject);
$headers = [
    'From: ' . $SITE_NAME . ' <' . $FROM . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: PHP/' . phpversion(),
];
if ($email !== '') {
    $headers[] = 'Reply-To: ' . $email;
}

$encodedSubject = '=?UTF-8?B?' . base64_encode($subject) . '?=';
$ok = @mail($TO, $encodedSubject, $body, implode("\r\n", $headers), '-f' . $FROM);

if (!$ok) back_with_error('send');

header('Location: ' . $redirect, true, 303);
exit;
