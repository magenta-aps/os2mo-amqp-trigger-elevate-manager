import unittest.mock
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydantic import parse_obj_as

from elevate_manager.events import process_manager_event
from elevate_manager.models.get_existing_managers import GetExistingManagers
from elevate_manager.models.get_manager_engagements_uuids import Engagement
from elevate_manager.models.get_manager_engagements_uuids import (
    GetManagerEngagementUuids,
)


@pytest.mark.asyncio
@unittest.mock.patch("elevate_manager.events.get_manager_engagements")
@unittest.mock.patch("elevate_manager.events.logger")
async def test_process_manager_event_none_when_no_engagements_found_in_manager_obj(
    mock_events_logger, mock_get_managers_function
):
    """
    Tests if:
    1) process_manager_event returns None when no engagement found in
       manager object.
    2) logging message gets properly logged with correct error level.
    """
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
async def test_process_manager_event_none_when_no_manager_obj_found(
    mock_events_logger, mock_get_managers_function
):
    """
    Tests if:
    1) process_manager_event returns None when no manager object found.
    2) logging message gets properly logged with correct error level.
    """

    # ARRANGE
    manager_no_objects: dict = {"managers": [{"objects": []}]}
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
@pytest.mark.parametrize(
    "engagements", [[], [Engagement(uuid=str(uuid4())), Engagement(uuid=str(uuid4()))]]
)
@unittest.mock.patch("elevate_manager.events.get_manager_engagements")
@unittest.mock.patch("elevate_manager.events.logger")
async def test_process_manager_event_none_when_manager_does_not_have_one_engagement(
    mock_events_logger, mock_get_managers_function, engagements
):
    """
    Tests if:
    1) process_manager_event returns None when manager does not have exactly
       one engagement.
    2) logging message gets properly logged with correct error level.
    """
    manager_no_engagements: dict = {
        "managers": [{"objects": [{"employee": [{"engagements": engagements}]}]}]
    }
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


@unittest.mock.patch("elevate_manager.events.terminate_existing_managers")
@unittest.mock.patch("elevate_manager.events.get_existing_managers")
@unittest.mock.patch("elevate_manager.events.get_manager_engagements")
async def test_terminate_managers_when_existing_managers_present(
    mock_get_manager_engagements: AsyncMock,
    mock_get_existing_managers: AsyncMock,
    mock_terminate_existing_managers: AsyncMock,
):
    """Test that any existing managers are terminated"""

    # ARRANGE

    graphql_manager_engagements = {
        "data": {
            "managers": [
                {"objects": [{"employee": [{"engagements": [{"uuid": str(uuid4())}]}]}]}
            ]
        }
    }
    manager_engagements = parse_obj_as(
        GetManagerEngagementUuids, graphql_manager_engagements
    )
    mock_get_manager_engagements.return_value = manager_engagements

    graphql_existing_managers_resp = {
        "data": {
            "org_units": [
                {
                    "objects": [
                        {
                            "managers": [
                                {"uuid": str(uuid4()), "user_key": "some manager 1"},
                                {"uuid": str(uuid4()), "user_key": "some manager 2"},
                            ]
                        }
                    ]
                }
            ]
        }
    }
    existing_managers = parse_obj_as(
        GetExistingManagers, graphql_existing_managers_resp
    )
    mock_get_existing_managers.return_value = existing_managers

    gql_client = AsyncMock()
    manager_uuid = uuid4()

    # ACT
    await process_manager_event(
        gql_client=gql_client,
        manager_uuid=manager_uuid,
        org_unit_uuid_of_manager=uuid4(),
    )

    # ASSERT
    mock_terminate_existing_managers.assert_awaited_once_with(
        gql_client, existing_managers, manager_uuid
    )
