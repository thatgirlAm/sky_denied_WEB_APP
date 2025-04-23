<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;

class UserController extends Controller
{
    public function addUser(Request $request)
    {
        try {
            // Validate the input data
            $validatedData = $request->validate([
                'name' => 'required|string|max:255',
                'tail_number' => 'required|string|max:50',
                'email' => 'required|email|max:255',
                'schedule_date_utc' => 'required|date'
            ]);
            
            // Create a new user record
            $user = new User();
            $user->name = $validatedData['name'];
            $user->tail_number = $validatedData['tail_number'];
            $user->email = $validatedData['email'];
            $user->schedule_date_utc = $validatedData['schedule_date_utc'];
            $user->save();
            
            // Return success response
            return response()->json([
                'message' => 'User added successfully',
                'user' => $user
            ], 201);
            
        } catch (\Illuminate\Validation\ValidationException $e) {
            // Return validation error response
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $e->errors()
            ], 422);
        } catch (\Exception $e) {
            // Return general error response
            return response()->json([
                'message' => 'Failed to add user',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
