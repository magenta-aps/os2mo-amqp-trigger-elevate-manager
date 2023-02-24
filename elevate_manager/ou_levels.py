# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

# Modul containing functions for handling the actual business logic
# of the application

import structlog
from more_itertools import one
# TODO: add return type
from elevate_manager.models.get_org_unit_levels import GetOrgUnitLevels, \
    OrganisationUnit

logger = structlog.get_logger(__name__)


# Make it possible to add or adjust org unit levels (as we have seen examples
# of org unit levels called "NY3½-niveau !?)
ORG_UNIT_LEVELS = {
    "Afdelings-niveau": -100,
    "NY0-niveau": 0,
    "NY1-niveau": 100,
    "NY2-niveau": 200,
    "NY3-niveau": 300,
    "NY4-niveau": 400,
    "NY5-niveau": 500,
    "NY6-niveau": 600,
}


def _get_org_unit_level(org_unit: OrganisationUnit) -> int | None:
    ou_level_name = org_unit.org_unit_level.name
    ou_level = ORG_UNIT_LEVELS.get(ou_level_name)
    if ou_level is None:
        logger.error(
            "Unknown org unit level for org unit!", org_unit=org_unit
        )
    return ou_level


def get_new_org_unit_for_engagement(
    org_unit_levels: GetOrgUnitLevels
) -> OrganisationUnit | None:
    """
    Extract the OU level of the OU where the manager update occurred and OU
    level of the OU of the units where the manager has an engagement and
    compare the OU levels.

    NOTE: log an error if the manager does not have exactly one and do not
    perform any engagement movements in this case!

    Args:
        org_unit_levels: The object to be parsed object returned from
          mo.get_org_unit_levels

    Returns:
        If the OU level of the OU where the manager update occurred is higher
        than the OU level of the OU where the manager has engagements then
        return the OU where the manager update occurred and else return None.
    """

    # Get the objects from the GraphQL response
    manager_objects = one(one(org_unit_levels.data.managers).objects)

    # Get numeric value of the manager org unit level
    manager_org_unit = one(manager_objects.org_unit)
    manager_org_unit_level = _get_org_unit_level(manager_org_unit)
    if manager_org_unit_level is None:
        return

    employee = one(manager_objects.employee)
    try:
        manager_engagement = one(employee.engagements)
    except ValueError:
        logger.error("Manager has more than one engagement! "
                     "No engagement moves performed")
        return

    # Get numeric value of the engagement org unit level
    engagement_org_unit = one(manager_engagement.org_unit)
    engagement_org_unit_level = _get_org_unit_level(engagement_org_unit)
    if engagement_org_unit_level is None:
        return

    logger.debug(
        "Org unit levels",
        manager_org_unit_level=manager_org_unit_level,
        engagement_org_unit_level=engagement_org_unit_level
    )

    if manager_org_unit_level > engagement_org_unit_level:
        return manager_org_unit

    return
