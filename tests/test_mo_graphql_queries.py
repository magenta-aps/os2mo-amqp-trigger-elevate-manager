import datetime
import unittest.mock

import pytest
from unittest.mock import AsyncMock
from uuid import UUID
from uuid import uuid4
from pydantic import parse_obj_as

from elevate_manager.models.get_org_unit_levels import GetOrgUnitLevels
from elevate_manager.models.get_existing_managers import GetExistingManagers
from elevate_manager.mo import (
    get_org_unit_levels,
    get_existing_managers,
    terminate_existing_managers,
    elevate_engagements,
    QUERY_FOR_GETTING_ORG_UNIT_LEVELS,
    QUERY_FOR_GETTING_EXISTING_MANAGERS,
    MUTATION_FOR_TERMINATING_MANAGER,
    MUTATION_FOR_UPDATING_ENGAGEMENT,
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


@pytest.mark.asyncio
async def test_get_org_unit_levels():
    """Tests if the function call was awaited and that the response data
    is parsed with the expected model."""
    # ARRANGE
    manager_uuid = uuid4()
    # Mock the GraphQL client, as this makes an actual DB call,
    # and we need to mock this behaviour out.
    mocked_gql_client = AsyncMock()
    # Parse the object returned from the response to our GetOrgUnitLevels model.
    parsed_org_unit_level_response = parse_obj_as(
        GetOrgUnitLevels, {"data": org_unit_level_response}
    )

    # Assign a mocked return value to the GraphQL client call. This behaves as
    # if the client was executed, and this value would have been returned.
    mock_execute = AsyncMock(return_value=org_unit_level_response)
    mocked_gql_client.execute = mock_execute

    # ACT
    actual_org_unit_levels_response = await get_org_unit_levels(
        gql_client=mocked_gql_client, manager_uuid=manager_uuid
    )

    # ASSERT
    assert actual_org_unit_levels_response == parsed_org_unit_level_response
    mock_execute.assert_awaited_once_with(
        QUERY_FOR_GETTING_ORG_UNIT_LEVELS,
        variable_values={"manager_uuid": str(manager_uuid)},
    )


@pytest.mark.asyncio
async def test_get_existing_managers():
    """Tests if the function call was awaited and that the response data
    is parsed with the expected model."""
    # ARRANGE
    org_unit_uuid = uuid4()
    mocked_gql_client = AsyncMock()

    parsed_managers_response = parse_obj_as(
        GetExistingManagers, {"data": managers_response}
    )

    mock_execute = AsyncMock(return_value=managers_response)
    mocked_gql_client.execute = mock_execute

    actual_managers_response = await get_existing_managers(
        gql_client=mocked_gql_client, org_unit_uuid=org_unit_uuid
    )

    # Assert if the actual response is the same as the one parsed.
    assert actual_managers_response == parsed_managers_response
    mock_execute.assert_awaited_once_with(
        QUERY_FOR_GETTING_EXISTING_MANAGERS,
        variable_values={"uuids": str(org_unit_uuid)},
    )


@pytest.mark.asyncio
async def test_terminate_existing_managers():
    """
    Tests if the function call was awaited and that the mutation
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
async def test_elevate_engagements():
    """Tests if the function call was awaited and that the mutation was executed."""
    # ARRANGE
    org_unit_uuid = uuid4()
    engagement_uuid = uuid4()
    mocked_gql_client = AsyncMock()

    mock_execute = AsyncMock()
    mocked_gql_client.execute = mock_execute

    # ACT
    await elevate_engagements(
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
