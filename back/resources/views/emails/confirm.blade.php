<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You for Contacting Us</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background-color: #7C4091;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .content {
            padding: 20px;
        }
        .footer {
            background-color: #f8f9fa;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
        }
        .button {
            display: inline-block;
            background-color: #28A745;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .details {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .details h3 {
            margin-top: 0;
            color: #495057;
        }
        
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Thank You for Contacting Us</h1>
        </div>
        
        <div class="content">
            <p>Dear {{ $data['name'] ?? 'Valued Customer' }},</p>
            
            <p>Thank you for reaching out to us. We have received your message and will get back to you as soon as possible.</p>
            
            <div class="details">
                <h3>Your Message Details</h3>
                <p><strong>Email:</strong> {{ $data['email'] }}</p>
                
                @if(isset($data['subject']) && !empty($data['subject']))
                    <p><strong>Subject:</strong> {{ $data['subject'] }}</p>
                @endif
                
                <p><strong>Message:</strong></p>
                <p>{!! nl2br(e(substr($data['body'], 0, 150) . (strlen($data['body']) > 150 ? '...' : ''))) !!}</p>
            </div>
            
            <p>Our team is reviewing your inquiry and will respond within 1-2 business days.</p>
            
            <p>If you have any urgent concerns, please don't hesitate to call us at <strong>07 123 89 00 00</strong>.</p>
            
            <p>Best regards,<br>
            The Sky Denied Team</p>
            
            <a href="sky_denied.cranfield.uk" class="button">Visit Our Website</a>
        </div>
        
        <div class="footer">
            <p>© {{ date('Y') }} Sky Denied. All rights reserved.</p>
            <p>This is an automated message, please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>