# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from more_itertools import one
from pydantic import parse_obj_as

from elevate_manager.models.get_org_unit_levels import GetOrgUnitLevels
from elevate_manager.ou_levels import get_new_org_unit_for_engagement

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
                                                "parent_uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
                                                "org_unit_level": {
                                                    "name": "OVERRIDE IN TEST",
                                                    "uuid": "84f95e29-48a0-4175-85fd-84a1f596e1a4"
                                                }
                                            }
                                        ]
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
                                    "uuid": "84f95e29-48a0-4175-85fd-84a1f596e1a4"
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
}


def test_get_new_org_unit_for_engagement():
    # Arrange
    org_unit_levels = parse_obj_as(GetOrgUnitLevels, graphql_response)
    objects = one(one(org_unit_levels.data.managers).objects)
    manager_ou = one(objects.org_unit)

    # Set manager OU level
    manager_ou.org_unit_level.name = "NY6-niveau"
    # Set engagement ou level
    one(one(one(objects.employee).engagements).org_unit).org_unit_level.name = "NY5-niveau"

    # Act
    org_unit = get_new_org_unit_for_engagement(org_unit_levels)

    # Assert
    assert org_unit == manager_ou
