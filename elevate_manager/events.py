# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import structlog
from more_itertools import one
from raclients.graph.client import PersistentGraphQLClient  # type: ignore

from .mo import get_existing_managers
from .mo import get_manager_engagements
from .mo import move_engagement
from .mo import terminate_existing_managers

logger = structlog.get_logger(__name__)


async def process_manager_event(
    gql_client: PersistentGraphQLClient,
    manager_uuid: UUID,
    manager_org_unit_uuid: UUID,
) -> None:
    """
    We process the various events made to an organisation unit and its manager.
    This includes finding the managers potential engagement, terminating existing
    manager(s) if the organisation unit has pre-existing manager(s) occupying the
    position and transferring the new managers engagement so that it sits
    appropriately in the same organisation unit where the manager role resides.

    Args:
        gql_client: A GraphQL client to perform the various queries
        manager_uuid: UUID of the new manager
        manager_org_unit_uuid: UUID of the new managers organisation unit
    """
    logger.debug(
        "Processing manager event",
        manager_uuid=manager_uuid,
        ou_uuid=manager_org_unit_uuid,
    )

    # Trying to handle the possibility of the manager not being an employee.
    try:
        manager_engagements = await get_manager_engagements(gql_client, manager_uuid)
    # Return None gracefully, if the manager object has no employee attached to it.
    except ValueError:
        logger.error("No employee was found in the manager object")
        return None

    try:
        # Extracting manager objects.
        manager_objects = one(one(manager_engagements.data.managers).objects)  # type: ignore
    except ValueError:
        logger.error("No manager objects found")
        return None

    # This should always return one employee.
    employee = one(manager_objects.employee)

    # Trying to handle the possibility of multiple engagements attached to the manager.
    try:
        employee_engagement = one(employee.engagements)
    # Return None gracefully, since we, as of now, do not know which engagement to change.
    except ValueError:
        logger.error(
            "Manager does not have exactly one engagement, and engagement can not be moved"
        )
        return None

    # Uuid of engagement to move to the managers new organisation unit.
    engagement_uuid_to_be_moved = UUID(employee_engagement.uuid)

    logger.info(
        "Moving manager engagement and terminate old manager(s)",
        new_ou_for_eng=manager_org_unit_uuid,
    )

    # Finding potential existing managers.
    existing_managers = await get_existing_managers(
        manager_org_unit_uuid, gql_client
    )
    # Terminating pre-existing managers.
    await terminate_existing_managers(
        gql_client,
        existing_managers,
        manager_uuid,
    )
    logger.info("All existing managers now terminated")
    # Moving engagement to managers new organisation unit.

    await move_engagement(
        gql_client, manager_org_unit_uuid, engagement_uuid_to_be_moved
    )

    logger.info("Manager engagement successfully moved")
