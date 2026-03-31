import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class EpidBotResponseParser:
    """
    Parser for EpidBot markdown responses containing epidemiological data.
    """

    REQUIRED_FIELDS = {"total_cases", "deaths", "hospitalizations", "fatality_rate"}

    @staticmethod
    def parse_dengue_summary(markdown: str) -> dict[str, Any] | None:
        """
        Parse dengue surveillance data from markdown response.

        Args:
            markdown: Markdown text from EpidBot

        Returns:
            Dictionary with parsed data or None if incomplete.
            Format:
            {
                "total_cases": int,
                "deaths": int,
                "hospitalizations": int,
                "fatality_rate": float,
                "by_week": dict,
                "by_age_group": dict
            }
        """
        if not markdown:
            logger.warning("Empty markdown response")
            return None

        logger.info(f"Parsing dengue summary from markdown, length={len(markdown)}")

        data: dict[str, Any] = {
            "total_cases": 0,
            "deaths": 0,
            "hospitalizations": 0,
            "fatality_rate": 0.0,
            "by_week": {},
            "by_age_group": {},
        }

        found_fields: set[str] = set()

        data.update(EpidBotResponseParser._parse_table(markdown))
        found_fields.update(
            k for k in data.keys() if data[k] != 0 and data[k] != 0.0 and data[k] != {}
        )

        if found_fields >= EpidBotResponseParser.REQUIRED_FIELDS:
            logger.info(f"Successfully parsed complete dengue summary: {found_fields}")
            return data

        data.update(EpidBotResponseParser._parse_bold_patterns(markdown))
        found_fields.update(
            k for k in data.keys() if data[k] != 0 and data[k] != 0.0 and data[k] != {}
        )

        if found_fields >= EpidBotResponseParser.REQUIRED_FIELDS:
            logger.info(f"Successfully parsed complete dengue summary: {found_fields}")
            return data

        data.update(EpidBotResponseParser._parse_list_patterns(markdown))
        found_fields.update(
            k for k in data.keys() if data[k] != 0 and data[k] != 0.0 and data[k] != {}
        )

        if found_fields >= EpidBotResponseParser.REQUIRED_FIELDS:
            logger.info(f"Successfully parsed complete dengue summary: {found_fields}")
            return data

        logger.warning(
            f"Incomplete dengue summary. Found fields: {found_fields}, required: {EpidBotResponseParser.REQUIRED_FIELDS}"
        )
        return None

    @staticmethod
    def _parse_table(markdown: str) -> dict[str, Any]:
        """Parse pipe-separated markdown tables."""
        data: dict[str, Any] = {}
        lines = markdown.split("\n")

        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 3:
                continue
            key = parts[1].lower().strip()
            value_str = parts[2].strip().replace(",", "").replace("%", "")

            if key in ("metric", "key", "indicator", "variable"):
                continue

            try:
                if key in ("total_cases", "total cases", "cases", "casos"):
                    data["total_cases"] = int(float(value_str))
                elif key in ("deaths", "mortes"):
                    data["deaths"] = int(float(value_str))
                elif key in ("hospitalizations", "hospitalized", "internacoes"):
                    data["hospitalizations"] = int(float(value_str))
                elif key in ("fatality_rate", "fatality", "letalidade"):
                    data["fatality_rate"] = float(value_str)
            except ValueError:
                pass

        return data

    @staticmethod
    def _parse_bold_patterns(markdown: str) -> dict[str, Any]:
        """Parse bold markdown patterns like **Total Cases:** 1234."""
        data: dict[str, Any] = {}

        bold_pattern = r"\*{2}([^*]+)\*{2}\s*[:\-]?\s*([\d,\.]+)"
        matches = re.findall(bold_pattern, markdown)

        for label, value_str in matches:
            label_lower = label.lower().strip()
            value_str = value_str.replace(",", "")
            try:
                value = float(value_str)
                if (
                    "case" in label_lower
                    and "total" in label_lower
                    or label_lower.strip() == "cases"
                ):
                    data["total_cases"] = int(value)
                elif "death" in label_lower:
                    data["deaths"] = int(value)
                elif "hospitaliz" in label_lower:
                    data["hospitalizations"] = int(value)
                elif "fatality" in label_lower or "letalidade" in label_lower:
                    data["fatality_rate"] = value
            except ValueError:
                pass

        return data

    @staticmethod
    def _parse_list_patterns(markdown: str) -> dict[str, Any]:
        """Parse list patterns like - Total Cases: 1234."""
        data: dict[str, Any] = {}

        list_patterns = [
            r"-\s*(?:Total\s+)?[Cc]ases[:\s]+([\d,\.]+)",
            r"-\s*(?:Total\s+)?[Dd]eaths[:\s]+([\d,\.]+)",
            r"-\s*[Hh]ospitalizations[:\s]+([\d,\.]+)",
            r"-\s*[Ff]atality\s*[Rr]ate[:\s]+([\d,\.]+)",
        ]

        try:
            matches = re.findall(list_patterns[0], markdown, re.IGNORECASE)
            if matches:
                data["total_cases"] = int(float(matches[0].replace(",", "")))
        except (ValueError, IndexError):
            pass

        try:
            matches = re.findall(list_patterns[1], markdown, re.IGNORECASE)
            if matches:
                data["deaths"] = int(float(matches[0].replace(",", "")))
        except (ValueError, IndexError):
            pass

        try:
            matches = re.findall(list_patterns[2], markdown, re.IGNORECASE)
            if matches:
                data["hospitalizations"] = int(float(matches[0].replace(",", "")))
        except (ValueError, IndexError):
            pass

        try:
            matches = re.findall(list_patterns[3], markdown, re.IGNORECASE)
            if matches:
                data["fatality_rate"] = float(matches[0].replace(",", ""))
        except (ValueError, IndexError):
            pass

        return data
