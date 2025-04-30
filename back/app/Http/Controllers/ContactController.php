<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Mail\ContactMail;
use App\Mail\ConfirmContactMail;
use Illuminate\Support\Facades\Mail;
use Illuminate\Http\Response;

class ContactController extends Controller
{
    use FormatTrait;
    
    public function send_contact(Request $request)
    {
        // Validate required fields
        $validated = $request->validate([
            'email' => 'required|email',
            'body' => 'required|string',
            
        ]);
        
        $data = $request->all();
        
        Mail::to("sky.denied.cranfield@gmail.com")->send(new ContactMail($data));
        $this->confirm_contact($request);
        return $this->format(["Contact form sent", Response::HTTP_OK, ""]);
    }

    public function confirm_contact(Request $request)
{
    $validated = $request->validate([
        'email' => 'required|email' 
    ]);
    
    $email = $validated['email'];
    $data = $request->all();
    
    Mail::to($email)->send(new ConfirmContactMail($data));
    return $this->format(['Confirmation sent', Response::HTTP_OK,""]);
}
}