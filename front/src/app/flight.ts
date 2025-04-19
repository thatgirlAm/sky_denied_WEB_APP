export class Flight {
    depart!: string;
    arrival!: string;
    flightDate!: string;
    flightNumberIata!: string;
    tailNumber?: string;
    airline?: string;
    status?: string;
    scheduledDepartureLocal?: string;
    scheduledDepartureUtc?: string;
    actualDepartureLocal?: string | null;
    actualDepartureUtc?: string | null;
    scheduledArrivalLocal?: string;
    scheduledArrivalUtc?: string;
    actualArrivalLocal?: string | null;
    actualArrivalUtc?: string | null;
    scheduleDuration?: string;
    actualDuration?: string | null;

    constructor(apiResponse: any) {
        this.depart = apiResponse.depart_from;
        this.arrival = apiResponse.arrive_at;
        this.flightDate = apiResponse.flight_date;
        this.flightNumberIata = apiResponse.flight_number_iata;
        this.tailNumber = apiResponse.tail_number?.trim();
        this.airline = apiResponse.airline;
        this.status = apiResponse.status;
        this.scheduledDepartureLocal = apiResponse.scheduled_departure_local;
        this.scheduledDepartureUtc = apiResponse.scheduled_departure_utc;
        this.actualDepartureLocal = apiResponse.actual_departure_local;
        this.actualDepartureUtc = apiResponse.actual_departure_utc;
        this.scheduledArrivalLocal = apiResponse.scheduled_arrival_local;
        this.scheduledArrivalUtc = apiResponse.scheduled_arrival_utc;
        this.actualArrivalLocal = apiResponse.actual_arrival_local;
        this.actualArrivalUtc = apiResponse.actual_arrival_utc;
        this.scheduleDuration = apiResponse.schedule_duration;
        this.actualDuration = apiResponse.actual_duration;
    }
}