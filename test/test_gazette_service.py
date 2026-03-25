import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.gazette_service import GazetteService
from src.exception.exceptions import InternalServerError, NotFoundError
from src.models.organisation_schemas import Entity


@pytest.mark.asyncio
async def test_get_gazette_data_points_success(gazette_service, mock_opengin_service):

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

    result = await gazette_service.get_gazette_data_points()

    assert "2023" in result
    assert result["2023"][0] == 2
    assert result["2023"][1] == 1
    assert all(count == 0 for i, count in enumerate(result["2023"]) if i not in [0, 1])

    assert "2024" in result
    assert result["2024"][4] == 2
    assert all(count == 0 for i, count in enumerate(result["2024"]) if i != 4)

    # Verify sorting
    assert list(result.keys()) == ["2023", "2024"]


@pytest.mark.asyncio
async def test_get_gazette_data_points_empty(gazette_service, mock_opengin_service):
    mock_opengin_service.get_entities.side_effect = NotFoundError("not found")

    result = await gazette_service.get_gazette_data_points()

    assert result == {}


@pytest.mark.asyncio
async def test_get_gazette_data_points_internal_server_error(
    gazette_service, mock_opengin_service
):
    with patch(
        "src.services.gazette_service.asyncio.gather", side_effect=Exception("failure")
    ):
        with pytest.raises(InternalServerError):
            await gazette_service.get_gazette_data_points()
