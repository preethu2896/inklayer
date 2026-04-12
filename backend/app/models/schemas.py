from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
import bleach


class SubscribeRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def sanitize_email(cls, v: str) -> str:
        """Strip whitespace and sanitize to prevent injection."""
        if not isinstance(v, str):
            raise ValueError("Email must be a string.")
        return bleach.clean(v.strip().lower())


class SubscribeResponse(BaseModel):
    success: bool
    message: str


class SubscriberOut(BaseModel):
    id: int
    email: str
    tag: str
    created_at: str


class SubscriberListResponse(BaseModel):
    count: int
    subscribers: List[SubscriberOut]


# ── Admin Auth ──────────────────────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username", "password", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Field must be a string.")
        return bleach.clean(v.strip())


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Drop Send ───────────────────────────────────────────────────────────

class SendDropRequest(BaseModel):
    subject: str
    body: str
    tag: Optional[str] = None  # If None → send to ALL subscribers

    @field_validator("subject", "body", mode="before")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Field must be a string.")
        return bleach.clean(v.strip())


class SendDropResponse(BaseModel):
    sent_to: int
    message: str


# ── Tag Update ──────────────────────────────────────────────────────────

class TagUpdateRequest(BaseModel):
    email: EmailStr
    tag: str  # e.g. "vip", "early_access", "general"

    @field_validator("tag", mode="before")
    @classmethod
    def validate_tag(cls, v: str) -> str:
        allowed = {"vip", "early_access", "general"}
        v = v.strip().lower()
        if v not in allowed:
            raise ValueError(f"Tag must be one of: {', '.join(allowed)}")
        return v
