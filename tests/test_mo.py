import datetime
import unittest.mock
from unittest.mock import AsyncMock
from uuid import UUID
from uuid import uuid4

import pytest
from pydantic import parse_obj_as

from elevate_manager.mo import get_existing_managers
from elevate_manager.mo import get_manager_engagements
from elevate_manager.mo import move_engagement
from elevate_manager.mo import MUTATION_FOR_TERMINATING_MANAGER
from elevate_manager.mo import MUTATION_FOR_UPDATING_ENGAGEMENT
from elevate_manager.mo import QUERY_FOR_GETTING_EXISTING_MANAGERS
from elevate_manager.mo import QUERY_FOR_GETTING_MANAGER_ENGAGEMENTS
from elevate_manager.mo import terminate_existing_managers
from elevate_manager.models.get_existing_managers import GetExistingManagers
from elevate_manager.models.get_manager_engagements_uuids import (
    GetManagerEngagementUuids,
)


org_unit_level_response = {
    "managers": [
        {
            "objects": [
                {
                    "employee": [
                        {
                            "engagements": [
                                {
                                    "uuid": "141c39db-7ce0-4332-b4e4-a4d2114b0f51",
                                    "user_key": "-",
                                    "org_unit": [
                                        {
                                            "name": "Borgmesterens Afdeling",
                                            "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
                                            "parent_uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",  # noqa: E501
                                            "org_unit_level": {
                                                "name": "NY5-niveau",
                                                "uuid": "84f95e29-48a0-4175-85fd-84a1f596e1a4",
                                            },
                                        }
                                    ],
                                }
                            ]
                        }
                    ],
                    "org_unit": [
                        {
                            "name": "Borgmesterens Afdeling",
                            "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
                            "org_unit_level": {
                                "name": "NY6-niveau",
                                "uuid": "84f95e29-48a0-4175-85fd-84a1f596e1a4",
                            },
                        }
                    ],
                }
            ]
        }
    ]
}

managers_empty_response = {
    "org_units": [
        {
            "objects": [
                {
                    "name": "Budget og Planlægning",
                    "uuid": "1f06ed67-aa6e-4bbc-96d9-2f262b9202b5",
                    "managers": [],
                }
            ]
        }
    ]
}

managers_response = {
    "org_units": [
        {
            "objects": [
                {
                    "name": "Budget og Planlægning",
                    "uuid": "1f06ed67-aa6e-4bbc-96d9-2f262b9202b5",
                    "managers": [{"uuid": "5a988dee-109a-4353-95f2-fb414ea8d605"}],
                }
            ]
        }
    ]
}

multiple_managers_response = {
    "org_units": [
        {
            "objects": [
                {
                    "name": "Budget og Planlægning",
                    "uuid": "1f06ed67-aa6e-4bbc-96d9-2f262b9202b5",
                    "managers": [
                        {"uuid": "5a988dee-109a-4353-95f2-fb414ea8d605"},
                        {"uuid": "12388dee-109a-4353-95f2-fb414ea84321"},
                        {"uuid": "98788dee-109a-4353-95f2-fb414ea8d789"},
                    ],
                }
            ]
        }
    ]
}

manager_one_engagement_response = {
    "managers": [
        {
            "objects": [
                {
                    "employee": [
                        {
                            "engagements": [
                                {"uuid": "fa5e2af6-ae28-4b6b-8895-3b7d39f93d54"}
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}


@pytest.mark.asyncio
async def test_get_manager_engagements():
    """Tests if the GraphQL execute coroutine was awaited and that the response data
    is parsed as we expect it in accordance with the models defined by QuickType."""
    manager_uuid = uuid4()
    mocked_gql_client = AsyncMock()

    expected_managers = parse_obj_as(
        GetManagerEngagementUuids, {"data": manager_one_engagement_response}
    )

    mock_execute = AsyncMock(return_value=manager_one_engagement_response)
    mocked_gql_client.execute = mock_execute

    actual_manager_response = await get_manager_engagements(
        gql_client=mocked_gql_client, manager_uuid=manager_uuid
    )

    assert actual_manager_response == expected_managers
    mock_execute.assert_awaited_once_with(
        QUERY_FOR_GETTING_MANAGER_ENGAGEMENTS,
        variable_values={"manager_uuid": str(manager_uuid)},
    )


@pytest.mark.asyncio
async def test_get_existing_managers():
    """Tests if the GraphQL execute coroutine was awaited and that the response data
    is parsed with the expected model."""
    # ARRANGE
    org_unit_uuid = uuid4()
    mocked_gql_client = AsyncMock()

    expected_managers_response = parse_obj_as(
        GetExistingManagers, {"data": managers_response}
    )

    mock_execute = AsyncMock(return_value=managers_response)
    mocked_gql_client.execute = mock_execute

    # ACT
    actual_managers_response = await get_existing_managers(
        gql_client=mocked_gql_client, org_unit_uuid=org_unit_uuid
    )

    # Assert if the actual response is the same as the one parsed.
    assert actual_managers_response == expected_managers_response
    mock_execute.assert_awaited_once_with(
        QUERY_FOR_GETTING_EXISTING_MANAGERS,
        variable_values={"uuids": str(org_unit_uuid)},
    )


@pytest.mark.asyncio
async def test_terminate_existing_managers_awaited():
    """
    Tests if the GraphQL execute coroutine was awaited and that the mutation
    was executed with the length of the list of manager uuids.
    """
    # ARRANGE
    # Actual uuid of the manager, that has been assigned this Organisation Unit.
    # This uuid is therefore NOT to be terminated in our function call.
    manager_uuid = UUID("5a988dee-109a-4353-95f2-fb414ea8d605")
    parsed_managers_response = parse_obj_as(
        GetExistingManagers, {"data": multiple_managers_response}
    )
    mocked_gql_client = AsyncMock()

    mock_execute = AsyncMock()
    mocked_gql_client.execute = mock_execute

    # ACT
    await terminate_existing_managers(
        mocked_gql_client, parsed_managers_response, manager_uuid
    )

    # ASSERT
    # Asserting for the length of the managers list, which should exclude the
    # manager uuid provided in the function call that matches the objects' payload,
    assert len(mock_execute.call_args_list) == 2

    # The first element in the list should be the call to be terminated.
    assert mock_execute.call_args_list[0] == unittest.mock.call(
        MUTATION_FOR_TERMINATING_MANAGER,
        variable_values={
            "input": {
                "uuid": "12388dee-109a-4353-95f2-fb414ea84321",
                "to": datetime.date.today().isoformat(),
            }
        },
    )
    # This should match the second call of termination.
    assert mock_execute.call_args_list[1] == unittest.mock.call(
        MUTATION_FOR_TERMINATING_MANAGER,
        variable_values={
            "input": {
                "uuid": "98788dee-109a-4353-95f2-fb414ea8d789",
                "to": datetime.date.today().isoformat(),
            }
        },
    )


@pytest.mark.asyncio
async def test_terminate_existing_manager_not_awaited():
    """
    Test to verify the GraphQL execute coroutine is not awaited and that the mutation
    was executed with only 1 manager uuid.
    """
    # ARRANGE
    manager_uuid = UUID("5a988dee-109a-4353-95f2-fb414ea8d605")
    parsed_managers_response = parse_obj_as(
        GetExistingManagers, {"data": managers_response}  # Only 1 previous manager.
    )
    mocked_gql_client = AsyncMock()

    mock_execute = AsyncMock()
    mocked_gql_client.execute = mock_execute

    # ACT
    await terminate_existing_managers(
        mocked_gql_client, parsed_managers_response, manager_uuid
    )

    # ASSERT
    mock_execute.assert_not_awaited()  # Awaited 0 times.


@pytest.mark.asyncio
async def test_no_existing_manager_to_terminate_and_not_awaited():
    """
    Test to verify the GraphQL execute coroutine is not awaited and that the mutation
    was executed with only 1 manager uuid.
    """
    # ARRANGE
    manager_uuid = UUID("12388dee-109a-4353-95f2-fb414ea84321")
    parsed_empty_managers_response = parse_obj_as(
        GetExistingManagers, {"data": managers_empty_response}  # No previous manager.
    )
    mocked_gql_client = AsyncMock()

    mock_execute = AsyncMock()
    mocked_gql_client.execute = mock_execute

    # ACT
    await terminate_existing_managers(
        mocked_gql_client, parsed_empty_managers_response, manager_uuid
    )

    # ASSERT
    mock_execute.assert_not_awaited()  # Awaited 0 times.


@pytest.mark.asyncio
async def test_elevate_engagements():
    """Tests if the GraphQL execute coroutine was awaited and that the mutation was executed."""
    # ARRANGE
    org_unit_uuid = uuid4()
    engagement_uuid = uuid4()
    mocked_gql_client = AsyncMock()

    mock_execute = AsyncMock()
    mocked_gql_client.execute = mock_execute

    # ACT
    await move_engagement(
        gql_client=mocked_gql_client,
        org_unit_uuid=org_unit_uuid,
        engagement_uuid=engagement_uuid,
    )

    # ASSERT
    mock_execute.assert_awaited_once_with(
        MUTATION_FOR_UPDATING_ENGAGEMENT,
        variable_values={
            "input": {
                "uuid": str(engagement_uuid),
                "validity": {"from": datetime.date.today().isoformat()},
                "org_unit": str(org_unit_uuid),
            }
        },
    )
