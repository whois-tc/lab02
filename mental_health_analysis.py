import json
from pathlib import Path

import requests


API_URL = "https://ghoapi.azureedge.net/api/MH_6"
OUTPUT = Path("mental_health_summary.json")

def download_data():
    """Download mental-health workforce records from the WHO API."""
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["value"]

def clean_data(records):
    """Keep records that have a valid region and psychiatrist rate."""
    valid_records = []

    for record in records:
        region = record.get("ParentLocation")
        rate = record.get("NumericValue")

        if region != None and region != "" and rate != None:
            try:
                rate = float(rate)
            except (TypeError, ValueError):
                rate = None

        if region != None and region != "" and rate != None:
            record["NumericValue"] = rate
            valid_records.append(record)

    return valid_records

def group_by_region(records):
    """Group psychiatrist rates by WHO region."""
    region_rates = {}

    for record in records:
        region = record["ParentLocation"]
        rate = record["NumericValue"]
        current_rates = region_rates.get(region)

        if current_rates == None:
            region_rates[region] = [rate]
        else:
            current_rates.append(rate)

    return region_rates

def calculate_region_averages(region_rates):
    """Calculate the average psychiatrist rate for each region."""
    region_averages = {}

    for region in region_rates:
        rates = region_rates[region]
        average = sum(rates) / len(rates)
        region_averages[region] = round(average, 2)

    return region_averages

def count_access_levels(records):
    """Count records by psychiatrist access level."""
    access_counts = {
        "Under 1": 0,
        "1 to 5": 0,
        "Over 5": 0
    }

    for record in records:
        rate = record["NumericValue"]

        if rate < 1:
            access_counts["Under 1"] += 1
        elif rate <= 5:
            access_counts["1 to 5"] += 1
        else:
            access_counts["Over 5"] += 1

    return access_counts

def build_summary(records, valid_records, years, region_averages, access_counts):
    """Combine the analysis results into one summary dictionary."""
    summary = {
        "source_url": API_URL,
        "downloaded_record_count": len(records),
        "valid_record_count": len(valid_records),
        "skipped_record_count": len(records) - len(valid_records),
        "years": sorted(years),
        "region_averages": region_averages,
        "access_counts": access_counts
    }

    return summary

def write_summary(summary, path):
    """Write the summary dictionary to a JSON file."""
    path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8"
    )

def main():
    try:
        records = download_data()
    except requests.RequestException:
        print("Error: Could not download data from the WHO API.")
        return
    valid_records = clean_data(records)
    region_rates = group_by_region(valid_records)
    region_averages = calculate_region_averages(region_rates)
    access_counts = count_access_levels(valid_records)
    years = {record["TimeDim"] for record in valid_records}
    output_path = save_results(records,valid_records,years,region_averages,access_counts)

def main():
    """Download, analyze, display, and save the mental-health data."""
    try:
        records = download_data()
    except requests.RequestException:
        print("Error: Could not download data from the WHO API.")
        return

    valid_records = clean_data(records)
    region_rates = group_by_region(valid_records)
    region_averages = calculate_region_averages(region_rates)
    access_counts = count_access_levels(valid_records)
    years = {record["TimeDim"] for record in valid_records}

    summary = build_summary(
        records,
        valid_records,
        years,
        region_averages,
        access_counts
    )
    write_summary(summary, OUTPUT)

    print(f"Downloaded records: {len(records)}")
    print(f"Valid records: {len(valid_records)}")
    print(f"Skipped records: {len(records) - len(valid_records)}")
    print("Average psychiatrists per 100,000 by region:")
    print(region_averages)
    print("Records by psychiatrist access level:")
    print(access_counts)
    print("Years included in the data:")
    print(years)
    print(f"Results saved to: {OUTPUT}")


if __name__ == "__main__":
    main()