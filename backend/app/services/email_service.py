import os
import logging
from typing import List, Optional

logger = logging.getLogger("uvicorn.error")

# ── Resend SDK (installed via pip install resend) ─────────────────────────────
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    logger.warning("Resend SDK not installed. Emails will be logged only.")

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM     = os.getenv("EMAIL_FROM", "drops@inklayer.shop")


def _get_confirmation_html(email: str) -> str:
    """Returns the premium HTML body for the confirmation email."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>You're in – Inklayer Drop Access</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    body {{
      margin: 0; padding: 0;
      background-color: #0a0a0a;
      font-family: 'Inter', sans-serif;
      color: #e5e5e5;
    }}
    .wrapper {{
      max-width: 560px;
      margin: 48px auto;
      background: #111111;
      border: 1px solid #1f1f1f;
      border-radius: 4px;
      overflow: hidden;
    }}
    .header {{
      padding: 40px 48px 24px;
      border-bottom: 1px solid #1f1f1f;
    }}
    .brand {{
      font-size: 13px;
      letter-spacing: 0.25em;
      text-transform: uppercase;
      color: #888;
      margin-bottom: 8px;
    }}
    .headline {{
      font-size: 28px;
      font-weight: 600;
      color: #ffffff;
      line-height: 1.2;
      margin: 0;
    }}
    .body {{
      padding: 32px 48px;
    }}
    .body p {{
      font-size: 15px;
      line-height: 1.7;
      color: #aaaaaa;
      margin: 0 0 20px;
    }}
    .divider {{
      width: 40px;
      height: 1px;
      background: #333;
      margin: 28px 0;
    }}
    .footer {{
      padding: 20px 48px 32px;
      border-top: 1px solid #1a1a1a;
      font-size: 12px;
      color: #444;
      letter-spacing: 0.05em;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <p class="brand">Inklayer</p>
      <h1 class="headline">You're in the circle.</h1>
    </div>
    <div class="body">
      <p>
        You've secured early access to every Inklayer drop. No noise — just the signal,
        when it matters.
      </p>
      <p>
        When the next collection goes live, you'll be the first to know.
        Keep an eye on this inbox.
      </p>
      <div class="divider"></div>
      <p style="font-size:13px; color:#555;">
        This confirmation was sent to <strong style="color:#888;">{email}</strong>.<br>
        If you didn't sign up, you can safely ignore this message.
      </p>
    </div>
    <div class="footer">
      © Inklayer · Premium Streetwear · Drops by invite only.
    </div>
  </div>
</body>
</html>
"""


def _get_drop_html(subject: str, body: str) -> str:
    """Returns the premium HTML body for a drop announcement email."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{subject}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    body {{
      margin: 0; padding: 0;
      background-color: #0a0a0a;
      font-family: 'Inter', sans-serif;
      color: #e5e5e5;
    }}
    .wrapper {{
      max-width: 560px;
      margin: 48px auto;
      background: #111111;
      border: 1px solid #1f1f1f;
      border-radius: 4px;
      overflow: hidden;
    }}
    .header {{
      padding: 40px 48px 24px;
      border-bottom: 1px solid #1f1f1f;
    }}
    .brand {{
      font-size: 13px;
      letter-spacing: 0.25em;
      text-transform: uppercase;
      color: #888;
      margin-bottom: 8px;
    }}
    .headline {{
      font-size: 28px;
      font-weight: 600;
      color: #ffffff;
      line-height: 1.2;
      margin: 0;
    }}
    .body {{
      padding: 32px 48px;
      font-size: 15px;
      line-height: 1.7;
      color: #aaaaaa;
    }}
    .footer {{
      padding: 20px 48px 32px;
      border-top: 1px solid #1a1a1a;
      font-size: 12px;
      color: #444;
      letter-spacing: 0.05em;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <p class="brand">Inklayer · Drop Alert</p>
      <h1 class="headline">{subject}</h1>
    </div>
    <div class="body">
      {body.replace(chr(10), '<br>')}
    </div>
    <div class="footer">
      © Inklayer · Premium Streetwear · You're receiving this because you joined the drop.
    </div>
  </div>
</body>
</html>
"""


async def send_confirmation_email(email: str) -> bool:
    """
    Send a premium confirmation email to a new subscriber via Resend.
    Falls back to console logging if Resend is not configured.
    """
    subject = "You're in – Inklayer Drop Access"
    html_body = _get_confirmation_html(email)

    if RESEND_AVAILABLE and RESEND_API_KEY and not RESEND_API_KEY.startswith("re_your"):
        try:
            resend.api_key = RESEND_API_KEY
            resend.Emails.send({
                "from":    EMAIL_FROM,
                "to":      [email],
                "subject": subject,
                "html":    html_body,
            })
            logger.info(f"[EMAIL] Confirmation sent → {email}")
            return True
        except Exception as e:
            logger.error(f"[EMAIL] Resend error for {email}: {e}")
            return False
    else:
        # Development fallback — log to console
        logger.info(f"\n{'─'*48}")
        logger.info(f"  [DEV EMAIL] To:      {email}")
        logger.info(f"  [DEV EMAIL] Subject: {subject}")
        logger.info(f"  [DEV EMAIL] Body:    Premium HTML confirmation (see email_service.py)")
        logger.info(f"{'─'*48}\n")
        return True


async def send_drop_email(emails: List[str], subject: str, body: str) -> int:
    """
    Send a bulk drop notification to a list of emails.
    Uses Resend batch API if available, otherwise logs each one.
    Returns the count of emails successfully dispatched.
    """
    html_body = _get_drop_html(subject, body)
    sent = 0

    if RESEND_AVAILABLE and RESEND_API_KEY and not RESEND_API_KEY.startswith("re_your"):
        resend.api_key = RESEND_API_KEY
        for email in emails:
            try:
                resend.Emails.send({
                    "from":    EMAIL_FROM,
                    "to":      [email],
                    "subject": subject,
                    "html":    html_body,
                })
                sent += 1
                logger.info(f"[DROP] Sent → {email}")
            except Exception as e:
                logger.error(f"[DROP] Failed → {email}: {e}")
    else:
        logger.info(f"\n{'─'*48}")
        logger.info(f"  [DEV DROP] Subject: {subject}")
        logger.info(f"  [DEV DROP] Would send to {len(emails)} subscriber(s):")
        for email in emails:
            logger.info(f"    · {email}")
            sent += 1
        logger.info(f"{'─'*48}\n")

    return sent
