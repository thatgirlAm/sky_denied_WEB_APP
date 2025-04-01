<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Notifications\Notifiable;

class Flight_info extends Model
{
    use Notifiable;

    protected $fillable=[
        
    'flight_id character',
    'destination_code',
    'origin_code' ,
    'airline_code',
    'flightnumber' 

    ];
}

