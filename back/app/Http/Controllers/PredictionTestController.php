<?php
// Generated with AI

//TODO review this
namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Prediction;
use App\Models\Flight;

class PredictionControllerTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test the update function for a Prediction.
     */
    public function test_update_prediction()
    {
        $prediction = Prediction::factory()->create();
        $data = [
            'status' => 'updated_status',
            'value' => 42, // Adjust based on your Prediction model's structure
        ];

        $response = $this->putJson(route('predictions.update', $prediction->id), $data);

        $response->assertStatus(200)
                 ->assertJson([
                     'success' => true,
                     'data' => $data,
                 ]);

        $this->assertDatabaseHas('predictions', $data);
    }

    /**
     * Test the crawling_trigger function.
     */
    public function test_crawling_trigger()
    {
        $data = ['tail_number' => 'ABC123'];
        $response = $this->postJson(route('predictions.crawling_trigger'), $data);

        $response->assertStatus(200)
                 ->assertJsonStructure([
                     'message',
                     'status',
                     'data' => [
                         '*' => ['field1', 'field2'], // Adjust based on your script output
                     ],
                 ]);
    }

    /**
     * Test the data_handling function.
     */
    public function test_data_handling()
    {
        $data = [
            'status' => 200,
            'flights' => [
                ['id' => 1, 'flag' => '1'],
                ['id' => 2, 'flag' => '0'],
                ['id' => 3, 'flag' => '0'],
            ],
        ];

        $response = $this->postJson(route('predictions.data_handling'), $data);

        $response->assertStatus(200)
                 ->assertJsonStructure([
                     'data' => [
                         '*' => ['id', 'flag'],
                     ],
                 ]);
    }

    /**
     * Test the model_trigger function.
     */
    public function test_model_trigger()
    {
        $data = [
            'data' => [
                'flight_info' => ['field1' => 'value1'],
                'weather_info' => ['field1' => 'value1'],
            ],
        ];

        $response = $this->postJson(route('predictions.model_trigger'), $data);

        $response->assertStatus(200)
                 ->assertJsonStructure([
                     'prediction' => ['field1', 'field2'], // Adjust based on model output
                 ]);
    }

    /**
     * Test the trigger function for the complete prediction scheme.
     */
    public function test_trigger_prediction_scheme()
    {
        $crawlingRequest = [
            'tail_number' => 'ABC123',
        ];

        $response = $this->postJson(route('predictions.trigger'), $crawlingRequest);

        $response->assertStatus(200)
                 ->assertJsonStructure([
                     'message',
                     'status',
                     'data' => ['field1', 'field2'], // Adjust based on final output
                 ]);
    }

    /**
     * Test validation for the crawling_trigger endpoint.
     */
    public function test_crawling_trigger_validation()
    {
        $data = []; // Missing required tail_number

        $response = $this->postJson(route('predictions.crawling_trigger'), $data);

        $response->assertStatus(422) // Unprocessable Entity
                 ->assertJsonValidationErrors(['tail_number']);
    }
}
