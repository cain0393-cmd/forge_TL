import argparse
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from .config import config
from .core import Portfolio

def main():
    parser = argparse.ArgumentParser(description="FORGE_TL CLI")
    subparsers = parser.add_subparsers(dest="command")

    # 'check' command
    check_parser = subparsers.add_parser("check", help="Check if the foundation is operational")

    # 'nse-day' command
    nse_day_parser = subparsers.add_parser("nse-day", help="Download and ingest NSE data for a specific date")
    nse_day_parser.add_argument("date", type=str, help="Date in YYYY-MM-DD format")

    # 'query' command
    query_parser = subparsers.add_parser("query", help="Query market data")
    query_parser.add_argument("--symbol", type=str, required=True, help="Symbol to query")

    # 'export' command
    export_parser = subparsers.add_parser("export", help="Export DuckDB to Parquet")

    args = parser.parse_args()

    if args.command == "check":
        portfolio = Portfolio()
        print("FORGE_TL operational.")
        print(f"Starting capital: \u20b9{portfolio.get_capital():,.2f}")
        sys.exit(0)
    elif args.command == "nse-day":
        from .data import NSEDownloader, NSEParser, MarketDataValidator, MarketDataDB
        
        date_str = args.date
        print(f"Downloading data for {date_str}...")
        try:
            zip_path = NSEDownloader.download(date_str)
            print(f"Parsing {zip_path}...")
            df = NSEParser.parse(zip_path)
            
            print("Validating and normalizing data...")
            df_canonical = MarketDataValidator.validate_and_normalize(df)
            
            print(f"Ingesting {len(df_canonical)} records into DuckDB...")
            db = MarketDataDB()
            db.ingest(df_canonical)
            
            print("Done.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.command == "query":
        from .data import MarketDataDB
        db = MarketDataDB()
        df = db.query(args.symbol)
        if df.empty:
            print(f"No data found for symbol {args.symbol}")
        else:
            print(df.to_string(index=False))
        sys.exit(0)
    elif args.command == "export":
        from .historical import ParquetExporter
        print("Exporting DuckDB to Parquet...")
        ParquetExporter.export()
        print("Done.")
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
