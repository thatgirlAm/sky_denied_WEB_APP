<?php

namespace App\Http\Controllers;

use App\Http\Requests\DataHandlingRequest;
use App\Models\Prediction;
use Illuminate\Http\Request;
use \App\Http\Requests\CrawlingRequest ; 
use \App\Http\Requests\ModelRequest; 
use PhpParser\Node\Stmt\Catch_;
use Symfony\Component\Process\Process;
use Symfony\Component\HttpFoundation\Response;
use App\Models\Flight;
use Illuminate\Support\Facades\Log; 
use Illuminate\Support\Facades\Http;   
//use DateTime;

class PredictionController extends Controller
{
    use FormatTrait;
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        //
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $input = $request->all();
        $input["tail_number"] = $request->input("tail_number");
        $value = $request->input("value", "");
        $input["delayed"] = !str_contains($value, "Delayed");
        $input["previous_prediction"] = "On time";
        $input["schedule_date_utc"] = $request->input("schedule_date_utc");
        $input["accuracy"] = "";
        return $this->format(["Success", Response::HTTP_OK,Prediction::create($input)]);
    }
    
    /**
     * Display the specified resource.
     */
    public function show(Prediction $prediction)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(Prediction $prediction)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Prediction $prediction)
    {
        $prediction->update($request->all());
        return $this->format(['success', Response::HTTP_OK, $prediction]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Prediction $prediction)
    {
        $prediction->delete();
    }

    // function to handle data crawling in real time
    public function crawling_trigger(CrawlingRequest $crawling_request)
    {
        // Retrieve parameters from the request
        $response = $crawling_request->all();
        $tail_number = $response['tail_number'];
        $main_flight_date_utc = $response['main_scheduled_departure_utc'];
    
        // Construct the JSON data to be passed to the API
        $queryParams = [
            'aircraft' => $tail_number,
        ];
    
        // Define the API URL
        $ip = "172.179.154.4";
        $api_url = 'http://' . $ip . ':8000/realtime';
    
        try {
            // Call the API with a timeout
            $response = \Http::timeout(120)->get($api_url, $queryParams);
    
            // Check for HTTP errors
            if ($response->failed()) {
                \Log::error("API call failed: " . $response->status());
                return $this->format_error(
                    'API call failed with status: ' . $response->status(),
                    Response::HTTP_INTERNAL_SERVER_ERROR
                );
            }
    
            // Decode the JSON response
            $flights_information = $response->json();
            if (json_last_error() !== JSON_ERROR_NONE) {
                \Log::error("JSON decode error: " . json_last_error_msg());
                return $this->format_error(
                    'Error parsing API response: ' . json_last_error_msg(),
                    Response::HTTP_INTERNAL_SERVER_ERROR
                );
            }
    
            // Extract relevant flight data
            $flight_data = $flights_information['response']['data'] ?? [];
            $processed_flights = [];
            foreach ($flight_data as $flight) {
                $processed_flights[] = [
                    'flight_date' => $flight['flight_date'] ?? null,
                    'flight_date_utc' => $flight['flight_date_utc'] ?? null,
                    'flight_number_iata' => $flight['flight_number_iata'] ?? null,
                    'flight_number_icao' => $flight['flight_number_icao'] ?? null,
                    'tail_number' => $flight['tail_number'] ?? null,
                    'airline' => $flight['airline'] ?? null,
                    'status' => $flight['status'] ?? null,
                    'depart_from' => $flight['depart_from'] ?? null,
                    'depart_from_iata' => $flight['depart_from_iata'] ?? null,
                    'depart_from_icao' => $flight['depart_from_icao'] ?? null,
                    'scheduled_departure_local' => $flight['scheduled_departure_local'] ?? null,
                    'scheduled_departure_local_tz' => $flight['scheduled_departure_local_tz'] ?? null,
                    'scheduled_departure_utc' => $flight['scheduled_departure_utc'] ?? null,
                    'actual_departure_local' => $flight['actual_departure_local'] ?? null,
                    'actual_departure_local_tz' => $flight['actual_departure_local_tz'] ?? null,
                    'actual_departure_utc' => $flight['actual_departure_utc'] ?? null,
                    'arrive_at' => $flight['arrive_at'] ?? null,
                    'arrive_at_iata' => $flight['arrive_at_iata'] ?? null,
                    'arrive_at_icao' => $flight['arrive_at_icao'] ?? null,
                    'scheduled_arrival_local' => $flight['scheduled_arrival_local'] ?? null,
                    'scheduled_arrival_local_tz' => $flight['scheduled_arrival_local_tz'] ?? null,
                    'scheduled_arrival_utc' => $flight['scheduled_arrival_utc'] ?? null,
                    'actual_arrival_local' => $flight['actual_arrival_local'] ?? null,
                    'actual_arrival_local_tz' => $flight['actual_arrival_local_tz'] ?? null,
                    'actual_arrival_utc' => $flight['actual_arrival_utc'] ?? null,
                    'duration' => $flight['duration'] ?? null,
                ];
                
            }
    
            // Structure the result as desired
            $result = [
                'main_scheduled_departure_utc' => $main_flight_date_utc,
                'flights' => $processed_flights,
            ];
    
            // Return success response
            return $this->format(['API call successful', Response::HTTP_OK, $result]);
    
        } catch (\Exception $e) {
            // Log and handle unexpected errors
            \Log::error("Unexpected error: " . $e->getMessage());
            return $this->format_error(
                'An unexpected error occurred: ' . $e->getMessage(),
                Response::HTTP_INTERNAL_SERVER_ERROR
            );
        }
    }
    

    
    
    // function to handle the data resizing                   
    public function data_handling(DatahandlingRequest $request)
    {
        $response = $request->all(); 
        $flights = $response['data']['flights'] ?? [];
        $main_scheduled_departure_utc = $response["data"]["main_scheduled_departure_utc"];
        $result = [];
        //return $flights;
        if ($response['status'] == Response::HTTP_OK) {
            // Find matching flight and previous 3 flights
            foreach ($flights as $i => $flight) {
                //printf($flight['scheduled_departure_utc'] . " " .  "\n" );
                if ($flight['scheduled_departure_utc'] === $main_scheduled_departure_utc) {
                    // Add matching flight and previous 3 flights
                    $result[] = $flight;
                    for ($j = 3; $j >= 1; $j--) {
                        if (isset($flights[$i + $j])) {
                            $result[] = $flights[$i + $j];
                        }
                    }
                    break;
                }
            }
    
            // Add reporting_airline to filtered flights
            foreach ($result as &$flight) {
                $flightNumberIata = $flight['flight_number_iata'] ?? '';
                $flight['reporting_airline'] = substr($flightNumberIata, 0, 2);
            }
            unset($flight); // Break the reference
    
            if (empty($result)) {
                return $this->format_error(
                    'No flight corresponds to the given UTC date/time',
                    Response::HTTP_NO_CONTENT
                );
            }
    
            return $this->format([
                'success',
                Response::HTTP_OK,
                $result
                 
            ]);
        }
    }


    // TODO: Test this
    // function to trigger the model 
    public function model_trigger(ModelRequest $model_request)
    {
        // Extract data from the request
        $data = $model_request['data'];
    
        // TODO: Replace with the actual API endpoint URL
        $ip = "4.149.171.79";
        $api_url = 'http://'.$ip.':8000/predict';
    
        try 
        {
            // Send a POST request to the API with the data
            $response = Http::post($api_url, $data);
            if ($response->successful()) 
            {
                return $response->json(); 
            } 
            else 
            {
                return $this->format_error(
                    'Model API returned an error: ' . $response->body(), 
                    $response->status()
                );
            }
        } 
        catch (\Exception $e) 
        {
            return $this->format_error(
                'Model API call failed: ' . $e->getMessage(), 
                Response::HTTP_INTERNAL_SERVER_ERROR
            );
        }
    }

    // // function to test out crawling and data handling
    // public function crawling_handling_test(CrawlingRequest $request)
    // {
    //     // 1) Run the crawler and get its JSON‑response
    //     $crawlingResponse = $this->crawling_trigger($request);
    
    //     // 2) Decode the raw JSON
    //     $raw     = $crawlingResponse->getContent();
    //     $decoded = json_decode($raw, true);
    
    //     if (json_last_error() !== JSON_ERROR_NONE) {
    //         return $this->format_error(
    //             'Invalid JSON from crawling_trigger: '.json_last_error_msg(),
    //             Response::HTTP_INTERNAL_SERVER_ERROR
    //         );
    //     }
    
    //     // 3) Did it succeed?
    //     $status = $decoded['status'] ?? null;
    //     if ($status !== Response::HTTP_OK) {
    //         // propagate the failure message/status
    //         return $this->format_error(
    //             $decoded['message']    ?? 'crawling_trigger failed',
    //             $decoded['status']     ?? Response::HTTP_INTERNAL_SERVER_ERROR
    //         );
    //     }
    
    //     // 4) Pull out the first (and only) element in data[]
    //     if (
    //         ! isset($decoded['data']['flights'][0], $decoded['data'][0]['main_scheduled_departure_utc'])
    //     ) {
    //         return $this->format_error(
    //             'Unexpected payload shape from crawling_trigger',
    //             Response::HTTP_INTERNAL_SERVER_ERROR
    //         );
    //     }
    
    //     $flights = $decoded['data'][0]['flights'];
    //     $mainUtc = $decoded['data'][0]['main_flight_date'];
    
    //     // 5) Build the exact payload your Datahandling_request expects
    //     $payload = [
    //         'status' => Response::HTTP_OK,
    //         'data'   => [
    //             'main_scheduled_departure_utc' => $mainUtc,
    //             'flights'                     => $flights,
    //         ],
    //     ];
    
    //     // 6) Instantiate & populate the FormRequest
    //     $handling_request = new DataHandlingRequest();
    //     $handling_request->merge($payload);
    
    //     // 7) Dispatch to data_handling() and return its response
    //     return $this->data_handling($handling_request);
    // }
    
    public function model_testing(ModelRequest $request)
    {
        $data = $request['data']; 
        //return $data;
        $script_path = base_path('../model/run_inference.py') ; 
        $json_data = json_encode($data, true); 
        $process = new Process(['python3', $script_path, '--flights-cli', $json_data]);
        try 
        {
            $process->run();
            $output = $process->getOutput();
            return json_encode($output);
        }
        catch (\Exception $e)
        {
            return $this->format_error("Error: " .$e, Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }
    /*
    public function model_trigger_test()
    {
        // data is an array with 2 json files: one for flight information and one for weather information 
        // $data = json_encode($model_request['data']);
        $tail_number = '12HBDN';
        $crawlingRequest = new CrawlingRequest(['tail_number' => $tail_number]);
        $data = $this->crawling_trigger($crawlingRequest);
        $response_data = $data->getData();
        $data_array = json_decode(json_encode($response_data), true); 
        $data_formatted = $this->data_handling(new Request($data_array));

        $data_array_passed= json_encode($data_formatted);
        // TODO: replace by model's path
        $script_path = base_path('../test/model_test.py') ; 
        $process = new Process(['/Library/Frameworks/Python.framework/Versions/3.12/bin/python3', $script_path, $data_array_passed]);
        try
        {
            $process->run();
            return json_decode($process->getOutput(), true);
        }
        catch (\Exception $e) 
        {
            return $this->format_error('Model did not run : ' .$e, Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    // function to trigger the whole prediction scheme
    */

    // TODO: Test this
    public function trigger(CrawlingRequest $crawlingRequest)
    {
        try {
            // Step 1: Trigger the crawling process
            $crawlingResponse = $this->crawling_trigger($crawlingRequest);
      
            $dataHandlingRequest = new DataHandlingRequest([
                'message' => $crawlingResponse->original['message'],
                'status' => $crawlingResponse->original['status'],
                'data' => $crawlingResponse->original['data']
            ]);
           
            // Step 2: Pre-processing the data to only pass the 3 precedent flights
            $dataFormatted = $this->data_handling($dataHandlingRequest);
            //return $dataFormatted;
            $modelTriggerRequest = new ModelRequest([
                'message' => $dataFormatted->original['message'],
                'status' => $dataFormatted->original['status'],
                'data' => $dataFormatted->original['data']
            ]);
            
            // Step 3: Trigger the model prediction process
            $modelResponse = $this->model_trigger($modelTriggerRequest);
            
            // Step 4: Extract flight data from formatted data
            if (empty($dataFormatted->original['data']) || !isset($dataFormatted->original['data'][0])) {
                return $this->format_error('Flight data is missing', Response::HTTP_BAD_REQUEST);
            }
            $flightData = $dataFormatted->original['data'][0];
            //return $flightData;
           $flightData['scheduled_departure_utc'] .= ':00';
           //return $flightData['scheduled_departure_utc'];
            // Get flight from database or return error if not found
            // $flight = Flight::where('tail_number', $flightData['tail_number'])
            //         ->where('scheduled_departure_utc', $flightData['scheduled_departure_utc'])
            //         ->first();
            //return $flight;
            // if (!$flight) {
            //     return $this->format_error('Flight not found in database', Response::HTTP_NOT_FOUND);
            // }
            
            // Step 5: Determine if the flight is delayed based on model response
            $isDelayed = $modelResponse['value'] !== 'On Time / Slight Delay (<= 15 min)';
            
            // Step 6: Prepare the prediction data for the database
            $predictionDataDB = [
                'tail_number' => $flightData['tail_number'], 
                'delayed' => $isDelayed,
                'value' => $modelResponse['value'], 
                'previous_prediction' => null, 
                'accuracy' => null, 
                'schedule_date_utc' => $flightData['scheduled_departure_utc']
            ];
            
            //return $predictionDataDB;
            // Step 7: Create or update prediction in database
            $prediction = Prediction::where('tail_number', $flightData['tail_number'])
                       ->where('schedule_date_utc', $flightData['scheduled_departure_utc'])
                       ->first();
            //return $prediction; 
            if ($prediction) {
                $predictionDataDB['previous_prediction'] = $prediction->value;
                $prediction->update($predictionDataDB);
            } else {
                $prediction = Prediction::create($predictionDataDB);
            }
            
            // Step 9: Format the response to match your Prediction interface
            $responseData = [
                'message' => 'Prediction completed successfully',
                'status' => $modelResponse['status'],
                'value' => $modelResponse['value'],
                'tail_number' => $flightData['tail_number'],
                'delayed' => $isDelayed,
                'previous_predicition' => $predictionDataDB['previous_prediction'],
                'schedule_date_utc' => $flightData['scheduled_departure_utc']
            ];
    
    
            return $this->format(["Success", Response::HTTP_OK, $responseData]);
    
        } catch (\Exception $e) {
            // Handle any other exceptions during the entire process
            return $this->format_error('An error occurred during the prediction process: ' . $e->getMessage(), Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }
}
