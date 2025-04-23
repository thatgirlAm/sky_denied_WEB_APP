<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class Flight extends Model
{
    use Notifiable, HasApiTokens;

    // Table name in the database
    protected $table = 'flight_schedule';

    public $timestamps = false;

    // Defining fillable fields
    protected $fillable = [
        'flight_date',
        'flight_date_utc',
        'flight_number_iata',
        'flight_number_icao',
        'tail_number',
        'airline',
        'status',
        'depart_from',
        'depart_from_iata',
        'depart_from_icao',
        'scheduled_departure_local',
        'scheduled_departure_local_tz',
        'scheduled_departure_utc',
        'actual_departure_local',
        'actual_departure_local_tz',
        'actual_departure_utc',
        'arrive_at',
        'arrive_at_iata',
        'arrive_at_icao',
        'scheduled_arrival_local',
        'scheduled_arrival_local_tz',
        'scheduled_arrival_utc',
        'actual_arrival_local',
        'actual_arrival_local_tz',
        'actual_arrival_utc',
        'duration',
    ];


      /**
     * Find a flight based on tail number and schedule date
     *
     * @param string $tailNumber
     * @param string $scheduleDate
     * @return Flight|null
     */
    public static function findByCompositeKey($tailNumber, $scheduleDate)
    {
        return self::where('tail_number', $tailNumber)
                ->where('schedule_date_utc', $scheduleDate)
                ->first();
    }
    
    /**
     * Update a flight's status based on composite key
     *
     * @param string $tailNumber
     * @param string $scheduleDate
     * @param string $status
     * @return Flight|bool
     */
    public static function updateStatusByCompositeKey($tailNumber, $scheduleDate, $status)
    {
        $flight = self::findByCompositeKey($tailNumber, $scheduleDate);
        
        if (!$flight) {
            return false;
        }
        
        $flight->status = $status;
        $flight->save();
        
        return $flight;
    }
}

