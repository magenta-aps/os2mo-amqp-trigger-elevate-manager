# Module containing GraphQL functions to interact with MO
from uuid import UUID

import structlog
from gql import gql  # type: ignore
from pydantic import parse_obj_as
from raclients.graph.client import PersistentGraphQLClient  # type: ignore

from elevate_manager.config import Settings
from elevate_manager.models.get_existing_managers import GetExistingManagers

logger = structlog.get_logger()


def get_client(settings: Settings) -> PersistentGraphQLClient:
    """
    Configure and return GraphQL client
    """
    gql_client = PersistentGraphQLClient(
        url=f"{settings.mo_url}/graphql/v3",
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        auth_realm=settings.auth_realm,
        auth_server=settings.auth_server,
        sync=True,
        httpx_client_kwargs={"timeout": None},
    )
    logger.debug("Set up GraphQL client")
    return gql_client


# TODO: add return type which is yet unknown (comes from Quicktype)
def get_org_unit_levels(gql_client: PersistentGraphQLClient):
    """
    Call MO and return OU-levels in a (Quicktype generated) model instance
    for
    1) The OU where the manager update occurred
    2) All the OUs where the manager has engagements

    Raise a custom exception in case of errors contacting MO

    Note: the responsibility for this function is NOT to perform all
    the logic that extracts the OU-levels, but ONLY to
    1) Call MO
    2) Build and return a (Quicktype generated) model instance
    3) Raise custom exception(s) in case of errors

    A GraphQL query like this can be used to call MO:
    (maybe create a helper function to put in the search args...)

    query Engagements {
      managers(uuids: "7c27c18f-9f5f-43c4-bfe0-b87421db4a59") {
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
    pass


# TODO: add return type (Quicktype obj) for the appropriate GQL query
async def get_existing_managers(
    org_unit_uuid: UUID,
    gql_client: PersistentGraphQLClient,
) -> GetExistingManagers:
    """
    Get existing managers of the given OU.

    Will return a response parsed in types using Quicktype, rather than nested
    objects and arrays.

    :arg:
    Uuid(s) of the Organisation unit(s) wanted to find managers of.
    Gql client to perform the query.

    :returns:
    Uuid(s) of manager(s)
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
    variables = {"uuids": org_unit_uuid}

    response = await gql_client.execute(graphql_query, variable_values=variables)

    return parse_obj_as(GetExistingManagers, response)


# TODO: add argument providing existing manager(s) (can be None)
def update_manager_and_elevate_engagement(
    org_unit: UUID, elevate_engagement: bool
) -> None:
    """
    This function will:
    1) Terminate any existing managers if provided
    2) Potentially elevate an existing manager engagement

    The two operations above will be done IN ONE GRAPHQL QUERY in
    order to be "atomic". If the queries were split into two
    separate queries we might risk ending up in an inconsistent
    state e.g. if the application crashes between the two queries.

    Args:
        org_unit: The UUID of the OU where the manager update occurred
        elevate_engagement: if true, move the existing engagement

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
    pass
