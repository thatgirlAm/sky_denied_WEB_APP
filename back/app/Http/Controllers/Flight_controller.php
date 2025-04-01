<?php

namespace App\Http\Controllers;

use App\Models\Flight_info;
use Illuminate\Http\Request;
use lluminate\Http\Resources\Flight_info_resouce ; 
use App\Http\Requests\Flight_info_request ; 
use Format; 

class Flight_controller extends Controller
{
    /**
     * Display a listing of the resource: this will be used for the search engine.
     */
    public function index()
    {
        return $this->format(['Index found', Response::HTTP_OK, Flight_info_resource::collection(Flight_info::all())]); 
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
    public function show(FLight_info_request $request)
    {
        $response = Flight_info_resource::make($request);
        return new Flight_info_Resource($response); 
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Flight_info $flight_info)
    {
        // not managed in the back-end
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Flight_info $flight_info)
    {
        // not managed in the back-end
    }
}
