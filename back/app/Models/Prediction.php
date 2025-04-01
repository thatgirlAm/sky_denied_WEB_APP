<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Prediction extends Model
{
    protected $fillable=[
        "flight_id", 
        "delayed",
        "previous_prediction",
        "accuracy"
    ];
}
