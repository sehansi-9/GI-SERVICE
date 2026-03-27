import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.document_service import DocumentService
from src.exception.exceptions import InternalServerError, NotFoundError
from src.models.organisation_schemas import Entity


@pytest.mark.asyncio
async def test_get_gazette_data_points_success(document_service, mock_opengin_service):

    org_gazette_1 = MagicMock()
    org_gazette_1.created = "2023-01-15T10:00:00Z"
    org_gazette_2 = MagicMock()
    org_gazette_2.created = "2023-01-20T12:00:00Z"
    org_gazette_3 = MagicMock()
    org_gazette_3.created = "2024-05-05T08:00:00Z"

    person_gazette_1 = MagicMock()
    person_gazette_1.created = "2023-02-10T14:00:00Z"
    person_gazette_2 = MagicMock()
    person_gazette_2.created = "2024-05-25T16:00:00Z"

    mock_opengin_service.get_entities.side_effect = [
        [
            org_gazette_1,
            org_gazette_2,
            org_gazette_3,
        ],
        [person_gazette_1, person_gazette_2],
    ]

    result = await document_service.get_gazette_data_points()

    assert "years" in result
    assert len(result["years"]) == 2
    assert result["years"][0]["year"] == 2023
    assert result["years"][0]["values"][0] == 2
    assert result["years"][0]["values"][1] == 1
    assert all(count == 0 for i, count in enumerate(result["years"][0]["values"]) if i not in [0, 1])

    assert result["years"][1]["year"] == 2024
    assert result["years"][1]["values"][4] == 2
    assert all(count == 0 for i, count in enumerate(result["years"][1]["values"]) if i != 4)

    # Verify sorting
    assert [y["year"] for y in result["years"]] == [2023, 2024]


@pytest.mark.asyncio
async def test_get_gazette_data_points_empty(document_service, mock_opengin_service):
    mock_opengin_service.get_entities.side_effect = NotFoundError("not found")

    result = await document_service.get_gazette_data_points()

    assert result == {"years": []}


@pytest.mark.asyncio
async def test_get_gazette_data_points_internal_server_error(
    document_service, mock_opengin_service
):
    with patch(
        "src.services.document_service.asyncio.gather", side_effect=Exception("failure")
    ):
        with pytest.raises(InternalServerError):
            await document_service.get_gazette_data_points()
