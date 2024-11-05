from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel


class ChatMessage(BaseModel):

    id: int
    name: str
    display_name: str
    message: str
    created_at: datetime


class OpenAIResponse(BaseModel):

    response: str
    total_tokens: int
    completion_tokens: int
    prompt_tokens: int


class TokenUserHistory(BaseModel):

    id: int
    name: str
    display_name: str
    tokens: int
    cost: float
    created_at: datetime


class TokenChannelHistory(BaseModel):

    id: int
    name: str
    tokens: int
    cost: float
    created_at: datetime


class TokenHistory(BaseModel):

    total_tokens: int = 0
    total_cost: float = 0.0

    user_history: List[TokenUserHistory] = []
    channel_history: List[TokenChannelHistory] = []


class ChannelCacheResponse(BaseModel):

    key: str
    response: str
    expires_at: datetime

class GenerationSnapshotSchema(BaseModel):
    """
    Schema for the generation snapshot called by end users
    """

    timestamp_at: datetime
    channel: str
    channel_id: int
    name: str
    display_name: str
    user_id: int
    prompt: str
    response: str
    estimated_tokens: int
    actual_tokens: int
    estimated_cost: Decimal
