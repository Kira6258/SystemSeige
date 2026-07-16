from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Default base for all request schemas — blocks mass assignment by rejecting unknown fields."""

    model_config = ConfigDict(extra="forbid")
