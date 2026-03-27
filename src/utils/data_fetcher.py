import asyncio
import logging
from typing import Any

import duckdb
import pandas as pd

from src.config import settings

logger = logging.getLogger(__name__)


class DengueDataFetcher:
    """
    Fetches dengue surveillance data from SINAN via PySUS.
    """

    def __init__(self, cache_dir: str = "~/pysus"):
        self.cache_dir = cache_dir
        logger.info(f"DengueDataFetcher initialized with cache_dir={cache_dir}")

    async def fetch_dengue_data(
        self,
        year: int,
        state: str | None = None,
        municipality_code: str | None = None,
    ) -> pd.DataFrame:
        """
        Download and return dengue (DENG) data from SINAN.

        Args:
            year: Year to fetch data for
            state: State abbreviation (e.g., "SP", "RJ")
            municipality_code: IBGE municipality code

        Returns:
            DataFrame with dengue case data
        """
        logger.info(
            f"Starting fetch_dengue_data: year={year}, state={state}, municipality_code={municipality_code}"
        )

        try:
            # Run blocking PySUS operations in a thread pool
            df = await asyncio.to_thread(
                self._fetch_dengue_data_sync, year, state, municipality_code
            )
            logger.info(f"Successfully fetched {len(df)} dengue records")
            return df
        except Exception as e:
            logger.exception(f"Error fetching dengue data: {e}")
            raise

    def _fetch_dengue_data_sync(
        self,
        year: int,
        state: str | None = None,
        municipality_code: str | None = None,
    ) -> pd.DataFrame:
        """
        Synchronous implementation of data fetching.

        This runs in a thread pool to avoid blocking the event loop.
        Uses DuckDB for efficient filtering of large parquet files.
        """
        logger.info("Loading PySUS SINAN module")
        from pysus import SINAN

        logger.info("Initializing SINAN and loading files")
        sinan = SINAN().load()

        logger.info(f"Getting DENG files for year {year}")
        files = sinan.get_files(dis_code="DENG", year=year)

        if not files:
            error_msg = f"No dengue data available for year {year}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Found {len(files)} file(s): {[str(f) for f in files]}")

        # Warn about large downloads
        if not state and not municipality_code:
            logger.warning(
                f"Downloading full Brazil dengue data for {year}. "
                "This may take several minutes. Consider filtering by state or municipality."
            )

        logger.info(f"Downloading {files[0]}...")
        parquet_path = files[0].download()
        logger.info(f"Download complete, parquet saved to: {parquet_path}")

        # Use DuckDB for efficient filtering
        logger.info("Querying parquet file with DuckDB")

        # Build query with filters
        if municipality_code:
            logger.info(f"Filtering by municipality_code={municipality_code} using DuckDB")
            query = f"SELECT * FROM '{parquet_path}' WHERE ID_MUNICIP = '{municipality_code}'"
        elif state:
            logger.info(f"Filtering by state={state} using DuckDB")
            query = f"SELECT * FROM '{parquet_path}' WHERE SG_UF_NOT = '{state}'"
        else:
            logger.info("Loading all data (no filters)")
            query = f"SELECT * FROM '{parquet_path}'"

        logger.info(f"Executing query: {query}")
        df = duckdb.query(query).to_df()
        logger.info(f"Query complete, returned {len(df)} records")

        if len(df) > 0:
            logger.info(f"Dataframe columns: {list(df.columns)[:20]}")

        return df

    def summarize(self, df: pd.DataFrame) -> dict[str, Any]:
        """
        Generate summary statistics for the dengue data.

        Args:
            df: DataFrame with dengue case data

        Returns:
            Dictionary with summary statistics
        """
        try:
            logger.info(f"Summarizing dataframe with {len(df)} records")
            total_cases = len(df)

            if total_cases == 0:
                logger.warning("Empty dataframe, returning zero summary")
                return {
                    "total_cases": 0,
                    "by_week": {},
                    "by_age_group": {},
                    "hospitalizations": 0,
                    "deaths": 0,
                    "fatality_rate": 0.0,
                }

            by_week = {}
            if "SEM_NOT" in df.columns:
                logger.debug("Grouping by SEM_NOT (epidemiological week)")
                by_week = df.groupby("SEM_NOT").size().to_dict()
            else:
                logger.warning("SEM_NOT column not found in dataframe")

            by_age_group = {}
            if "NU_IDADE_N" in df.columns:
                logger.debug("Grouping by NU_IDADE_N (age)")
                by_age_group = df.groupby("NU_IDADE_N").size().to_dict()
            else:
                logger.warning("NU_IDADE_N column not found in dataframe")

            hospitalizations = 0
            if "HOSPITALIZ" in df.columns:
                hospitalizations = int((df["HOSPITALIZ"] == 1).sum())
                logger.debug(f"Hospitalizations: {hospitalizations}")
            else:
                logger.warning("HOSPITALIZ column not found in dataframe")

            deaths = 0
            if "EVOLUCAO" in df.columns:
                deaths = int((df["EVOLUCAO"] == 2).sum())
                logger.debug(f"Deaths: {deaths}")
            else:
                logger.warning("EVOLUCAO column not found in dataframe")

            fatality_rate = (deaths / total_cases * 100) if total_cases > 0 else 0.0

            summary = {
                "total_cases": total_cases,
                "by_week": by_week,
                "by_age_group": by_age_group,
                "hospitalizations": hospitalizations,
                "deaths": deaths,
                "fatality_rate": round(fatality_rate, 2),
            }

            logger.info(
                f"Summary completed: {total_cases} cases, {deaths} deaths, {fatality_rate:.2f}% fatality"
            )
            return summary

        except Exception as e:
            logger.exception(f"Error summarizing data: {e}")
            raise
