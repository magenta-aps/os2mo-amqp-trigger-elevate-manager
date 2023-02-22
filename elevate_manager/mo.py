# Module containing GraphQL functions to interact with MO
from uuid import UUID

import structlog
from raclients.graph.client import PersistentGraphQLClient  # type: ignore

from .config import Settings

logger = structlog.get_logger()


async def get_client(settings: Settings) -> PersistentGraphQLClient:
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
    return gql_client
    logger.debug("Set up GraphQL client")
    pass


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
                }
                org_unit_level_uuid
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
def get_existing_managers(org_unit_uuid: UUID, gql_client: PersistentGraphQLClient):
    """
    Get existing managers of the given OU

    This query can be used:

    query MyQuery {
        org_units(uuids: "f06ee470-9f17-566f-acbe-e938112d46d9") {
            objects {
                managers {
                    uuid
                    user_key
                }
            }
        }
    }

    Return appropriate Quicktype object or None if there are
    not any existing managers.
    """
    pass


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
