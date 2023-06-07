import unittest.mock
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydantic import parse_obj_as

from elevate_manager.events import process_manager_event
from elevate_manager.models.get_manager_engagements_uuids import (
    GetManagerEngagementUuids,
)


manager_no_objects: dict = {"managers": [{"objects": []}]}


manager_no_engagements: dict = {
    "managers": [{"objects": [{"employee": [{"engagements": []}]}]}]
}


@pytest.mark.asyncio
@unittest.mock.patch("elevate_manager.events.get_manager_engagements")
@unittest.mock.patch("elevate_manager.events.logger")
async def test_logger_logging_message_correct(
    mock_events_logger, mock_get_managers_function
):
    """Tests if logging message gets properly logged with correct error level."""
    # ARRANGE
    manager_uuid = uuid4()
    org_unit_uuid = uuid4()
    mocked_gql_client = AsyncMock()
    mock_get_managers_function.side_effect = ValueError()

    # ACT
    result = await process_manager_event(
        gql_client=mocked_gql_client,
        manager_uuid=manager_uuid,
        org_unit_uuid_of_manager=org_unit_uuid,
    )

    # ASSERT
    assert result is None
    mock_events_logger.error.assert_any_call(
        "No employee was found in the manager object"
    )


@pytest.mark.asyncio
@unittest.mock.patch("elevate_manager.events.get_manager_engagements")
@unittest.mock.patch("elevate_manager.events.logger")
async def test_no_objects_message_value(mock_events_logger, mock_get_managers_function):
    """Tests if logging message gets properly logged with correct error level."""
    # ARRANGE
    expected_manager_response_with_no_engagement = parse_obj_as(
        GetManagerEngagementUuids, {"data": manager_no_objects}
    )

    mock_get_managers_function.return_value = (
        expected_manager_response_with_no_engagement
    )

    # ACT
    result = await process_manager_event(
        gql_client=AsyncMock(),
        manager_uuid=uuid4(),
        org_unit_uuid_of_manager=uuid4(),
    )

    # ASSERT
    assert result is None
    mock_events_logger.error.assert_any_call("No manager objects found")


@pytest.mark.asyncio
@unittest.mock.patch("elevate_manager.events.get_manager_engagements")
@unittest.mock.patch("elevate_manager.events.logger")
async def test_not_only_one_manager_object_message_value(
    mock_events_logger, mock_get_managers_function
):
    """Tests if logging message gets properly logged with correct error level."""
    # ARRANGE
    expected_manager_response_with_no_engagement = parse_obj_as(
        GetManagerEngagementUuids, {"data": manager_no_engagements}
    )

    mock_get_managers_function.return_value = (
        expected_manager_response_with_no_engagement
    )

    # ACT
    result = await process_manager_event(
        gql_client=AsyncMock(),
        manager_uuid=uuid4(),
        org_unit_uuid_of_manager=uuid4(),
    )

    # ASSERT
    assert result is None
    mock_events_logger.error.assert_any_call(
        "Manager does not have exactly one engagement, and engagement can not be moved"
    )
