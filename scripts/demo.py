#!/usr/bin/env python3
"""
Demo script for EpidBot-OpenMAIC Bridge.

This script demonstrates the end-to-end flow:
1. Submit a training generation request
2. Poll for job completion
3. Display the classroom URL

Usage:
    uv run python scripts/demo.py
"""

import asyncio
import sys

import httpx

BASE_URL = "http://localhost:8765"


async def demo():
    print("=" * 60)
    print("EpidBot-OpenMAIC Bridge Demo")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Health check
        print("\n[1] Checking service health...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            health = response.json()
            print(f"    Status: {health['status']}")
            print(f"    OpenMAIC connected: {health.get('openmaic_connected')}")
        except Exception as e:
            print(f"    Error: {e}")
            print("    Make sure the bridge service is running: uv run serve")
            return

        # 2. Submit training generation
        print("\n[2] Submitting dengue training generation request...")
        print("    Region: São Paulo (municipality)")
        print("    Year: 2024")
        print("    Note: Using municipality code for faster download")

        try:
            response = await client.post(
                f"{BASE_URL}/api/generate-dengue-training",
                json={
                    "region": "São Paulo",
                    "year": 2024,
                    "state": "SP",
                    "municipality_code": "355030",  # São Paulo city - much faster than entire state
                    "language": "pt-BR",
                    "target_audience": "agentes de saúde",
                },
            )
            response.raise_for_status()
            result = response.json()
            job_id = result["job_id"]
            print(f"    Job ID: {job_id}")
            print(f"    Data summary:")
            print(f"      - Total cases: {result['data_summary']['total_cases']:,}")
            print(f"      - Deaths: {result['data_summary']['deaths']:,}")
            print(f"      - Hospitalizations: {result['data_summary']['hospitalizations']:,}")
            print(f"      - Fatality rate: {result['data_summary']['fatality_rate']}%")
        except httpx.HTTPStatusError as e:
            print(f"    HTTP Error: {e.response.status_code}")
            print(f"    Detail: {e.response.json().get('detail', 'Unknown error')}")
            return
        except Exception as e:
            print(f"    Error: {e}")
            return

        # 3. Poll for completion
        print("\n[3] Polling job status...")
        poll_count = 0
        max_polls = 120  # 10 minutes max

        while poll_count < max_polls:
            try:
                response = await client.get(f"{BASE_URL}/api/job/{job_id}")
                status_data = response.json()
                status = status_data["status"]
                progress = status_data.get("progress", 0)

                print(f"    [{poll_count + 1}] Status: {status}, Progress: {progress}%")

                if status == "completed":
                    print("\n" + "=" * 60)
                    print("SUCCESS! Classroom generated.")
                    print("=" * 60)
                    print(f"\nClassroom URL: {status_data.get('classroom_url')}")
                    print(f"Classroom ID: {status_data.get('classroom_id')}")
                    break
                elif status == "failed":
                    print(f"\nFAILED: {status_data.get('error')}")
                    break

                await asyncio.sleep(5)
                poll_count += 1

            except Exception as e:
                print(f"    Polling error: {e}")
                await asyncio.sleep(5)
                poll_count += 1

        if poll_count >= max_polls:
            print("\nTimeout: Job did not complete in time")


if __name__ == "__main__":
    asyncio.run(demo())
