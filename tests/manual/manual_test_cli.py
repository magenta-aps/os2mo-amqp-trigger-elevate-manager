# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio

import click

from elevate_manager.mo import get_client
from elevate_manager.mo import get_existing_managers
from elevate_manager.mo import get_org_unit_levels


@click.group()
@click.option(
    "--mo_base_url",
    "mo_base_url",
    type=click.STRING,
    default="http://localhost:5000",
    help="MO base url",
)
@click.option(
    "--client-id",
    "client_id",
    type=click.STRING,
    default="dipex",
    help="Keycloak client id",
)
@click.option(
    "--client-secret",
    "client_secret",
    type=click.STRING,
    required=True,
    help="Keycloak client secret",
)
@click.option(
    "--auth-server",
    "auth_server",
    type=click.STRING,
    default="http://localhost:5000/auth",
    help="Base URL for Keycloak",
)
@click.option(
    "--timeout",
    "timeout",
    type=click.INT,
    default=120,
    help="HTTPX timeout for GraphQL client",
)
@click.pass_context
def cli(ctx, mo_base_url, client_id, client_secret, auth_server, timeout):
    ctx.ensure_object(dict)

    ctx.obj["mo_base_url"] = mo_base_url
    ctx.obj["client_id"] = client_id
    ctx.obj["client_secret"] = client_secret
    ctx.obj["auth_server"] = auth_server
    ctx.obj["timeout"] = timeout


@cli.command()
@click.option(
    "--manager-uuid",
    "manager_uuid",
    type=click.UUID,
    required=True,
    help="MO manager UUID",
)
@click.pass_context
def get_org_unit_levels_facade(ctx, manager_uuid):
    gql_client = get_client(
        mo_url=ctx.obj["mo_base_url"],
        client_id=ctx.obj["client_id"],
        client_secret=ctx.obj["client_secret"],
        auth_realm="mo",
        auth_server=ctx.obj["auth_server"],
    )

    async def run_task():
        org_unit_levels = await get_org_unit_levels(gql_client, manager_uuid)
        click.echo(org_unit_levels)

    asyncio.run(run_task())


@cli.command()
@click.option(
    "--org-unit-uuid",
    "org_unit_uuid",
    type=click.UUID,
    required=True,
    help="Org unit uuids",
)
@click.pass_context
def get_org_managers(ctx, org_unit_uuid):
    gql_client = get_client(
        mo_url=ctx.obj["mo_base_url"],
        client_id=ctx.obj["client_id"],
        client_secret=ctx.obj["client_secret"],
        auth_realm="mo",
        auth_server=ctx.obj["auth_server"],
    )

    async def run_task():
        org_unit_levels = await get_existing_managers(org_unit_uuid, gql_client)
        click.echo(org_unit_levels)

    asyncio.run(run_task())


if __name__ == "__main__":
    cli(obj={})
