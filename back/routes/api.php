<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\HTTP\Controllers\Flight_controller ;


//-- For now I do not put any middleware--//

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');


//-- Using CRUD --//
// (TEST: trying to display the index with the CRUD function)
Route::apiResource('flight_info', Flight_controller::class); 