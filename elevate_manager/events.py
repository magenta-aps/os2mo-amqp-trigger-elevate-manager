# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import structlog
from raclients.graph.client import PersistentGraphQLClient  # type: ignore

from .mo import get_existing_managers
from .mo import get_org_unit_levels
from .mo import terminate_existing_managers_and_elevate_engagement
from .ou_levels import get_new_org_unit_for_engagement

logger = structlog.get_logger(__name__)


async def process_manager_event(
    gql_client: PersistentGraphQLClient, manager_uuid: UUID
) -> None:
    logger.debug("Processing manager event", manager_uuid=manager_uuid)

    org_unit_levels = await get_org_unit_levels(gql_client, manager_uuid)
    new_manager_engagement_unit = get_new_org_unit_for_engagement(org_unit_levels)
    if new_manager_engagement_unit is not None:
        logger.info(
            "Moving manager engagement and terminate old manager(s)",
            new_ou_for_eng=new_manager_engagement_unit,
        )
        new_manager_engagement_unit_uuid = UUID(new_manager_engagement_unit.uuid)
        existing_managers = await get_existing_managers(
            new_manager_engagement_unit_uuid, gql_client
        )
        await terminate_existing_managers_and_elevate_engagement(
            gql_client,
            manager_uuid,
            new_manager_engagement_unit_uuid,
            existing_managers,
        )

    logger.info("Manager engagement not elevated")
