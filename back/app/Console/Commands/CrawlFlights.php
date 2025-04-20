<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Http\Controllers\PredictionController;
use App\Http\Requests\CrawlingRequest;
use Illuminate\Http\Request;

class CrawlFlights extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'crawl:flights {--airports=* : List of airport IATA codes to crawl} {--debug : Enable detailed debugging}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Run the scheduled flight crawling process and update the database';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $this->info('Starting scheduled flight crawling...');
        
        $debug = $this->option('debug');
        
        try {
            // Get airports from command options or use defaults
            $airports = $this->option('airports');
            if (empty($airports)) {
                $airports = ["NCL", "DUB"]; // Default airports if none specified
            }
            
            $this->info('Crawling airports: ' . implode(', ', $airports));
            
            $controller = app()->make(PredictionController::class);
            
            // Create a mock request with the necessary data
            $mockRequest = new Request();
            $mockRequest->merge([
                'mode' => 'scheduled',
                'airport_list_iata' => $airports
            ]);
            
            if ($debug) {
                $this->info('Request data: ' . json_encode($mockRequest->all()));
            }
            
            // Convert to your custom request class
            // Check if we can create the CrawlingRequest directly
            try {
                $crawlingRequest = new CrawlingRequest($mockRequest->all());
            } catch (\Exception $e) {
                $this->error("Failed to create CrawlingRequest: " . $e->getMessage());
                
                // Try the createFrom method as alternative
                $crawlingRequest = CrawlingRequest::createFrom($mockRequest);
            }
            
            // Execute the controller method
            $result = $controller->crawling_trigger($crawlingRequest);
            
            // Dump raw response for debugging if enabled
            if ($debug) {
                $this->info('Raw response: ' . $result->getContent());
            }
            
            // Check result status
            $resultData = json_decode($result->getContent(), true);
            
            if ($debug) {
                $this->info('Decoded response: ' . print_r($resultData, true));
            }
            
            if (isset($resultData['status']) && $resultData['status'] === 200) {
                $data = $resultData['data'][2] ?? null;
                
                if ($debug && !$data) {
                    $this->warn('No data found in response at index 2');
                    $this->info('Full response structure: ' . print_r($resultData, true));
                }
                
                // Display database update stats if available
                if (isset($data['db_stats'])) {
                    $stats = $data['db_stats'];
                    
                    $this->info("Flight database update completed:");
                    $this->info("- Created: {$stats['created']}");
                    $this->info("- Updated: {$stats['updated']}");
                    $this->info("- Skipped: {$stats['skipped']}");
                    $this->info("- Errors: {$stats['errors']}");
                } else if ($debug) {
                    $this->warn('No db_stats found in response data');
                }
                
                // Display flight information if available
                if (isset($data['flights'])) {
                    $flightsCount = is_array($data['flights']) ? count($data['flights']) : 0;
                    $this->info("Retrieved {$flightsCount} flights");
                } else if ($debug) {
                    $this->warn('No flights found in response data');
                }
                
                $this->info('Flight crawling completed successfully!');
            } else {
                $errorMessage = $resultData['message'] ?? 'Unknown error';
                $this->error('Flight crawling failed: ' . $errorMessage);
            }
            
        } catch (\Exception $e) {
            $this->error('Flight crawling failed with exception: ' . $e->getMessage());
            if ($debug) {
                $this->error('Stack trace: ' . $e->getTraceAsString());
            }
        }
    }
}