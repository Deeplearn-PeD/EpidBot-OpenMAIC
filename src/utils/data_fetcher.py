from typing import Any

import pandas as pd


class DengueDataFetcher:
    """
    Fetches dengue surveillance data from SINAN via PySUS.
    """

    def __init__(self, cache_dir: str = "~/pysus"):
        self.cache_dir = cache_dir

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
        from pysus.online_data.SINAN import download, parquets_to_dataframe

        files = download("DENG", year)
        if not files:
            raise ValueError(f"No dengue data available for year {year}")

        df = parquets_to_dataframe(files)

        if municipality_code:
            df = df[df.ID_MUNICIP == municipality_code]
        elif state:
            df = df[df.SG_UF_NOT == state]

        return df

    def summarize(self, df: pd.DataFrame) -> dict[str, Any]:
        """
        Generate summary statistics for the dengue data.

        Args:
            df: DataFrame with dengue case data

        Returns:
            Dictionary with summary statistics
        """
        total_cases = len(df)

        if total_cases == 0:
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
            by_week = df.groupby("SEM_NOT").size().to_dict()

        by_age_group = {}
        if "NU_IDADE_N" in df.columns:
            by_age_group = df.groupby("NU_IDADE_N").size().to_dict()

        hospitalizations = 0
        if "HOSPITALIZ" in df.columns:
            hospitalizations = int((df["HOSPITALIZ"] == 1).sum())

        deaths = 0
        if "EVOLUCAO" in df.columns:
            deaths = int((df["EVOLUCAO"] == 2).sum())

        fatality_rate = (deaths / total_cases * 100) if total_cases > 0 else 0.0

        return {
            "total_cases": total_cases,
            "by_week": by_week,
            "by_age_group": by_age_group,
            "hospitalizations": hospitalizations,
            "deaths": deaths,
            "fatality_rate": round(fatality_rate, 2),
        }
