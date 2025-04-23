<?php

namespace Tests\Unit\Controllers;

use App\Http\Controllers\UserController;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\Request;
use Tests\TestCase;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\ValidationException;

class UserTest extends TestCase
{
    use RefreshDatabase;

    protected UserController $controller;

    public function setUp(): void
    {
        parent::setUp();
        $this->controller = new UserController();
    }

    // TEST SUCCESSFUL USER CREATION
    public function test_add_user_with_valid_data()
    {
        $request = new Request([
            'name' => 'John Doe',
            'tail_number' => 'N12345',
            'email' => 'john.doe@example.com',
            'schedule_date_utc' => '2025-04-22T15:00:00Z'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(201, $response->getStatusCode());
        $this->assertEquals('User added successfully', $responseData['message']);
        $this->assertEquals('John Doe', $responseData['user']['name']);
        $this->assertEquals('N12345', $responseData['user']['tail_number']);
        $this->assertEquals('john.doe@example.com', $responseData['user']['email']);
        $this->assertEquals('2025-04-22T15:00:00Z', $responseData['user']['schedule_date_utc']);
        
        $this->assertDatabaseHas('users', [
            'name' => 'John Doe',
            'tail_number' => 'N12345',
            'email' => 'john.doe@example.com'
        ]);
    }

    public function test_add_user_with_minimum_valid_data()
    {
        $request = new Request([
            'name' => 'Jane Smith',
            'tail_number' => 'N54321',
            'email' => 'jane.smith@example.com',
            'schedule_date_utc' => '2025-05-15T10:30:00Z'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(201, $response->getStatusCode());
        $this->assertEquals('User added successfully', $responseData['message']);
        $this->assertArrayHasKey('user', $responseData);
    }

    public function test_add_user_with_additional_fields()
    {
        $request = new Request([
            'name' => 'Bob Johnson',
            'tail_number' => 'N98765',
            'email' => 'bob.johnson@example.com',
            'schedule_date_utc' => '2025-06-10T08:15:00Z',
            'extra_field' => 'This should be ignored',
            'another_extra' => 123
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(201, $response->getStatusCode());
        
        // Check that our user was created with correct data
        $this->assertDatabaseHas('users', [
            'name' => 'Bob Johnson',
            'tail_number' => 'N98765',
            'email' => 'bob.johnson@example.com'
        ]);
        
        // The extra fields should not be in the user model
        $user = User::where('email', 'bob.johnson@example.com')->first();
        $this->assertObjectNotHasAttribute('extra_field', $user);
        $this->assertObjectNotHasAttribute('another_extra', $user);
    }

    // TEST VALIDATION FAILURES
    public function test_add_user_missing_required_name()
    {
        $request = new Request([
            'tail_number' => 'N12345',
            'email' => 'missing.name@example.com',
            'schedule_date_utc' => '2025-04-22T15:00:00Z'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(422, $response->getStatusCode());
        $this->assertEquals('Validation failed', $responseData['message']);
        $this->assertArrayHasKey('errors', $responseData);
        $this->assertArrayHasKey('name', $responseData['errors']);
        
        $this->assertDatabaseMissing('users', [
            'email' => 'missing.name@example.com'
        ]);
    }

    public function test_add_user_missing_required_tail_number()
    {
        $request = new Request([
            'name' => 'Missing Tail',
            'email' => 'missing.tail@example.com',
            'schedule_date_utc' => '2025-04-22T15:00:00Z'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(422, $response->getStatusCode());
        $this->assertEquals('Validation failed', $responseData['message']);
        $this->assertArrayHasKey('errors', $responseData);
        $this->assertArrayHasKey('tail_number', $responseData['errors']);
    }

    public function test_add_user_missing_required_email()
    {
        $request = new Request([
            'name' => 'Missing Email',
            'tail_number' => 'N12345',
            'schedule_date_utc' => '2025-04-22T15:00:00Z'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(422, $response->getStatusCode());
        $this->assertEquals('Validation failed', $responseData['message']);
        $this->assertArrayHasKey('errors', $responseData);
        $this->assertArrayHasKey('email', $responseData['errors']);
    }

    public function test_add_user_missing_required_schedule_date()
    {
        $request = new Request([
            'name' => 'Missing Date',
            'tail_number' => 'N12345',
            'email' => 'missing.date@example.com'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(422, $response->getStatusCode());
        $this->assertEquals('Validation failed', $responseData['message']);
        $this->assertArrayHasKey('errors', $responseData);
        $this->assertArrayHasKey('schedule_date_utc', $responseData['errors']);
    }

    public function test_add_user_with_empty_data()
    {
        $request = new Request([]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(422, $response->getStatusCode());
        $this->assertEquals('Validation failed', $responseData['message']);
        $this->assertArrayHasKey('errors', $responseData);
        $this->assertCount(4, $responseData['errors']); // All 4 fields should fail validation
    }

    // TEST DATA FORMAT VALIDATION
    public function test_add_user_with_invalid_email_format()
    {
        $request = new Request([
            'name' => 'Invalid Email',
            'tail_number' => 'N12345',
            'email' => 'not-an-email',
            'schedule_date_utc' => '2025-04-22T15:00:00Z'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(422, $response->getStatusCode());
        $this->assertEquals('Validation failed', $responseData['message']);
        $this->assertArrayHasKey('errors', $responseData);
        $this->assertArrayHasKey('email', $responseData['errors']);
        
        $this->assertDatabaseMissing('users', [
            'name' => 'Invalid Email'
        ]);
    }

    public function test_add_user_with_invalid_date_format()
    {
        $request = new Request([
            'name' => 'Invalid Date',
            'tail_number' => 'N12345',
            'email' => 'invalid.date@example.com',
            'schedule_date_utc' => 'not-a-date'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(422, $response->getStatusCode());
        $this->assertEquals('Validation failed', $responseData['message']);
        $this->assertArrayHasKey('errors', $responseData);
        $this->assertArrayHasKey('schedule_date_utc', $responseData['errors']);
    }

    public function test_add_user_with_name_too_long()
    {
        // Generate a string longer than 255 characters
        $longName = str_repeat('A', 256);
        
        $request = new Request([
            'name' => $longName,
            'tail_number' => 'N12345',
            'email' => 'long.name@example.com',
            'schedule_date_utc' => '2025-04-22T15:00:00Z'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(422, $response->getStatusCode());
        $this->assertEquals('Validation failed', $responseData['message']);
        $this->assertArrayHasKey('errors', $responseData);
        $this->assertArrayHasKey('name', $responseData['errors']);
    }

    public function test_add_user_with_tail_number_too_long()
    {
        // Generate a string longer than 50 characters
        $longTailNumber = str_repeat('N', 51);
        
        $request = new Request([
            'name' => 'Long Tail',
            'tail_number' => $longTailNumber,
            'email' => 'long.tail@example.com',
            'schedule_date_utc' => '2025-04-22T15:00:00Z'
        ]);

        $response = $this->controller->addUser($request);
        $responseData = json_decode($response->getContent(), true);

        $this->assertEquals(422, $response->getStatusCode());
        $this->assertEquals('Validation failed', $responseData['message']);
        $this->assertArrayHasKey('errors', $responseData);
        $this->assertArrayHasKey('tail_number', $responseData['errors']);
    }

    // TEST EXCEPTION HANDLING
    public function test_add_user_with_database_exception()
    {
        // Create a mock of the Request class
        $request = $this->createMock(Request::class);
        
        // Set up the validate method to return validated data
        $request->method('validate')
            ->willReturn([
                'name' => 'Exception Test',
                'tail_number' => 'N12345',
                'email' => 'exception@example.com',
                'schedule_date_utc' => '2025-04-22T15:00:00Z'
            ]);
        
        // Create a partial mock of the User model that throws an exception on save
        $mockUser = $this->createPartialMock(User::class, ['save']);
        
        // Set up the save method to throw an exception
        $mockUser->method('save')
            ->will($this->throwException(new \Exception('Database connection error')));
        
        // Create a mock of the controller with a method to return our mock User
        $mockController = $this->getMockBuilder(UserController::class)
            ->onlyMethods(['createUserModel'])
            ->getMock();
        
        // Set up the createUserModel method to return our mock User
        $mockController->method('createUserModel')
            ->willReturn($mockUser);
        
        // In reality, we'd need to modify the controller to use this method, 
        // but for test purposes we're demonstrating the concept
        
        // Execute the test using our real controller instead (since we can't modify it)
        // This test would be better if the UserController had a way to inject a User model
        $actualController = new UserController();
        
        // Mark this test as incomplete
        $this->markTestIncomplete(
            'This test requires modifying the UserController to allow for mocking the User model creation'
        );
        
        // The following is how the test would ideally continue:
        // $response = $mockController->addUser($request);
        // $responseData = json_decode($response->getContent(), true);
        // 
        // $this->assertEquals(500, $response->getStatusCode());
        // $this->assertEquals('Failed to add user', $responseData['message']);
        // $this->assertArrayHasKey('error', $responseData);
    }

    public function test_add_user_with_validation_exception_manually_thrown()
    {
        // This test demonstrates handling of ValidationException when manually thrown
        
        // Create a mock validator that will fail
        $validator = Validator::make(
            ['name' => ''], // Empty name to fail validation
            ['name' => 'required']
        );
        
        // If validation fails (which it will), throw ValidationException
        if ($validator->fails()) {
            try {
                $validator->validate();
            } catch (ValidationException $e) {
                // Create a request object
                $request = new Request(['name' => '']);
                
                // On a real controller, we might inject the validator or use a custom validation method
                // But since we can't modify the controller, we'll use the real one and expect it to fail
                // with similar validation errors
                $response = $this->controller->addUser($request);
                $responseData = json_decode($response->getContent(), true);
                
                $this->assertEquals(422, $response->getStatusCode());
                $this->assertEquals('Validation failed', $responseData['message']);
                $this->assertArrayHasKey('errors', $responseData);
                $this->assertArrayHasKey('name', $responseData['errors']);
            }
        }
    }
}