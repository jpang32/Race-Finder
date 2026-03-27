from pydantic import BaseModel
from typing import List, Optional

from enum import Enum
from pydantic import BaseModel, ValidationError

class RaceType(str, Enum):
    FIVE_K = "5k"
    TEN_K = "10k"
    HALF_MARATHON = "half-marathon"
    MARATHON = "marathon"
    DUATHLON = "duathlon"


class RaceQuery(BaseModel):
    # This Pydantic model is used as a way of validating the input that comes
    # from the LLM model call, and ultimately, from the user

    # Field restrictions such as radius_miles or race_types are meant to
    # restrict the amount of searching the LLM does to satisfy user requests
    city: str
    # TODO: Expand to other countries
    country: str = "USA"
    # Generalized term for when expanding to countries that don't have states
    jurisdiction: str
    date_start: str  # "YYYY-MM-DD"
    date_end: str # "YYYY-MM-DD"
    race_types: List[RaceType]  # ["5k", "10k", "half-marathon", "duathlon"]
    skill_level: Optional[str]  # "beginner" | "intermediate" | "advanced"
    transportation: Optional[str]
    radius_miles: Optional[int]
