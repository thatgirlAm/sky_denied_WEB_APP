<?php

namespace App\Http\Controllers;

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

    // function to trigger the data python script and crawl the data
    public function crawling_trigger(CrawlingRequest $crawling_request)
    {
        $tail_number = $crawling_request->route('tail_number');
        $mode = "real_time" ; 
        // TODO: change the path
        $script_path = base_path('../data/main.py') ; 
        $data = json_encode([[
            'aircraft' => $tail_number,
            'mode' => $mode
        ]]);
        // TODO: change the python path
        $process = new Process(['python3', $script_path, $data]);
        $process->setTimeout(120);

        try 
        {
            $process->mustRun();
            $output = json_decode($process->getOutput(), true);
            if (json_last_error() !== JSON_ERROR_NONE) {
                Log::error("JSON decode error: " . json_last_error_msg());
                return $this->format_error('Error parsing script output: ' . json_last_error_msg(), Response::HTTP_INTERNAL_SERVER_ERROR);
            }
            return $this->format(['Script Run successfully', Response::HTTP_OK, $output]);
        } 
        catch (ProcessFailedException $e) 
        {
            return $this->format_error('Script did not run: ' . $e->getMessage(), Response::HTTP_INTERNAL_SERVER_ERROR);
        }
            
    }

    // function to handle the data resizing                   
    public function data_handling(Request $request)
    {
    $response = $request->all(); 
    $flights = $response['flights'] ?? []; // Extracting flights from request data
    $result = [];
    if ($response['status'] == Response::HTTP_OK) {
        foreach ($flights as $index => $flight) {
            if ($flight['flag'] == '1') {
                // Adding the flagged flight (flag to know which flight is the predicted one)
                $result[] = $flight;

                // Add the 3 preceding flights
                for ($i = 1; $i <= 3; $i++) {
                    if (isset($flights[$index - $i])) 
                    {
                        $result[] = $flights[$index - $i];
                    }
                }
                break; 
            }
        }
        // Return the result in array(JSON) 
        return array(response()->json(['data' => $result], Response::HTTP_OK));
    } else 
    {
        return $this->format_error('Crawling data from flight went wrong', Response::HTTP_INTERNAL_SERVER_ERROR);
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
