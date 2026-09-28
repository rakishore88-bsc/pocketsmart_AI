from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, field_validator

PlannerType = Literal["home", "party", "jewelry"]


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=160)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class LoginRequest(BaseModel):
    email: str
    password: str


class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=5)
    rooms: list[str] = Field(min_length=1)
    style: str = Field(default="modern", max_length=100)
    notes: str = Field(default="", max_length=1000)
    quantities: dict[str, int] = Field(default_factory=dict)


class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=5)
    guests: int = Field(gt=0, le=10_000)
    event_type: str = Field(min_length=2, max_length=100)
    venue_area: str = Field(default="", max_length=150)
    food_preference: str = Field(default="mixed", max_length=100)
    notes: str = Field(default="", max_length=1000)


class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=5)
    occasion: str = Field(min_length=2, max_length=100)
    style: str = Field(default="elegant", max_length=100)
    metal: str = Field(default="any", max_length=100)
    outfit_description: str = Field(default="", max_length=1000)
    notes: str = Field(default="", max_length=1000)


class RecommendationItem(BaseModel):
    name: str
    category: str
    estimated_price: float = Field(ge=0)
    currency: str = "INR"
    platform: str
    url: str
    reason: str
    priority: Literal["high", "medium", "low"] = "medium"


class BudgetAllocation(BaseModel):
    category: str
    amount: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    rationale: str


class RecommendationResponse(BaseModel):
    planner: PlannerType
    title: str
    summary: str
    budget: float
    currency: str
    budget_allocations: list[BudgetAllocation] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    disclaimer: str = "Prices and availability are estimates and should be verified on the destination platform."
