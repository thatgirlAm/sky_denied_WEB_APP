<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class Flight extends Model
{
    use Notifiable, HasApiTokens;

    protected $fillable=[
        
    'flight_id character',
    'destination_code',
    'origin_code' ,
    'airline_code',
    'flightnumber' 

    ];
}

