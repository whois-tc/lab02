# Mental Health Workforce Analysis

This program downloads WHO mental-health workforce records and summarizes psychiatrist access across WHO regions. It helps show broad regional differences in the number of psychiatrists per 100,000 people.

## Data source

The data comes from the WHO Global Health Observatory API:

https://ghoapi.azureedge.net/api/MH_6

Each record represents a country's reported psychiatrist rate for a particular year. The API returned approximately 146 records when this project was created.

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows using Git Bash:

```bash
source .venv/Scripts/activate
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Run

```bash
python mental_health_analysis.py
```

## Example output

A successful run creates `mental_health_summary.json`. A shortened excerpt looks like this:

```json
{
  "source_url": "https://ghoapi.azureedge.net/api/MH_6",
  "downloaded_record_count": 146,
  "valid_record_count": 146,
  "skipped_record_count": 0,
  "years": [
    2013,
    2014,
    2015,
    2016,
    2017
  ]
}
```

The complete JSON file also contains average psychiatrist rates for each WHO region and counts records in three access levels: under 1, 1 to 5, and over 5 psychiatrists per 100,000 people.

The access levels were created for this project and are not official WHO classifications.

## Data quirks

- The API places its records inside a field named `value`, rather than returning the records directly.
- Country names are not included in the records. Countries are identified by three-letter codes in `SpatialDim`.
- The records cover several years rather than one shared reporting year.
- Region or rate values may be missing. The program skips those records and reports how many were skipped.
- A rate could also be malformed rather than numeric. The program attempts to convert each rate to a number and skips values that cannot be converted.
- All 146 records were valid during the successful run used to create the committed summary, but a future API response may differ.

## Design choices

- A list stores the valid records because the program needs to process each record in order.
- A dictionary groups lists of psychiatrist rates by WHO region because each region name must connect to its own collection of rates.
- Another dictionary stores the access-level counts and the final JSON summary because each value needs a descriptive label.
- A set stores the years because a set automatically keeps each year only once.
- A set comprehension builds the collection of unique years from the valid records.

## Known limitations

- The available records are from 2013 to 2017, so the results do not describe current psychiatrist access.
- The regional averages are simple averages of the available country records. They are not weighted by population.
- Countries may report data in different years, so the regional averages do not represent one common year.
- The program depends on the WHO API being available and retaining the same response structure.