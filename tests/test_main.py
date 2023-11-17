# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from ramqp.mo.models import PayloadType  # type: ignore

from elevate_manager.main import listener


@pytest.mark.asyncio
@patch("elevate_manager.main.process_manager_event")
async def test_listener(mock_process_manager_event: AsyncMock):
    # Arrange
    payload = PayloadType(uuid=uuid4(), object_uuid=uuid4(), time=datetime(2000, 1, 1))
    mock_graphql_session = MagicMock()
    context = {"graphql_session": mock_graphql_session}

    # Act
    await listener(context, payload)

    # Assert
    mock_process_manager_event.assert_awaited_once_with(
        mock_graphql_session, payload.object_uuid
    )
