import asyncio
import logging

logger = logging.getLogger("uvicorn.error")

async def send_confirmation_email(email: str):
    """
    Sends a confirmation email to the user.
    In a real production environment, you would integrate Resend, SendGrid, or native SMTP here.
    """
    # Simulate network delay for sending email
    await asyncio.sleep(0.5)
    
    # Simple console output to verify behavior and represent the premium tone
    logger.info(f"\n--- EMAIL SENT ---")
    logger.info(f"To: {email}")
    logger.info(f"Subject: You're in – Inklayer Drop Access")
    logger.info(f"Body: Welcome to the inner circle. We'll let you know when the next drop is live.")
    logger.info(f"------------------\n")
    return True
