export interface Prediction {
    message : string;
    status : string ; 
    tail_number : string;
    delayed : boolean;
    previous_predicition : string ; 
    schedule_date_utc : string ; 
    value : string;
}