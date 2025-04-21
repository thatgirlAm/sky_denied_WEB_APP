<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Airport extends Model
{

    protected $fillable = [
        "icao",
        "iata",
        "name", 
        "city",
        "subd",
        "country", 
        "elevation", 
        "lat",
        "lon", 
        "tz", 
        "lid"
 ];
}
