# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from ramqp.mo.models import PayloadType  # type: ignore

from elevate_manager.main import listener


@pytest.mark.asyncio
async def test_listener():
    # Arrange
    mock_graphql_client = AsyncMock()

    org_unit_uuid = uuid4()
    manager_uuid = uuid4()
    payload = PayloadType(uuid=org_unit_uuid, object_uuid=manager_uuid, time=datetime.now())

    # Act
    await listener({"graphql_session": mock_graphql_client}, payload)

    # Assert
    

# TODO: test listener decorated with create and edit but not terminate
