import json
import re
import frappe
from auth_api.module.subscription.constant import (
    READ_ONLY_EXEMPT_METHODS,
    SUBSCRIPTION_EXPIRED_MESSAGE,
    SUBSCRIPTION_EXPIRED_TITLE,
)
from auth_api.module.subscription.service import is_subscription_expired

_METHOD_PATH = re.compile(r"^/api/(?:v[12]/)?method/(.+)$")

def enforce_read_only_if_expired():
    """before_request: once the subscription has expired the request runs in Frappe's read-only mode.
    Every read works (GET or POST); any database write fails (see expired_write_response)."""
    request = getattr(frappe.local, "request", None)
    if not request or request.method == "OPTIONS":
        return
    if _called_method(request) in READ_ONLY_EXEMPT_METHODS:
        return
    if not is_subscription_expired():
        return

    frappe.flags.read_only = True
    frappe.flags.subscription_expired = True
    frappe.db.begin(read_only=True)  # also kept after any commit, frappe.db.begin() reads the flag

def expired_write_response(response, request):
    """after_request: a write refused because of the expired subscription gets our message, not
    Frappe's "read only mode for maintenance" one."""
    if not frappe.flags.get("subscription_expired") or response.status_code != 503:
        return
    try:
        body = json.loads(response.get_data(as_text=True) or "{}")
    except ValueError:
        return
    if body.get("exc_type") != "InReadOnlyMode":
        return

    message = {"message": SUBSCRIPTION_EXPIRED_MESSAGE, "title": SUBSCRIPTION_EXPIRED_TITLE, "indicator": "red"}
    response.set_data(json.dumps({
        "exc_type": "PermissionError",
        "message": SUBSCRIPTION_EXPIRED_MESSAGE,
        "_server_messages": json.dumps([json.dumps(message)]),
    }))
    response.status_code = 403

def _called_method(request) -> str | None:
    """Whitelisted method being called: /api/method/<m>, /api/v1/method/<m>, /api/v2/method/<m> or `cmd`."""
    match = _METHOD_PATH.match(request.path or "")
    if match:
        return match.group(1).strip("/")
    return frappe.form_dict.get("cmd")
