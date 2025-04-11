<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\HTTP\Controllers\FlightController ;
use App\Http\Controllers\PredictionController ;
use Tests\Feature\PredictionControllerTest;

Route::middleware([])->group(function () {
//-- Using CRUD functions --//
// (TEST: trying to display the index with the CRUD function)
Route::apiResource('/flights', FlightController::class); 
Route::apiResource('/prediction', PredictionController::class); 


// -- Prediction -- // 
// Route for the entire prediction scheme
Route::post('/trigger/{data}', [PredictionController::class, 'trigger']);



// ********** For testing sake ********** // 
// Default route for testing the API
Route::get('/test', function () {
    return response()->json(['message' => 'API is working'], 200);
});
// This triggers the Python script to crawl data from the source's website
Route::post('/prediction/crawl/{tail_number}', [PredictionController::class, 'crawling_trigger']);
// Route to trigger the model execution
Route::post('/model_trigger', [PredictionController::class, 'model_trigger']);
Route::post('/prediction/model_trigger_test', [PredictionController::class, 'model_trigger_test']);
Route::post('/prediction/data_handling', [PredictionController::class, 'data_handling']);
});