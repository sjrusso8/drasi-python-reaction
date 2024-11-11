from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class UpdatedResult(BaseModel):
    before: dict[str, Any]
    after: dict[str, Any]
    model_config = ConfigDict(extra="allow")


class ChangeEvent(BaseModel):
    kind: str = "change"
    added_results: List[dict[str, Any]] = Field(
        default_factory=list, alias="addedResults"
    )
    deleted_results: List[dict[str, Any]] = Field(
        default_factory=list, alias="deletedResults"
    )
    updated_results: List[UpdatedResult] = Field(
        default_factory=list, alias="updatedResults"
    )
    model_config = ConfigDict(extra="allow")


class ControlSignal(BaseModel):
    kind: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class ControlEvent(BaseModel):
    kind: str = "control"
    control_signal: Optional[ControlSignal] = Field(
        default_factory=list, alias="controlSignal"
    )
    model_config = ConfigDict(extra="allow")
