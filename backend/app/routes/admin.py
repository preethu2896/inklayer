from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
import io

from ..models.schemas import (
    AdminLoginRequest,
    TokenResponse,
    SubscriberListResponse,
    SubscriberOut,
    TagUpdateRequest,
    SendDropRequest,
    SendDropResponse,
)
from ..services.db_service import (
    get_all_subscribers,
    update_subscriber_tag,
    export_subscribers_csv,
    get_subscriber_emails,
)
from ..services.auth_service import verify_admin_credentials, create_access_token, get_current_admin
from ..services.email_service import send_drop_email

router = APIRouter()


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post(
    "/admin/login",
    response_model=TokenResponse,
    summary="Admin login — returns a JWT",
    tags=["Admin"],
)
async def admin_login(body: AdminLoginRequest):
    """
    Authenticate as admin and receive a Bearer token.
    Use the token in the Authorization header for all /admin/* endpoints.
    """
    if not verify_admin_credentials(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )
    token = create_access_token(data={"sub": body.username})
    return TokenResponse(access_token=token)


# ── Subscriber Management ─────────────────────────────────────────────────────

@router.get(
    "/emails",
    response_model=SubscriberListResponse,
    summary="Get all subscribers (admin only)",
    tags=["Admin"],
)
async def get_emails(
    tag: str = None,
    admin: str = Depends(get_current_admin),
):
    """
    Returns all subscribers, optionally filtered by tag.
    Query param: ?tag=vip | ?tag=early_access | ?tag=general
    """
    rows = await get_all_subscribers(tag=tag)
    subscribers = [SubscriberOut(**row) for row in rows]
    return SubscriberListResponse(count=len(subscribers), subscribers=subscribers)


@router.patch(
    "/admin/tag",
    summary="Update a subscriber's tag (admin only)",
    tags=["Admin"],
)
async def update_tag(
    body: TagUpdateRequest,
    admin: str = Depends(get_current_admin),
):
    """
    Update the tag (vip / early_access / general) for a subscriber's email.
    """
    updated = await update_subscriber_tag(body.email, body.tag)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscriber '{body.email}' not found.",
        )
    return {"success": True, "message": f"Tag updated to '{body.tag}' for {body.email}."}


# ── CSV Export ────────────────────────────────────────────────────────────────

@router.get(
    "/admin/export",
    summary="Export subscribers as CSV (admin only)",
    tags=["Admin"],
)
async def export_csv(
    tag: str = None,
    admin: str = Depends(get_current_admin),
):
    """
    Download all subscribers (or a tagged subset) as a CSV file.
    Query param: ?tag=vip | ?tag=early_access | ?tag=general
    """
    csv_data = await export_subscribers_csv(tag=tag)
    filename = f"inklayer_subscribers{'_' + tag if tag else ''}.csv"
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── Drop Notification ─────────────────────────────────────────────────────────

@router.post(
    "/send-drop",
    response_model=SendDropResponse,
    summary="Send a drop notification to all / tagged subscribers (admin only)",
    tags=["Admin"],
)
async def send_drop(
    body: SendDropRequest,
    background_tasks: BackgroundTasks,
    admin: str = Depends(get_current_admin),
):
    """
    Fire a drop notification email to all subscribers, or only those with a specific tag.
    Set 'tag' in the request body to target a subset (e.g. 'vip', 'early_access').
    Email is dispatched in the background for fast response.
    """
    emails = await get_subscriber_emails(tag=body.tag)
    if not emails:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscribers found for the given filter.",
        )

    background_tasks.add_task(send_drop_email, emails, body.subject, body.body)

    tag_label = f"'{body.tag}' subscribers" if body.tag else "all subscribers"
    return SendDropResponse(
        sent_to=len(emails),
        message=f"Drop dispatch initiated for {len(emails)} {tag_label}.",
    )
