import pandas as pd
import argparse
import os

def download_ookla_data(year, quarter, service="fixed"):
    """
    Downloads Ookla open data for a specific year and quarter,
    filters it to the Albay bounding box, and saves it locally.
    """

    minx, miny, maxx, maxy = 123.28054818, 12.98618489, 124.22011114, 13.52325523
    albay_bounds = [minx, miny, maxx, maxy]
    
    quarter_start = f"{year}-{(((quarter - 1) * 3) + 1):02}-01"
    url = f"s3://ookla-open-data/parquet/performance/type={service}/year={year}/quarter={quarter}/{quarter_start}_performance_{service}_tiles.parquet"
    
    bbox_filters = [
        ('tile_y', '<=', albay_bounds[3]), 
        ('tile_y', '>=', albay_bounds[1]),
        ('tile_x', '<=', albay_bounds[2]), 
        ('tile_x', '>=', albay_bounds[0])
    ]
    
    print(f"Connecting to S3 to fetch {service} network data for Q{quarter} {year}...")
    try:
        tiles_df = pd.read_parquet(
            url,
            columns=['quadkey', 'tile_x', 'tile_y', 'tests', 'devices', 'avg_lat_ms', 'avg_d_kbps', 'avg_u_kbps'],
            filters=bbox_filters,
            storage_options={"s3": {"anon": True}} 
        )
    except Exception as e:
        print(f"Failed to download data. Ensure the year and quarter are available in the Ookla dataset. Error: {e}")
        return
        
    output_file = f"albay_ookla_{service}_{year}_q{quarter}.parquet"
    
    print("Saving to local parquet file...")
    tiles_df.to_parquet(output_file)
    print(f"Success! {len(tiles_df)} tiles saved to '{output_file}'")
    print(f"File size: {os.path.getsize(output_file) / 1024:.2f} KB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and filter Ookla Open Data for Albay.")
    parser.add_argument("--year", type=int, default=2024, help="Year of the dataset (e.g. 2024)")
    parser.add_argument("--quarter", type=int, default=4, help="Quarter of the dataset (1-4)")
    parser.add_argument("--service", type=str, default="fixed", choices=["fixed", "mobile"], help="Service type (fixed or mobile)")
    
    args = parser.parse_args()
    
    download_ookla_data(args.year, args.quarter, args.service)
