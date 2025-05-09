from FlightRadar24 import FlightRadar24API
import pandas as pd
def get_airlines():
    fr_api = FlightRadar24API()
    airlines = fr_api.get_airlines()
    df = pd.DataFrame(airlines)
    df['refund_policy'] = None
    df.to_csv('data/airlines.csv',index=False)

if __name__ == "__main__":
    get_airlines()