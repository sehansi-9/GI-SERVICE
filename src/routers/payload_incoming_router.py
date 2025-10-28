from fastapi import APIRouter, Depends
from src.models import ENTITY_PAYLOAD, ATTRIBUTE_PAYLOAD, WRITE_PAYLOAD
from src.services import IncomingServiceAttributes, IncomingServiceOrgchart, WriteAttributes
from src.dependencies import get_config
from chartFactory.utils import transform_data_for_chart

router = APIRouter()
writer = WriteAttributes() 

def get_orgchart_service(config: dict = Depends(get_config)):
    return IncomingServiceOrgchart(config)

def get_stat_service(config: dict = Depends(get_config)):
    return IncomingServiceAttributes(config)

@router.get("/categories")
async def get_all_categories(id: str | None = None, statService: IncomingServiceAttributes = Depends(get_stat_service)):
    return await statService.expose_category_by_id(id)

# Get the relevant attributes for the entity
@router.post("/data/entity/{entityId}")
async def get_relevant_attributes_for_entity(ENTITY_PAYLOAD: ENTITY_PAYLOAD , entityId : str, statService: IncomingServiceAttributes = Depends(get_stat_service)):
    attributes_of_the_entity = await statService.expose_relevant_attributes(ENTITY_PAYLOAD , entityId)
    return attributes_of_the_entity

# Get attributes for the selected attribute
@router.post("/data/attribute/{entityId}")
async def get_relevant_attributes_for_datasets(ATTRIBUTE_PAYLOAD: ATTRIBUTE_PAYLOAD, entityId : str, statService: IncomingServiceAttributes = Depends(get_stat_service)):
    attribute_data_out = await statService.expose_data_for_the_attribute(ATTRIBUTE_PAYLOAD, entityId)   
    return transform_data_for_chart(attribute_data_out)

# Write attributes to the entities
@router.post("/data/writeAttributes")
async def write_attributes(WRITE_PAYLOAD: WRITE_PAYLOAD):
    # Example : base_url = /Users/yasandu/Desktop/datasets/data/2022
    base_url = WRITE_PAYLOAD.base_url
    result = writer.traverse_folder(base_url)
    result = writer.pre_process_traverse_result(result)
    result = writer.entity_validator(result)
    # return result
    return writer.create_parent_categories_and_children_categories_v2(result)

@router.get("/data/yearswithdata")
async def yearswithdata(name: str, parentId: str, statService: IncomingServiceAttributes = Depends(get_stat_service)):
    years = await statService.datacategoriesbyyear(name, parentId)
    return years

# Get the timeline for the orgchart
# @router.get("/data/orgchart/timeline")
# async def get_timeline_for_orgchart(orgchartService: IncomingServiceOrgchart = Depends(get_orgchart_service)):
#     documentData = await orgchartService.get_documents()
#     presidentData = await orgchartService.get_presidents()
#     timeLine = orgchartService.get_timeline(documentData, presidentData)
#     return timeLine

# # Get ministries for the selected date
# @router.post("/data/orgchart/ministries")
# async def get__for_orgchart(orgchartService: IncomingServiceOrgchart = Depends(get_orgchart_service)):
#     return

# # Get departments for the selected ministry at the selected date
# @router.post("/data/orgchart/departments")
# async def get__for_orgchart(orgchartService: IncomingServiceOrgchart = Depends(get_orgchart_service)):
#     return