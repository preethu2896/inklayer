from fastapi import APIRouter, Request, BackgroundTasks
from ..models.schemas import SubscribeRequest, SubscribeResponse
from ..services.db_service import add_subscriber
from ..services.email_service import send_confirmation_email
from ..services.rate_limiter import limiter

router = APIRouter()


@router.post(
    "/subscribe",
    response_model=SubscribeResponse,
    summary="Join the Drop waitlist",
    tags=["Public"],
)
@limiter.limit("3/minute")
async def subscribe_email(
    request: Request,
    body: SubscribeRequest,
    background_tasks: BackgroundTasks,
):
    """
    Submit an email to join the Inklayer drop waitlist.
    - Validates email format via Pydantic EmailStr (email-validator library)
    - Prevents duplicates at the database level
    - Sends confirmation email asynchronously (non-blocking)
    - Rate limited to 3 requests per minute per IP
    """
    email = body.email  # Already sanitized + lowercased by the Pydantic validator

    success = await add_subscriber(email)

    if not success:
        # Duplicate — not an error, just a soft response
        return SubscribeResponse(
            success=False, message="You're already on the list")

    # Non-blocking: fire the email and return immediately
    background_tasks.add_task(send_confirmation_email, email)

    return SubscribeResponse(
        success=True, message="You're in. Welcome to Inklayer.")
