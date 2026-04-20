from src.exception.exceptions import InternalServerError
import asyncio
from src.utils.util_functions import Util
from aiohttp import ClientSession
from src.utils import http_client
from src.models.organisation_schemas import Entity, Kind
from src.enums.kindEnum import KindMajorEnum, KindMinorEnum
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """
    This service is responsible for executing aggregate functions by calling the OpenGINService and processing the returned data.
    """

    def __init__(self, opengin_service):
        self.opengin_service = opengin_service

    @property
    def session(self) -> ClientSession:
        """Access the global session"""
        return http_client.session

    # get gazette data points
    async def get_gazette_data_points(self):
        try:
            organization_gazettes_task = self.opengin_service.get_entities(
                Entity(
                    kind=Kind(
                        major=KindMajorEnum.DOCUMENT.value,
                        minor=KindMinorEnum.EXTGZT_ORGANISATION.value,
                    )
                )
            )
            person_gazettes_task = self.opengin_service.get_entities(
                Entity(
                    kind=Kind(
                        major=KindMajorEnum.DOCUMENT.value,
                        minor=KindMinorEnum.EXTGZT_PERSON.value,
                    )
                )
            )

            results_gazettes = await asyncio.gather(
                organization_gazettes_task, person_gazettes_task, return_exceptions=True
            )
            all_gazettes = []
            for result in results_gazettes:
                if not isinstance(result, Exception) and result:
                    all_gazettes.extend(result)

            # aggregate by year and month
            res_dict: Dict[str, List[int]] = {}
            for gazette in all_gazettes:
                gazette_id = getattr(gazette, "id", "unknown")
                try:
                    created_date = getattr(gazette, "created", None)

                    if not created_date:
                        logger.warning(
                            f"Gazette with id {gazette_id} is missing creation date."
                        )
                        continue

                    dt_str = Util.normalize_timestamp(created_date)
                    if not dt_str:
                        logger.error(
                            f"Could not parse date for gazette with id {gazette_id}: {created_date}"
                        )
                        continue

                    # parsing using datetime
                    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
                    year = str(dt.year)
                    month = dt.month - 1  # 0-indexed for array

                    if year not in res_dict:
                        res_dict[year] = [0] * 12

                    res_dict[year][month] += 1
                except (ValueError, TypeError, IndexError, AttributeError) as e:
                    logger.error(
                        f"Error processing date for gazette with id {gazette_id}: {e}"
                    )
                    continue

            # Sort by year keys and format
            sorted_years = sorted(res_dict.items())
            return {
                "data": [
                    {"year": int(year), "values": values}
                    for year, values in sorted_years
                ]
            }

        except Exception as e:
            logger.error(f"Error in fetching gazette data points: {str(e)}")
            raise InternalServerError(
                "An unexpected error occurred while fetching gazette data"
            )
