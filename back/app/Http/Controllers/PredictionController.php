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
use Illuminate\Process\Exceptions\ProcessFailedException;
use App\Models\Flight;
use Illuminate\Support\Facades\Log; 


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
        //
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

   /**
 * Main method to trigger crawling process
 */
public function crawling_trigger(CrawlingRequest $crawling_request)
{
    // Retrieve parameters from the request
    $response = $crawling_request->all();
    $mode = $response['mode'];
    
    // Construct the JSON data based on mode
    $jsonData = [];
    
    if ($mode === 'realtime') {
        $tail_number = $response['tail_number'];
        $main_flight_date_utc = $response['main_scheduled_departure_utc'];
        
        $jsonData = [[
            'aircraft' => $tail_number,
            'mode' => $mode
        ]];
    } elseif ($mode === 'scheduled') {
        // For scheduled mode, we need airport list
        $airport_list_iata = $response['airport_list_iata'] ?? [];
        
        $jsonData = [[
            'mode' => $mode,
            'airport_list_iata' => $airport_list_iata
        ]];
    } else {
        return $this->format_error(
            'Invalid mode specified. Supported modes are "realtime" and "scheduled".',
            Response::HTTP_BAD_REQUEST
        );
    }
    
    // Encode the data for the Python script
    $data = json_encode($jsonData);

    // Determine the script path using a relative path
    $script_path = base_path('../data/main.py');

    // Define the Python process
    $process = new Process(['python3', $script_path, $data]);
    $process->setTimeout(300); // Increased timeout for scheduled mode which may take longer

    try {
        // Run the process
        $process->mustRun();

        // Trim the output and log it for debugging
        $output = trim($process->getOutput());
        \Log::info("Raw Python output: " . $output);

        // Decode the JSON output
        $flights_information = json_decode($output, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            \Log::error("JSON decode error: " . json_last_error_msg());
            \Log::error("Raw output: " . $output);
            return $this->format_error(
                'Error parsing script output: ' . json_last_error_msg(),
                Response::HTTP_INTERNAL_SERVER_ERROR
            );
        }
       
        // Structure the result as desired
        $result = [];
        if ($mode === 'realtime') {
            $main_flight_date_utc = $response['main_scheduled_departure_utc'];
            $result = [
                [
                    'flights' => $flights_information,
                    'main_flight_date' => $main_flight_date_utc
                ]
            ];
        } else {
            // For scheduled mode, update the database with flight information
            $saveStats = $this->saveFlightsToDatabase($flights_information);
            \Log::info("Database updated with flights. Created: {$saveStats['created']}, Updated: {$saveStats['updated']}, Skipped: {$saveStats['skipped']}, Errors: {$saveStats['errors']}");
            
            // Return the flight information and stats
            $result = [
                'flights' => $flights_information,
                'db_stats' => $saveStats
            ];
        }

        // Return success response
        return $this->format(['Script ran successfully', Response::HTTP_OK, $result]);

    } catch (ProcessFailedException $e) {
        // Log and handle process failure
        \Log::error("Python script failed: " . $e->getMessage());
        return $this->format_error(
            'Script did not run: ' . $e->getMessage(),
            Response::HTTP_INTERNAL_SERVER_ERROR
        );

    } catch (\Exception $e) {
        // Log and handle other exceptions
        \Log::error("Unexpected error: " . $e->getMessage());
        return $this->format_error(
            'An unexpected error occurred: ' . $e->getMessage(),
            Response::HTTP_INTERNAL_SERVER_ERROR
        );
    }
}

/**
 * Save or update flights in the database
 * 
 * @param array $flightsData Decoded JSON data from the Python script
 * @return array Statistics on the database operation
 */
public function saveFlightsToDatabase($flightsData)
{
    // Track stats for logging
    $stats = [
        'created' => 0,
        'updated' => 0,
        'skipped' => 0,
        'errors' => 0
    ];
    
    // Process each flight
    foreach ($flightsData as $flightData) {
        try {
            // Check if we have a valid flight
            if (!isset($flightData['flight_number_iata']) || 
                !isset($flightData['scheduled_departure_utc']) ||
                !isset($flightData['flight_date'])) {
                $stats['skipped']++;
                continue;
            }
            
            // Create a unique identifier for the flight
            $criteria = [
                'flight_number_iata' => $flightData['flight_number_iata'],
                'flight_date' => $flightData['flight_date'],
                'scheduled_departure_utc' => $flightData['scheduled_departure_utc']
            ];
            
            // Try to find an existing flight
            $flight = \App\Models\Flight::where($criteria)->first();
            
            if ($flight) {
                // Update existing flight
                $flight->fill($flightData);
                $flight->save();
                $stats['updated']++;
            } else {
                // Create new flight
                \App\Models\Flight::create($flightData);
                $stats['created']++;
            }
        } catch (\Exception $e) {
            \Log::error("Error saving flight data: " . $e->getMessage());
            $stats['errors']++;
        }
    }
    
    return $stats;
}

    
    
    // function to handle the data resizing                   
    public function data_handling(DatahandlingRequest $request)
    {
        // Extract the response body from the request
        $response = $request->all(); 
        
        // Ensure 'data' key exists and is an array
        $flights = $response['data']['flights'] ?? []; 
        $main_scheduled_departure_utc = $response["data"]["main_scheduled_departure_utc"];
        //return $flights ; 
        $result = [];
        
        // Check if the response status is HTTP_OK
        if ($response['status'] == Response::HTTP_OK) {
            $result = [];
            foreach ($flights as $i => $flight) {
                if ($flight['scheduled_departure_utc'] === $main_scheduled_departure_utc) {
                    $result[] = $flight;
                    for ($j = 1; $j <= 3; $j++) {
                        if (isset($flights[$i - $j])) {
                            $result[] = $flights[$i - $j];
                        }
                    }
                    break;
                }
            }
        
            // if nothing matched, return a clear NO_CONTENT error
            if (empty($result)) {
                return $this->format_error(
                    'No flight corresponds to the given UTC date/time',
                    Response::HTTP_NO_CONTENT
                );
            }
        
            // otherwise return your standard success shape
            return $this->format(['success', Response::HTTP_OK, $result]);
        }
    }
    



    // function to trigger the model 
    public function model_trigger(ModelRequest $model_request)
    {
        // data is an array with 2 json files: one for flight information and one for weather information 
        $data = json_encode($model_request['data']);

        // TODO: replace by model's path
        $script_path = base_path('../test/model.py') ; 
        $process = new Process(['python3', $script_path, $data]);
        try
        {
            $process->run();
            return json_decode($process->getOutput(), true);
        }
        catch (\Exception $e) 
        {
            return $this->format_error('Model did not run', Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    // function to test out crawling and data handling
    public function crawling_handling_test(CrawlingRequest $request)
    {
        // 1) Run the crawler and get its JSON‑response
        $crawlingResponse = $this->crawling_trigger($request);
    
        // 2) Decode the raw JSON
        $raw     = $crawlingResponse->getContent();
        $decoded = json_decode($raw, true);
    
        if (json_last_error() !== JSON_ERROR_NONE) {
            return $this->format_error(
                'Invalid JSON from crawling_trigger: '.json_last_error_msg(),
                Response::HTTP_INTERNAL_SERVER_ERROR
            );
        }
    
        // 3) Did it succeed?
        $status = $decoded['status'] ?? null;
        if ($status !== Response::HTTP_OK) {
            // propagate the failure message/status
            return $this->format_error(
                $decoded['message']    ?? 'crawling_trigger failed',
                $decoded['status']     ?? Response::HTTP_INTERNAL_SERVER_ERROR
            );
        }
    
        // 4) Pull out the first (and only) element in data[]
        if (
            ! isset($decoded['data'][0]['flights'], $decoded['data'][0]['main_flight_date'])
        ) {
            return $this->format_error(
                'Unexpected payload shape from crawling_trigger',
                Response::HTTP_INTERNAL_SERVER_ERROR
            );
        }
    
        $flights = $decoded['data'][0]['flights'];
        $mainUtc = $decoded['data'][0]['main_flight_date'];
    
        // 5) Build the exact payload your Datahandling_request expects
        $payload = [
            'status' => Response::HTTP_OK,
            'data'   => [
                'main_scheduled_departure_utc' => $mainUtc,
                'flights'                     => $flights,
            ],
        ];
    
        // 6) Instantiate & populate the FormRequest
        $handling_request = new DataHandlingRequest();
        $handling_request->merge($payload);
    
        // 7) Dispatch to data_handling() and return its response
        return $this->data_handling($handling_request);
    }
    
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
            return $output;
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
    
    
    public function trigger(CrawlingRequest $crawlingRequest)
    {
        try 
        {        
        $data = $this->crawling_trigger($crawlingRequest)['data'];
        $data_formatted = $this->data_handling($data); 
        $prediction_data = $this->model_trigger($data_formatted)['prediction']; 
        $flight_data = $data_formatted['flight_information'][0]; 
        $status = $prediction_data['status'];

        try 
        {
            // error handling
            if (!$flight_data) {
                return $this->format_error('Flight data is missing', Response::HTTP_BAD_REQUEST);
            }
            $flight = Flight::where('id', $flight_data['id'])->first();
            // error handling
            if (!$flight) {
                return $this->format_error('Flight not found', Response::HTTP_NOT_FOUND);
            }
            $prediction = Prediction::where('id', $prediction_data['id'])->first();
            // error handling   
            if (!$prediction) {
                return $this->format_error('Prediction not found', Response::HTTP_NOT_FOUND);
            }

            // Updating the DB
            $flight->update($status, $flight_data);
            $prediction->update($prediction_data, $prediction_data);

            return $this->format(['Prediction OK', Response::HTTP_OK, $prediction]);
        }
        catch (ProcessFailedException $e)
        {
            return $this->format_error('The scheme did not run', Response::HTTP_INTERNAL_SERVER_ERROR);
        }
        }
    
    catch (ProcessFailedException $e)
    {
        return $this->format_error('Prediction did not run', Response::HTTP_INTERNAL_SERVER_ERROR);
    }
}
}
