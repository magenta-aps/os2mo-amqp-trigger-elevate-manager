# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import one
from pydantic import parse_obj_as

from elevate_manager.models.get_org_unit_levels import GetOrgUnitLevels
from elevate_manager.models.get_org_unit_levels import OrganisationUnit
from elevate_manager.ou_levels import (
    get_new_org_unit_for_engagement,
    _get_org_unit_level,
)

graphql_response = {
    "data": {
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
                                                    "name": "OVERRIDE IN TEST",
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
                                    "name": "OVERRIDE IN TEST",
                                    "uuid": "84f95e29-48a0-4175-85fd-84a1f596e1a4",
                                },
                            }
                        ],
                    }
                ]
            }
        ]
    }
}

graphql_response2 = {
    "data": {
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
                                    },
                                    {
                                        "uuid": "499049e6-bb46-4b4d-a535-57850a8be2e7",
                                        "user_key": "-",
                                        "org_unit": [
                                            {
                                                "name": "IT-Support",
                                                "uuid": "9b7b3dde-16c9-4f88-87cc-e03aa5b4e709",
                                                "parent_uuid": "7a8e45f7-4de0-44c8-990f-43c0565ee505",  # noqa: E501
                                                "org_unit_level": {
                                                    "name": "NY5-niveau",
                                                    "uuid": "c553d5fd-0768-4907-9d34-14757c87454c",
                                                },
                                            }
                                        ],
                                    },
                                ],
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
}


@pytest.mark.parametrize(
    "manager_ou_level_name,eng_ou_level_name,expected",
    [
        (
            "NY6-niveau",
            "NY5-niveau",
            parse_obj_as(
                OrganisationUnit,
                {
                    "name": "Borgmesterens Afdeling",
                    "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
                    "org_unit_level": {
                        "name": "NY6-niveau",
                        "uuid": "84f95e29-48a0-4175-85fd-84a1f596e1a4",
                    },
                },
            ),
        ),
        ("NY5-niveau", "NY6-niveau", None),
        ("NY5-niveau", "NY5-niveau", None),
        # Tests if Organisation Unit returns None, if level is not recognized.
        ("Non-recognized Level", "NY3-niveau", None),
    ],
)
def test_get_new_org_unit_for_engagement(
    manager_ou_level_name, eng_ou_level_name, expected
):
    # Arrange
    org_unit_levels = parse_obj_as(GetOrgUnitLevels, graphql_response)
    objects = one(one(org_unit_levels.data.managers).objects)
    manager_ou = one(objects.org_unit)

    # Set manager OU level
    manager_ou.org_unit_level.name = manager_ou_level_name
    # Set engagement ou level
    one(
        one(one(objects.employee).engagements).org_unit
    ).org_unit_level.name = eng_ou_level_name

    # Act
    org_unit = get_new_org_unit_for_engagement(org_unit_levels)

    # Assert
    assert org_unit == expected


# TODO: add non happy path tests


@pytest.mark.parametrize(
    "org_unit_payload_to_be_parsed, expected_result_integer_representation",
    [
        (
            {
                "name": "Borgmesterens Afdeling",
                "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
                "org_unit_level": {
                    "name": "NY6-niveau",
                    "uuid": "84f95e29-48a0-4175-85fd-84a1f596e1a4",
                },
            },
            600,
        ),
        (
            {
                "name": "Borgmesterens Afdeling",
                "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
                "org_unit_level": {
                    "name": "NY0-niveau",
                    "uuid": "84f95e29-48a0-4175-85fd-84a1f596e1a4",
                },
            },
            0,
        ),
        (
            {
                "name": "Borgmesterens Afdeling",
                "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
                "org_unit_level": {
                    "name": "This should return None",
                    "uuid": "84f95e29-48a0-4175-85fd-84a1f596e1a4",
                },
            },
            None,
        ),
    ],
)
def test__get_org_unit_level_helper(
    org_unit_payload_to_be_parsed, expected_result_integer_representation
):
    """Tests if the helper function to retrieve the Organisation Unit's level returns
    the correct value and returns None if it doesn't recognize the naming convention
    attributed to the Organisation Units level."""
    # Insert the payload to the model and parse it correctly.
    organisation_unit_payload = parse_obj_as(
        OrganisationUnit, org_unit_payload_to_be_parsed
    )

    # Extract the Organisation Unit's integer value mapped to the key (i.e. "NY1-niveau" is mapped to 100).
    org_unit_levels_integer_representation = _get_org_unit_level(
        organisation_unit_payload
    )

    # Assert the correct mapping of the keys. If name does not exist as key, return None.
    assert (
        org_unit_levels_integer_representation == expected_result_integer_representation
    )


@pytest.mark.parametrize(
    "payloads_to_be_parsed, expected_exception",
    [(graphql_response2, ValueError), (graphql_response, None)],
)
def test_exception_in_get_new_org_unit_for_engagement(
    payloads_to_be_parsed, expected_exception
):
    if expected_exception:
        with pytest.raises(expected_exception):
            org_unit_levels = parse_obj_as(GetOrgUnitLevels, payloads_to_be_parsed)
            get_new_org_unit_for_engagement(org_unit_levels)
