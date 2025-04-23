<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    protected $fillable=[
        "name",
        "email",
        "tail_number",
        "schedule_date_utc"
    ];
}
