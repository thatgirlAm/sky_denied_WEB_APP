<?php
// source: personal project : https://github.com/thatgirlAm/daisy/blob/main/back/app/Http/Controllers/FormatTrait.php ; 
// author: Amaëlle DIOP - 461543 -- Sky Denied 

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

// The response to an API call should be in a particular format for every request; having a format controller helps setting the wanted format of a response 

Trait FormatTrait 
{
    public function format($data){
        return response()->json([
            "message"=>$data[0],
            "status"=>$data[1],
            "data"=>$data[2]
        ]);
    }

    public function format_delete($thing){
        return response()->json([
            "message"=> $thing. " deleted.",
            "status"=>Response::HTTP_OK,
            "data"=>null
        ])
        ;
    }
    public function format_error(string $message, string $status){
        return response()->json([
            "message"=> $message,
            "status"=>$status,
            "data"=>null
        ])
        ;

    }

    public function format_no_page(){
        return $this->formatError("This page does not exist", response::HTTP_NO_CONTENT);
    }
}