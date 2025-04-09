<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\HTTP\Controllers\FlightController ;


//-- Using CRUD --//
// (TEST: trying to display the index with the CRUD function)
Route::apiResource('/flights', FlightController::class); 