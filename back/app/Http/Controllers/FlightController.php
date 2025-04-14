<?php

namespace App\Http\Controllers;

use App\Models\Flight;
use Illuminate\Http\Request;
use App\Http\Resources\FlightResource ; 
use App\Http\Requests\FlightRequest ; 
use Symfony\Component\HttpFoundation\Response;

class FlightController extends Controller
{
    use FormatTrait;
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
        $flight->update($request->all());
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Flight $flight)
    {
        // not managed in the back-end
    }

    public function search_engine(FlightRequest $request)
    {
        // Extract search parameters from the request
        $response = $request->all();
        $tail_number = $response['tail_number'] ?? null;
        $date = $response['flight_date_utc'] ?? null;
        $flight_number = $response['flight_number_iata'] ?? null;

        $query = Flight::query();

        if ($date) 
        {
            $query->whereDate('flight_date_utc', $date);
        }

        if ($tail_number) 
        {
            $query->where('tail_number', 'LIKE', "%{$tail_number}%");
        }

        if ($flight_number) 
        {
            $query->where('flight_number_iata', 'LIKE', "%{$flight_number}%");
        }

        // Execute the query and get results
        $results = $query->get();

        return $results;
//$this->format(['Search completed successfully', Response::HTTP_OK, FlightResource::collection($results)]);
    }
    
}
