import json
import frappe
from auth_api.module.subscription.constant import DOCTYPE, SUBSCRIPTION_STATUSES


def validate_subscription_name(name: str):
    if not name or not str(name).strip():
        raise ValueError("masterSubscriptionName is required.")


def validate_subscription_status(status: str):
    if status and status not in SUBSCRIPTION_STATUSES:
        raise ValueError(f"Invalid subscriptionStatus. Allowed values: {', '.join(SUBSCRIPTION_STATUSES)}.")


def validate_subscription_not_exists(name: str):
    if frappe.db.exists(DOCTYPE, name):
        raise ValueError(f"Subscription '{name}' already exists.")


def validate_subscription_exists(name: str):
    if not frappe.db.exists(DOCTYPE, name):
        raise ValueError(f"Subscription '{name}' does not exist.")


def validate_details(details):
    """Accept dict/list or a JSON string; return the parsed dict/list."""
    if isinstance(details, str):
        try:
            details = json.loads(details)
        except ValueError:
            raise ValueError("details must be valid JSON.")

    if not isinstance(details, (dict, list)):
        raise ValueError("details must be a JSON object or array.")

    return details
