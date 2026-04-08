from fastapi import APIRouter, Request, BackgroundTasks
from ..models.schemas import SubscribeRequest, SubscribeResponse
from ..services.db_service import add_subscriber, get_all_subscribers
from ..services.email_service import send_confirmation_email
from ..services.rate_limiter import limiter

router = APIRouter()

@router.post("/subscribe", response_model=SubscribeResponse)
@limiter.limit("3/minute")
async def subscribe_email(request: Request, body: SubscribeRequest, background_tasks: BackgroundTasks):
    email = body.email.lower().strip()
    
    # Insert safely to the persistent lightweight DB
    success = await add_subscriber(email)
    
    if not success:
        # Prevent duplicate entries response
        return SubscribeResponse(message="You're already on the list.")
    
    # Dispatch email sending to background to ensure fast response times
    background_tasks.add_task(send_confirmation_email, email)
    
    # Clean premium success message
    return SubscribeResponse(message="You're in. Welcome to Inklayer.")

@router.get("/emails")
async def get_emails(request: Request):
    """
    Retrieves all subscribers.
    NOTE: In production, add a dependency strictly verifying admin credentials here.
    """
    subs = await get_all_subscribers()
    return {"count": len(subs), "subscribers": subs}
