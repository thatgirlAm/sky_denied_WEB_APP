<?php

namespace Tests\Unit;

use Tests\TestCase;
use App\Models\Flight;
use App\Http\Controllers\PredictionController;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Log;

class PredictionControllerTest extends TestCase
{
    use RefreshDatabase;

    protected function validFlightData($overrides = [])
    {
        return array_merge([
            'flight_number_iata' => 'FL123',
            'flight_date' => '2025-04-21',
            'scheduled_departure_utc' => '2025-04-21 08:00:00',
            'depart_from_iata' => 'JFK',
            'arrive_at_iata' => 'LAX',
            'airline' => 'Test Airways',
            'scheduled_arrival_utc' => '2025-04-21 11:00:00',
            'duration' => '3h'
        ], $overrides);
    }

    /** @test */
    public function it_creates_new_flights_via_controller()
    {
        $controller = new PredictionController();
        $flightData = $this->validFlightData();
        
        $stats = $controller->saveFlightsToDatabase([$flightData]);

        $this->assertEquals(1, $stats['created']);
        $this->assertDatabaseCount('flight_schedule', 1);
        $this->assertDatabaseHas('flight_schedule', $flightData);
    }

    /** @test */
    public function it_updates_existing_flights_via_controller()
    {
        $controller = new PredictionController();
        $existing = Flight::create($this->validFlightData());
        
        $updateData = $this->validFlightData([
            'airline' => 'Updated Airways',
            'status' => 'Delayed'
        ]);

        $stats = $controller->saveFlightsToDatabase([$updateData]);

        $this->assertEquals(1, $stats['updated']);
        $this->assertDatabaseHas('flight_schedule', [
            'id' => $existing->id,
            'airline' => 'Updated Airways',
            'status' => 'Delayed'
        ]);
    }

  

    protected function saveFlightsToDatabase($data)
    {
        // Direct controller instance creation
        $controller = new PredictionController();
        return $controller->saveFlightsToDatabase($data);
    }
}   