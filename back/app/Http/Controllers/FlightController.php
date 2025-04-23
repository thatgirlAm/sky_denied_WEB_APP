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
    public function show(FlightRequest $request)
    {
        $response = FlightResource::collection($request);
        return $response; 
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
        $scheduled_departure_local = $response['scheduled_departure_local'] ?? null;
        $depart_from = $response['depart_from'] ?? null; // Airport name
        $depart_from_iata = $response['depart_from_iata'] ?? null; // IATA code
        $depart_from_icao = $response['depart_from_icao'] ?? null; // ICAO code
        $arrive_at = $response['arrive_at'] ?? null; // Airport name
        $arrive_at_iata = $response['arrive_at_iata'] ?? null; // IATA code
        $arrive_at_icao = $response['arrive_at_icao'] ?? null; // ICAO code
    
        $query = Flight::query();
    
        if ($scheduled_departure_local) {
            $query->whereDate('scheduled_departure_local', $scheduled_departure_local);
        }
    
        if ($tail_number) {
            $query->where('tail_number', 'LIKE', "%{$tail_number}%");
        }
    
        if ($flight_number) {
            $query->where('flight_number_iata', 'LIKE', "%{$flight_number}%");
        }
    
        // Search by departure airport
        if ($depart_from) {
            $query->where('depart_from', 'LIKE', "%{$depart_from}%");
        }
    
        if ($depart_from_iata) {
            $query->where('depart_from_iata', 'LIKE', "%{$depart_from_iata}%");
        }
    
        if ($depart_from_icao) {
            $query->where('depart_from_icao', 'LIKE', "%{$depart_from_icao}%");
        }
    
        // Search by arrival airport
        if ($arrive_at) {
            $query->where('arrive_at', 'LIKE', "%{$arrive_at}%");
        }
    
        if ($arrive_at_iata) {
            $query->where('arrive_at_iata', 'LIKE', "%{$arrive_at_iata}%");
        }
    
        if ($arrive_at_icao) {
            $query->where('arrive_at_icao', 'LIKE', "%{$arrive_at_icao}%");
        }
    
        // Execute the query and get results
        $results = $query->get();
    
        return $this->format(["Successfully retrieved information", Response::HTTP_OK, FlightResource::collection($results)]);
    }
    public function updateFlight(array $flightData, array $attributes)
{
    // Attempt to find the flight based on the provided criteria
    $flight = Flight::where('tail_number', $flightData['tail_number'])
                    ->where('scheduled_departure_utc', $flightData['scheduled_departure_utc'])
                    ->first();

    // If the flight is not found, return an error response or handle it
    if (!$flight) {
        throw new \Exception('Flight not found with the given criteria.');
    }

    // Update the flight with the provided attributes
    $flight->update($attributes);

    return $flight;
}

    
}
