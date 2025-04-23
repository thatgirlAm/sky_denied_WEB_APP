<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class DataHandlingRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'status' => 'required|integer|in:200', // Validate status is 200
            'data' => 'required|array', // Ensure data is an array
            'data.main_scheduled_departure_utc' => 'required|date_format:Y-m-d H:i', // Validate UTC format
            'data.flights' => 'required|array', // Ensure flights is an array
            //'data.flights.*.scheduled_departure_utc' => 'required|date_format:Y-m-d H:i', // Validate each flight's UTC field
        ];
    }
    
}
