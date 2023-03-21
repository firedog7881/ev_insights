import json
from typing import List
import requests
from pydantic import BaseModel, validator
import typer
import pandas as pd

app = typer.Typer()

DATA_URL = "https://data.wa.gov/api/views/f6w7-q2d2/rows.json?accessType=DOWNLOAD"


class VehicleData(BaseModel):
    VIN: str
    County: str
    City: str
    State: str
    Postal_Code: int
    Model_Year: int
    Make: str
    Model: str
    Electric_Vehicle_Type: str
    Clean_Alternative_Fuel_Vehicle_Eligibility: bool # Using validator to change the data's text to a bool for easier usage
    Electric_Range: int

    @validator("Clean_Alternative_Fuel_Vehicle_Eligibility", pre=True)
    def eligibility_text_to_bool(cls, value):
        return value == "Clean Alternative Fuel Vehicle Eligible"


def fetch_data() -> List[VehicleData]:
    response = requests.get(DATA_URL)
    data = json.loads(response.text)
    vehicles = []

    for item in data["data"]:
        vehicle = VehicleData(
            VIN=item[8],
            County=item[9],
            City=item[10],
            State=item[11],
            Postal_Code=int(item[12]),
            Model_Year=int(item[13]),
            Make=item[14],
            Model=item[15],
            Electric_Vehicle_Type=item[16],
            Clean_Alternative_Fuel_Vehicle_Eligibility=item[17],  # Using "Clean Alternative Fuel Vehicle (CAFV) Eligibility" field as input
            Electric_Range=int(item[18]),
        )
        vehicles.append(vehicle)

    return vehicles



def create_dataframe(vehicles: List[VehicleData]) -> pd.DataFrame:
    data = [vehicle.dict() for vehicle in vehicles]
    return pd.DataFrame(data)


@app.command()
def popular_makes():
    vehicles = fetch_data()
    df = create_dataframe(vehicles)
    popular_makes = df["Make"].value_counts()
    typer.echo(f"Popular makes:\n{popular_makes}")


@app.command()
def electric_range_by_make():
    vehicles = fetch_data()
    df = create_dataframe(vehicles)
    range_by_make = df.groupby("Make")["Electric_Range"].mean()
    typer.echo(f"Average electric range by make:\n{range_by_make}")


@app.command()
def vehicle_counts_by_model_year():
    vehicles = fetch_data()
    df = create_dataframe(vehicles)
    counts_by_year = df["Model_Year"].value_counts()
    typer.echo(f"Vehicle counts by model year:\n{counts_by_year}")


def main():
    app()


if __name__ == "__main__":
    main()

