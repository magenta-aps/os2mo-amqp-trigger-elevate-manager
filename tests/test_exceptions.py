import unittest.mock
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from elevate_manager.events import process_manager_event


@pytest.mark.asyncio
async def test_error_message_value():
    """Tests if ValueError behaves as we want it."""
    # ARRANGE
    with pytest.raises(ValueError) as exc_info:
        # ACT
        raise ValueError("Display error message for testing purposes")
    # ASSERT
    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "Display error message for testing purposes"


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
