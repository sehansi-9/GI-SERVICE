from src.exception.exceptions import InternalServerError
import asyncio
from src.utils.util_functions import Util
from aiohttp import ClientSession
from src.utils import http_client
from src.models.organisation_schemas import Entity, Kind
from src.enums.kindEnum import KindMajorEnum, KindMinorEnum
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """
    This service is responsible for executing aggregate functions by calling the OpenGINService and processing the returned data.
    """

    def __init__(self, config: dict, opengin_service):
        self.config = config
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
                try:
                    if not gazette.created:
                        logger.warning(f"Gazette with id {gazette.id} is missing creation date.")
                        continue

                    dt_str = Util.normalize_timestamp(gazette.created)

                    if not dt_str or len(dt_str) < 7:
                        logger.error(f"Could not parse date for gazette with id {gazette.id}: {gazette.created}")
                        continue

                    # Extract year and month
                    year = dt_str[:4]
                    month = int(dt_str[5:7]) - 1  # 0-indexed for array

                    if year not in res_dict:
                        res_dict[year] = [0] * 12

                    res_dict[year][month] += 1
                except (ValueError, TypeError, IndexError) as e:
                    logger.error(f"Error processing date for gazette with id {gazette.id}: {e}")
                    continue

            # Sort by year keys and format
            sorted_years = sorted(res_dict.items())
            return {
                "years": [
                    {"year": int(year), "values": values}
                    for year, values in sorted_years
                ]
            }

        except Exception as e:
            logger.error(f"Error in fetching gazette data points: {str(e)}")
            raise InternalServerError(
                "An unexpected error occurred while fetching gazette data"
            )
