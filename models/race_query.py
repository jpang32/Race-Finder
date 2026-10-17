from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class RaceType(Enum):
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
	location: Union[USA, Canada, Italy] = Field(discriminator="country_code")
	date_start: str  # "YYYY-MM-DD"
	date_end: str  # "YYYY-MM-DD"
	race_types: List[RaceType]
	# Not yet supported:
	skill_level: Optional[str]  # "beginner" | "intermediate" | "advanced"
	transportation: Optional[str]
	radius_miles: Optional[int]


class Race(BaseModel):
	name: str
	date: str
	location: Union[USA, Canada, Italy]
	race_types: List[RaceType]
