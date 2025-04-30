<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
   /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('predictions', function (Blueprint $table) {
            $table->id();
            $table->string('tail_number');
            $table->boolean('delayed')->nullable();
            $table->text('previous_prediction')->nullable();
            $table->float('accuracy')->nullable();
            $table->dateTime('schedule_date_utc');
            $table->timestamps();
            
            // Create a unique composite index
            $table->unique(['tail_number', 'schedule_date_utc']);
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('predictions');
    }
};
