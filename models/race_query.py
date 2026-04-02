from typing import List, Optional, Literal, Union

from enum import Enum
from pydantic import BaseModel, Field

class RaceType(Enum):
    FIVE_K = "5k"
    TEN_K = "10k"
    HALF_MARATHON = "half-marathon"
    MARATHON = "marathon"
    DUATHLON = "duathlon"

class USA(BaseModel):
    country_code: Literal["USA"] = "USA"
    state: str
    county: str
    town: str

class Canada(BaseModel):
    country_code: Literal["CAN"] = "CAN"
    # "province" can also be set to the name of a territory
    province: str
    city: str

class Italy(BaseModel):
    country_code: Literal["ITA"] = "ITA"
    region: str
    city: str

class RaceQuery(BaseModel):
    # This Pydantic model is used as a way of validating the input that comes
    # from the LLM model call, and ultimately, from the user

    # Field restrictions such as radius_miles or race_types are meant to
    # restrict the amount of searching the LLM does to satisfy user requests
    location: Union[USA, Canada, Italy] = Field(discriminator="country_code")
    date_start: str  # "YYYY-MM-DD"
    date_end: str # "YYYY-MM-DD"
    race_types: List[RaceType]  # ["5k", "10k", "half-marathon", "duathlon"]
    skill_level: Optional[str]  # "beginner" | "intermediate" | "advanced"
    transportation: Optional[str]
    radius_miles: Optional[int]
