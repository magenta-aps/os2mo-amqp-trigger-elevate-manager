# Generated by ariadne-codegen on 2025-02-18 09:26
# Source: queries.graphql
from uuid import UUID

from .base_model import BaseModel


class MoveEngagement(BaseModel):
    engagement_update: "MoveEngagementEngagementUpdate"


class MoveEngagementEngagementUpdate(BaseModel):
    uuid: UUID


MoveEngagement.update_forward_refs()
MoveEngagementEngagementUpdate.update_forward_refs()
