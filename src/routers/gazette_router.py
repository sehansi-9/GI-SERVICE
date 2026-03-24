from fastapi import APIRouter, Depends
from src.dependencies import get_config
from src.services import OpenGINService, GazetteService

router = APIRouter(prefix="/v1/gazette", tags=["Gazette"])

def get_gazette_service(config: dict = Depends(get_config)):
    opengin_service = OpenGINService(config=config)
    return GazetteService(config, opengin_service)

@router.get('/data-points', summary="Get gazette data points.", description="Returns number of gazettes created for each month for all years.")
async def gazette_data_points(
    service: GazetteService = Depends(get_gazette_service)
):
    service_response = await service.get_gazette_data_points()
    return service_response
