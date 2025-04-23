<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Prediction extends Model
{
    protected $fillable=[
        "flight_id", 
        "delayed",
        "previous_prediction",
        "accuracy"
    ];


    public static function updateOrCreatePrediction(array $data)
    {
        return self::updateOrCreate(
            [
                'tail_number' => $data['tail_number'],
                'schedule_date_utc' => $data['schedule_date_utc']
            ],
            [
                'delayed' => $data['delayed'],
                'previous_prediction' => $data['previous_prediction'],
                'accuracy' => $data['accuracy']
            ]
        );
    }
    
    /**
     * Calculate and update the accuracy when actual results are known
     *
     * @param bool $actualDelayed The actual delayed status
     * @return Prediction
     */
    public function updateAccuracy(bool $actualDelayed)
    {
        // Calculate accuracy (1 if prediction matches actual, 0 if not)
        $this->accuracy = ($this->delayed === $actualDelayed) ? 1.0 : 0.0;
        $this->save();
        
        return $this;
    }
}
