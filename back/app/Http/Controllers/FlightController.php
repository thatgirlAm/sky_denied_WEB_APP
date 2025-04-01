<?php

namespace App\Http\Controllers;

use App\Models\Flight;
use Illuminate\Http\Request;
use lluminate\Http\Resources\FlightResource ; 
use App\Http\Requests\FlightRequest ; 
use Format; 

class FlightController extends Controller
{
    /**
     * Display a listing of the resource: this will be used for the search engine.
     */
    public function index()
    {
        return $this->format(['Index found', Response::HTTP_OK, FlightResource::collection(Flight::all())]); 
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        // not managed in the back-end
    }

    /**
     * Display the specified resource.
     */
    public function show(FlightResource $request)
    {
        $response = FlightResource::make($request);
        return new FlightResource($response); 
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Flight $flight)
    {
        // not managed in the back-end
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Flight $flight)
    {
        // not managed in the back-end
    }
}
