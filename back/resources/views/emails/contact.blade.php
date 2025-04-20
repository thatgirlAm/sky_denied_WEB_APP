<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Message</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #007bff;
        }
        .header h1 {
            margin: 0;
            color: #007bff;
            font-size: 24px;
        }
        .sender-info {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .sender-info p {
            margin: 5px 0;
        }
        .message-content {
            background-color: #fff;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e9ecef;
            margin-bottom: 20px;
        }
        .message-content h3 {
            margin-top: 0;
            color: #495057;
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 8px;
        }
        .footer {
            font-size: 12px;
            color: #6c757d;
            text-align: center;
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #e9ecef;
        }
        .highlight {
            font-weight: bold;
            color: #495057;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>New Contact Message</h1>
    </div>
    
    <div class="sender-info">
        <p><span class="highlight">From:</span> {{ $data['name'] ?? 'Unknown' }} &lt;{{ $data['email'] }}&gt;</p>
        
        @if(isset($data['subject']) && !empty($data['subject']))
            <p><span class="highlight">Subject:</span> {{ $data['subject'] }}</p>
        @endif
        
        @if(isset($data['phone']) && !empty($data['phone']))
            <p><span class="highlight">Phone:</span> {{ $data['phone'] }}</p>
        @endif
        
        <p><span class="highlight">Sent:</span> {{ date('F j, Y, g:i a') }}</p>
    </div>
    
    <div class="message-content">
        <h3>Message</h3>
        <div>
            {!! nl2br(e($data['body'])) !!}
        </div>
    </div>
    
    <div class="footer">
        <p>This email was sent from your website contact form.</p>
        <p>To reply directly to the sender, simply reply to this email.</p>
    </div>
</body>
</html>
```