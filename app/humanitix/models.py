from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class FlexibleBaseModel(BaseModel):
    """
    Flex data model class
    """

    model_config = ConfigDict(extra="allow")


class EventClassification(FlexibleBaseModel):

    type: str
    category: str
    subcategory: str


class AdditionalQuestion(FlexibleBaseModel):

    id: str = Field(..., alias="_id")
    question: str


class Event(FlexibleBaseModel):

    id: str = Field(..., alias="_id")
    location: str
    currency: str
    name: str
    description: str
    slug: str
    userId: str
    organiserId: str
    tagIds: List[str]
    classification: EventClassification
    public: bool
    published: bool
    suspendSales: bool
    markedAsSoldOut: bool
    startDate: datetime
    endDate: datetime
    timezone: str
    totalCapacity: int
    additionalQuestions: List[AdditionalQuestion]
    # Many more fields defined at runtime

    # DadLAN-specific values
    isRemote: bool = False
    ordersCount: int = 0
    contributions: float = 0.0
    sparesNeeded: int = 0


class Events(FlexibleBaseModel):

    total: int
    pageSize: int
    page: int
    events: List[Event]

class TicketAdditionalDetails(FlexibleBaseModel):

    questionId: str
    value: str | None = None

class Ticket(FlexibleBaseModel):

    id: str = Field(..., alias="_id")
    orderId: str
    eventId: str
    price: float
    additionalFields: List[TicketAdditionalDetails]


class Tickets(FlexibleBaseModel):

    total: int
    pageSize: int
    page: int
    tickets: List[Ticket]
