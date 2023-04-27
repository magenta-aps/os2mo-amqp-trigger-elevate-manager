# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import structlog
from more_itertools import one
from raclients.graph.client import PersistentGraphQLClient  # type: ignore

from .mo import elevate_engagement
from .mo import get_engagements_and_org_unit_uuids_for_manager
from .mo import get_existing_managers
from .mo import terminate_existing_managers

logger = structlog.get_logger(__name__)


async def process_manager_event(
    gql_client: PersistentGraphQLClient,
    new_manager_uuid: UUID,
    org_unit_uuid_of_new_manager: UUID,
) -> None:
    """
    We process the various events made to an Organisation Unit and its manager.
    This includes finding the managers potential engagement, terminating existing
    manager(s) if the Organisation Unit has pre-existing manager(s) occupying the
    position, editing and transferring the new managers engagement so that it sits
    appropriately in the same Organisation Unit where the manager role resides.

    :param gql_client:
    A GraphQL client to perform the various queries

    :param new_manager_uuid:
    Uuid of the new manager

    :param org_unit_uuid_of_new_manager:
    Uuid of the new managers Organisation Unit

    :return:
    A successful transfer of an engagement or None
    """
    logger.debug(
        "Processing manager event",
        manager_uuid=new_manager_uuid,
        ou_uuid=org_unit_uuid_of_new_manager,
    )

    # Trying to handle the possibility of the manager not being an employee.
    try:
        new_managers_engagement_uuid = (
            await get_engagements_and_org_unit_uuids_for_manager(
                gql_client, new_manager_uuid
            )
        )
    # Return None gracefully, if the manager object has no employee attached to it.
    except ValueError:
        logger.error("No employee was found in the manager object")
        return None

    # Extracting manager objects.
    manager_objects = one(one(new_managers_engagement_uuid.data.managers).objects)  # type: ignore
    # This should always return one employee.
    employee = one(manager_objects.employee)

    # Trying to handle the possibility of multiple engagements attached to the manager.
    try:
        employee_engagements = one(employee.engagements)

    # Return None gracefully, since we, as of now, do not know which engagement to change.
    except ValueError:
        logger.error(
            "Manager does not have exactly one engagement, and engagement can not be moved"
        )
        return None
    # Uuid of engagement to move to the managers new Organisation Unit.
    engagement_uuid_to_be_moved = UUID(employee_engagements.uuid)

    # If the Organisation Unit exists.
    if org_unit_uuid_of_new_manager is not None:
        logger.info(
            "Moving manager engagement and terminate old manager(s)",
            new_ou_for_eng=org_unit_uuid_of_new_manager,
        )

        # Finding potential existing managers.
        existing_managers = await get_existing_managers(
            org_unit_uuid_of_new_manager, gql_client
        )
        # Terminating pre-existing managers.
        await terminate_existing_managers(
            gql_client,
            existing_managers,
            new_manager_uuid,
        )
        logger.info("All existing managers now terminated")
        # Moving engagement to managers new Organisation Unit.
        await elevate_engagement(
            gql_client, org_unit_uuid_of_new_manager, engagement_uuid_to_be_moved
        )
        logger.info("Manager engagement successfully moved")
        return None

    logger.info("Manager engagement not moved")
