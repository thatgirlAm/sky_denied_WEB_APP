<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class CrawlingRequest extends FormRequest
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
            'mode' => 'required|string|in:realtime,scheduled',
            'tail_number' => 'required_if:mode,realtime|string',
            'main_scheduled_departure_utc' => 'required_if:mode,realtime|string',
            'airport_list_iata' => 'required_if:mode,scheduled|array',
            'airport_list_iata.*' => 'string',
        ];
    }
}
