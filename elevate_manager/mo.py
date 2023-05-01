# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# Module containing GraphQL functions to interact with MO
import datetime
from uuid import UUID

import structlog
from gql import gql  # type: ignore
from more_itertools import one
from pydantic import AnyHttpUrl
from pydantic import parse_obj_as
from raclients.graph.client import PersistentGraphQLClient  # type: ignore

from .models.get_existing_managers import GetExistingManagers
from .models.get_manager_engagements_uuids import GetManagerEngagementUuids

logger = structlog.get_logger()

QUERY_FOR_GETTING_MANAGER_ENGAGEMENTS = gql(
    """
     query GetManagerEngagement($manager_uuid: [UUID!]) {
      managers(uuids: $manager_uuid) {
        objects {
          employee {
            engagements {
              uuid
            }
          }
        }
      }
    }
    """
)

QUERY_FOR_GETTING_EXISTING_MANAGERS = gql(
    """
    query ManagerEngagements ($uuids: [UUID!]) {
      org_units(uuids: $uuids) {
        objects {
          name
          uuid
          managers {
            uuid
          }
        }
      }
    }
    """
)

MUTATION_FOR_TERMINATING_MANAGER = gql(
    """
    mutation ($input: ManagerTerminateInput!) {
      manager_terminate(input: $input) {
        uuid
      }
    }
    """
)

MUTATION_FOR_UPDATING_ENGAGEMENT = gql(
    """
    mutation MoveEngagement($input: EngagementUpdateInput!) {
      engagement_update(input: $input) {
        uuid
      }
    }
    """
)


# Only used for manual testing since we are now using the GraphQL client
# which is shipped with FastRAMQPI. This also enables us to use the
# Kubernetes health check probes build into FastRAMQPI
def get_client(
    mo_url: str,
    client_id: str,
    client_secret: str,
    auth_realm: str,
    auth_server: str,
    sync: bool = False,
    timeout: int = 120,
) -> PersistentGraphQLClient:
    """
    Configure and return GraphQL client
    """
    logger.debug("Set up GraphQL client")

    gql_client = PersistentGraphQLClient(
        url=f"{mo_url}/graphql/v3",
        client_id=client_id,
        client_secret=client_secret,
        auth_realm=auth_realm,
        auth_server=parse_obj_as(AnyHttpUrl, auth_server),
        sync=sync,
        httpx_client_kwargs={"timeout": timeout},
    )
    return gql_client


async def get_manager_engagements(
    gql_client: PersistentGraphQLClient, manager_uuid: UUID
) -> GetManagerEngagementUuids:
    """
    Get the engagement(s) and Organisation Units uuid(s) for the manager.

    Args:
        manager_uuid: UUID of the manager to find potential engagements of
        gql_client: The GraphQL client to perform the query.

    Returns:
        Manager objects consisting of engagements and org units uuids
    """

    response = await gql_client.execute(
        QUERY_FOR_GETTING_MANAGER_ENGAGEMENTS,
        variable_values={"manager_uuid": str(manager_uuid)},
    )

    return parse_obj_as(GetManagerEngagementUuids, {"data": response})


async def get_existing_managers(
    org_unit_uuid: UUID,
    gql_client: PersistentGraphQLClient,
) -> GetExistingManagers:
    """
    Get existing managers of the given OU.

    Args:
        org_unit_uuid: UUID of the organisation unit to find managers of
        gql_client: The GraphQL client to perform the query.

    Returns:
        UUIDs of the org unit managers
    """
    response = await gql_client.execute(
        QUERY_FOR_GETTING_EXISTING_MANAGERS,
        variable_values={"uuids": str(org_unit_uuid)},
    )

    return parse_obj_as(GetExistingManagers, {"data": response})


async def terminate_existing_managers(
    gql_client: PersistentGraphQLClient,
    existing_managers: GetExistingManagers,
    manager_uuid: UUID,
) -> None:
    """
    This function will:
    Terminate any existing managers.

    Args:
        gql_client: The GraphQL client
        existing_managers: The managers already existing in the OU.
        manager_uuid: UUID of the new manager to be elevated.
    """
    # Get previous manager(s) UUID(s)
    previous_managers = one(one(existing_managers.data.org_units).objects).managers  # type: ignore
    previous_managers_uuids = [
        m.uuid for m in previous_managers if m.uuid != str(manager_uuid)
    ]

    # Terminate all previous managers
    for uuid in previous_managers_uuids:
        terminate_variables = {
            "input": {
                "uuid": str(uuid),  # UUID of the previous manager to be terminated.
                "to": datetime.date.today().isoformat(),  # Valid until today.
            }
        }

        await gql_client.execute(
            MUTATION_FOR_TERMINATING_MANAGER, variable_values=terminate_variables
        )


async def move_engagement(
    gql_client: PersistentGraphQLClient,
    org_unit_uuid: UUID,
    engagement_uuid: UUID,
):
    """
    The purpose of this function is to move an engagement to whichever
    organisation unit a person has been made a manager of.

    Args:
        gql_client: The GraphQL client
        org_unit_uuid: UUID of the organisation unit to transfer the manager to
        engagement_uuid: UUID of the engagement to be transfered.
    """

    update_engagement_variables = {
        "input": {
            "uuid": str(engagement_uuid),  # UUID of the engagement to be updated.
            "validity": {"from": datetime.date.today().isoformat()},  # From today.
            "org_unit": str(
                org_unit_uuid
            ),  # UUID of the OU wanting to transfer the engagement to.
        }
    }

    await gql_client.execute(
        MUTATION_FOR_UPDATING_ENGAGEMENT, variable_values=update_engagement_variables
    )
