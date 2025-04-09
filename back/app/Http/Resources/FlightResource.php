<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class FlightResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'flight_date' => $this->flight_date,
            'flight_date_utc' => $this->flight_date_utc,
            'flight_number_iata' => $this->flight_number_iata,
            'flight_number_icao' => $this->flight_number_icao,
            'tail_number' => $this->tail_number,
            'airline' => $this->airline,
            'status' => $this->status,
            'depart_from' => $this->depart_from,
            'depart_from_iata' => $this->depart_from_iata,
            'depart_from_icao' => $this->depart_from_icao,
            'scheduled_departure_local' => $this->scheduled_departure_local,
            'scheduled_departure_local_tz' => $this->scheduled_departure_local_tz,
            'scheduled_departure_utc' => $this->scheduled_departure_utc,
            'actual_departure_local' => $this->actual_departure_local,
            'actual_departure_local_tz' => $this->actual_departure_local_tz,
            'actual_departure_utc' => $this->actual_departure_utc,
            'arrive_at' => $this->arrive_at,
            'arrive_at_iata' => $this->arrive_at_iata,
            'arrive_at_icao' => $this->arrive_at_icao,
            'scheduled_arrival_local' => $this->scheduled_arrival_local,
            'scheduled_arrival_local_tz' => $this->scheduled_arrival_local_tz,
            'scheduled_arrival_utc' => $this->scheduled_arrival_utc,
            'actual_arrival_local' => $this->actual_arrival_local,
            'actual_arrival_local_tz' => $this->actual_arrival_local_tz,
            'actual_arrival_utc' => $this->actual_arrival_utc,
            'duration' => $this->duration,
        ];
    }
}
