#!/usr/bin/env python3
"""
Test script to verify PySUS data fetching works in isolation.

Usage:
    uv run python scripts/test_pysus.py
"""

import sys
import traceback


def test_pysus_import():
    """Test if PySUS can be imported."""
    print("[1/4] Testing PySUS import...")
    try:
        from pysus import SINAN

        print("      ✓ PySUS imported successfully")
        return True
    except Exception as e:
        print(f"      ✗ Failed to import PySUS: {e}")
        traceback.print_exc()
        return False


def test_sinan_load():
    """Test if SINAN can be loaded."""
    print("[2/4] Testing SINAN load...")
    try:
        from pysus import SINAN

        sinan = SINAN().load()
        print("      ✓ SINAN loaded successfully")
        return True
    except Exception as e:
        print(f"      ✗ Failed to load SINAN: {e}")
        traceback.print_exc()
        return False


def test_get_files():
    """Test if we can get dengue files."""
    print("[3/4] Testing get_files for DENG 2024...")
    try:
        from pysus import SINAN

        sinan = SINAN().load()
        files = sinan.get_files(dis_code="DENG", year=2024)
        print(f"      ✓ Found {len(files)} file(s)")
        if files:
            print(f"      First file: {files[0]}")
        return True
    except Exception as e:
        print(f"      ✗ Failed to get files: {e}")
        traceback.print_exc()
        return False


def test_download():
    """Test if we can download and read a file."""
    print("[4/4] Testing download and read...")
    try:
        from pysus import SINAN

        sinan = SINAN().load()
        files = sinan.get_files(dis_code="DENG", year=2024)

        if not files:
            print("      ✗ No files to download")
            return False

        print(f"      Downloading {files[0]}...")
        parquet = files[0].download()
        print(f"      ✓ Downloaded successfully")

        print("      Converting to dataframe...")
        df = parquet.to_dataframe()
        print(f"      ✓ Dataframe created with {len(df)} rows")

        print(f"      Columns: {list(df.columns)[:10]}...")

        # Try filtering by state
        if "SG_UF_NOT" in df.columns:
            print("      Filtering by state SP...")
            df_sp = df[df.SG_UF_NOT == "SP"]
            print(f"      ✓ Filtered to {len(df_sp)} rows for SP")

        return True
    except Exception as e:
        print(f"      ✗ Failed to download/read: {e}")
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("PySUS Data Fetcher Test")
    print("=" * 60)

    tests = [
        test_pysus_import,
        test_sinan_load,
        test_get_files,
        test_download,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"      ✗ Test crashed: {e}")
            traceback.print_exc()
            results.append(False)
        print()

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
