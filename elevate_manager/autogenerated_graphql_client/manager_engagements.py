# Generated by ariadne-codegen on 2025-02-05 16:31
# Source: queries.graphql
from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ManagerEngagements(BaseModel):
    managers: "ManagerEngagementsManagers"


class ManagerEngagementsManagers(BaseModel):
    objects: list["ManagerEngagementsManagersObjects"]


class ManagerEngagementsManagersObjects(BaseModel):
    current: Optional["ManagerEngagementsManagersObjectsCurrent"]


class ManagerEngagementsManagersObjectsCurrent(BaseModel):
    employee: list["ManagerEngagementsManagersObjectsCurrentEmployee"] | None
    org_unit_uuid: UUID


class ManagerEngagementsManagersObjectsCurrentEmployee(BaseModel):
    engagements: list["ManagerEngagementsManagersObjectsCurrentEmployeeEngagements"]


class ManagerEngagementsManagersObjectsCurrentEmployeeEngagements(BaseModel):
    uuid: UUID


ManagerEngagements.update_forward_refs()
ManagerEngagementsManagers.update_forward_refs()
ManagerEngagementsManagersObjects.update_forward_refs()
ManagerEngagementsManagersObjectsCurrent.update_forward_refs()
ManagerEngagementsManagersObjectsCurrentEmployee.update_forward_refs()
ManagerEngagementsManagersObjectsCurrentEmployeeEngagements.update_forward_refs()
