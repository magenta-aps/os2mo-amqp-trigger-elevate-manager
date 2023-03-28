import unittest.mock
from unittest.mock import AsyncMock
from uuid import uuid4, UUID
import pytest
import time
import datetime
from unittest.mock import patch
from pydantic import parse_obj_as
from ramqp.mo.models import PayloadType
from elevate_manager.events import process_manager_event
from elevate_manager.main import listener


process_manager = {
    "data": {"engagement_update": {"uuid": "55cf8c17-d619-4a06-8a88-b2a63b4155e1"}}
}


@pytest.mark.asyncio
@patch("elevate_manager.mo.elevate_engagement")
async def test_listener(mock_elevate_engagement: AsyncMock):
    print("************************", mock_elevate_engagement)
    # ARRANGE
    gql_client = AsyncMock()
    gql_client.side_effect = []
    context = {"graphql_session": gql_client}

    payload = PayloadType(uuid=uuid4(), object_uuid=UUID("87a47459-d1ac-48f5-809a-6d7f607a7f6d"),
                          time=datetime.datetime.now())
    # ACT
    await listener(context, payload)

    mock_elevate_engagement.assert_awaited()

    # ARRANGE
    # mocked_gql_client_from_context = AsyncMock()
    # mock_execute = AsyncMock(return_value=process_manager)
    # mocked_gql_client_from_context.execute = mock_execute
    #
    # payload = AsyncMock(return_value=uuid4())


    #
    # mocked_gql_client_from_context = AsyncMock()
    # mocked_gql_client_from_context.x.return_value = process_manager
    # payload = AsyncMock()
    # payload.return_value = uuid4()
    # # payload_type_for_uuid = AsyncMock(return_value=object_uuid)
    #
    # await listener(mocked_gql_client_from_context.x(), payload)


    #mock_execute.assert_awaited_once_with(process_manager, payload.object_uuid)
