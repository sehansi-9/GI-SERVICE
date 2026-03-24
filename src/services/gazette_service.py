from src.enums.relationEnum import RelationNameEnum
from src.exception.exceptions import BadRequestError
from src.exception.exceptions import NotFoundError
from src.exception.exceptions import InternalServerError
import asyncio
from src.utils.util_functions import Util
from aiohttp import ClientSession
from src.utils import http_client
from src.models.organisation_schemas import Entity, Relation, Kind
from src.enums.kindEnum import KindMajorEnum, KindMinorEnum
from typing import Optional, Sequence, Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GazetteService:
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
                Entity(kind=Kind(
                    major=KindMajorEnum.DOCUMENT.value, 
                    minor=KindMinorEnum.EXTRA_ORDINARY_GAZETTE_ORGANISATION.value
                ))
            )
            person_gazettes_task = self.opengin_service.get_entities(
                Entity(kind=Kind(
                    major=KindMajorEnum.DOCUMENT.value, 
                    minor=KindMinorEnum.EXTRA_ORDINARY_GAZETTE_PERSON.value
                ))
            )

            organization_gazettes, person_gazettes = await asyncio.gather(
                 organization_gazettes_task, person_gazettes_task
            )

            all_gazettes = []
            if not isinstance(organization_gazettes, Exception) and organization_gazettes:
                all_gazettes.extend(organization_gazettes)
            if not isinstance(person_gazettes, Exception) and person_gazettes:
                all_gazettes.extend(person_gazettes)

            # aggregate by year and month
            res_dict: Dict[str, List[int]] = {}
            for gazette in all_gazettes:
                try:
                    dt_str = Util.normalize_timestamp(gazette.created)
                    
                    # Extract year and month
                    year = dt_str[:4]
                    month = int(dt_str[5:7]) - 1 # 0-indexed for array

                    if year not in res_dict:
                        res_dict[year] = [0] * 12
                    
                    res_dict[year][month] += 1
                except Exception as e:
                    logger.error(f"Error parsing date for gazette: {e}")
                    continue
            
            # Sort by year keys
            return dict(sorted(res_dict.items()))

        except Exception as e:
            logger.error(f"Error in fetching gazette data points: {str(e)}")
            raise InternalServerError("An unexpected error occurred while fetching gazette data")

