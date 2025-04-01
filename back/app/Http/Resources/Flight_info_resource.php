<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class Flight_info_resource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [

            'flight_id' => $this->flight_id,
            'destination_code' => $this->destiantion_code,
            'origin_code' => $this->origin_code,
            'airline_code'=> $this->airline_code,

            // TO FIX: typo
            'flightnumber' => $this->flightnumber,
            
        ];  
    }
}
