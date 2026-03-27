#!/usr/bin/env python3
"""
Quick test of PySUS download with timeout and smaller dataset.

Usage:
    timeout 60 uv run python scripts/test_pysus_quick.py
"""

import sys


def main():
    print("Testing PySUS download with São Paulo municipality...")
    print("(This should be faster than full state download)")
    print()

    try:
        from pysus import SINAN

        print("✓ PySUS imported")

        sinan = SINAN().load()
        print("✓ SINAN loaded")

        files = sinan.get_files(dis_code="DENG", year=2024)
        print(f"✓ Found {len(files)} file(s): {files}")

        print("Downloading (this may take 10-30 seconds)...")
        parquet = files[0].download()
        print("✓ Download complete")

        print("Converting to dataframe...")
        df = parquet.to_dataframe()
        print(f"✓ Dataframe created: {len(df)} rows")

        print("Filtering by São Paulo municipality (355030)...")
        if "ID_MUNICIP" in df.columns:
            df_sp = df[df.ID_MUNICIP == "355030"]
            print(f"✓ Filtered to {len(df_sp)} rows for São Paulo city")
            print(f"  Columns: {list(df_sp.columns)[:10]}...")
            return 0
        else:
            print(f"✗ ID_MUNICIP column not found")
            print(f"  Available columns: {list(df.columns)}")
            return 1

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
