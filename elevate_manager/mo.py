# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# Module containing GraphQL functions to interact with MO
import datetime
from uuid import UUID

import structlog
from gql import gql  # type: ignore
from pydantic import AnyHttpUrl
from pydantic import parse_obj_as
from raclients.graph.client import PersistentGraphQLClient  # type: ignore

from .models.get_existing_managers import GetExistingManagers
from .models.get_org_unit_levels import GetOrgUnitLevels

logger = structlog.get_logger()


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
    # logger.debug("Set up GraphQL client")

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


async def get_org_unit_levels(
    gql_client: PersistentGraphQLClient, manager_uuid: UUID
) -> GetOrgUnitLevels:
    """
    Call MO and return OU-levels in a (Quicktype generated) model instance
    for
    1) The OU where the manager update occurred
    2) All the OUs where the manager has engagements

    Args:
        gql_client: The GraphQL client
        manager_uuid: The UUID of the manager

    Returns:
        OU levels according to the description above
    """

    # TODO: raise a custom exception in case of errors contacting MO

    query = gql(
        """
        query GetOrgUnitLevels($manager_uuid: [UUID!]) {
          managers(uuids: $manager_uuid) {
            objects {
              employee {
                engagements {
                  uuid
                  user_key
                  org_unit {
                    name
                    uuid
                    parent_uuid
                    org_unit_level {
                      name
                      uuid
                    }
                  }
                }
              }
              org_unit {
                name
                uuid
                org_unit_level {
                  name
                  uuid
                }
              }
            }
          }
        }
        """
    )

    r = await gql_client.execute(
        query, variable_values={"manager_uuid": str(manager_uuid)}
    )

    return parse_obj_as(GetOrgUnitLevels, {"data": r})


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

    graphql_query = gql(
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
    variables = {"uuids": str(org_unit_uuid)}

    response = await gql_client.execute(graphql_query, variable_values=variables)

    return parse_obj_as(GetExistingManagers, {"data": response})


# TODO: add argument providing existing manager(s) (can be None)
async def terminate_existing_managers_and_elevate_engagement(
    gql_client: PersistentGraphQLClient,
    org_unit: UUID,
    manager_uuid: UUID,
    # existing_managers: GetExistingManagers,
) -> None:
    """
    This function will:
    1) Terminate any existing managers if provided
    2) Potentially elevate an existing manager engagement

    The two operations above will be done IN ONE GRAPHQL QUERY in
    order to be "atomic" (NOTE: this is actually not possible with
    the GraphQL API for now, but it is likely to be implemented later).
    If the queries were split into two separate queries we might
    risk ending up in an inconsistent state e.g. if the application
    crashes between the two queries.

    Args:
        gql_client: The GraphQL client
        org_unit: The UUID of the OU where the manager update occurred
        manager_uuid: UUID of the new manager
        existing_managers: The managers already existing in the OU

    (maybe create a helper function to build the mutation queries)

    GraphQL query (for elevating engagement) for inspiration:

    mutation MoveEngagement {
        engagement_update(
            input: {
                uuid: "8a37aeae-47af-4a4c-9ea7-37d40c1dcf6c",
                validity: {from: "2023-02-09"},
                org_unit: "fb2d158f-114e-5f67-8365-2c520cf10b58"
            }
        ) {
            uuid
        }
    }
    """
    # TODO: Helper function might be redundant. Remove it or adjust gql calls accordingly.
    # def extract_manager_uuids() -> str:
    #     managers = one(one(existing_managers.data.org_units).objects).managers
    #     for manager in managers:
    #         return str(manager.uuid)

    graphql_terminate_query = gql(
        """
        mutation ($input: ManagerTerminateInput!) {
          manager_terminate(input: $input) {
            uuid
          }
        }
        """
    )
    terminate_variables = {
        "input": {
            "uuid": str(manager_uuid),
            "to": datetime.date.today().isoformat(),
        }
    }

    graphql_update_manager_of_org_unit = gql(
        """
        mutation MyMutation($input: ManagerUpdateInput!) {
          manager_update(input: $input) {
            uuid
          }
        }
        """
    )
    update_variables = {
        "input": {
            "uuid": str(manager_uuid),
            "validity": {"from": datetime.date.today().isoformat()},
            "org_unit": str(org_unit),
        }
    }

    terminated_managers = await gql_client.execute(
        graphql_terminate_query, variable_values=terminate_variables
    )
    print(terminated_managers)

    updated_managers = await gql_client.execute(
        graphql_update_manager_of_org_unit, variable_values=update_variables
    )
    print(updated_managers)
