import json
import frappe
from frappe.utils import getdate
from auth_api.module.subscription.constant import DOCTYPE, SUBSCRIPTION_STATUSES

def validate_subscription_name(name: str):
    if not name or not str(name).strip():
        raise ValueError("master_subscription_name is required.")


def validate_subscription_status(status: str):
    if status and status not in SUBSCRIPTION_STATUSES:
        raise ValueError(f"Invalid subscription_status. Allowed values: {', '.join(SUBSCRIPTION_STATUSES)}.")


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

def validate_date(value, field: str):
    """Accept a YYYY-MM-DD string (or date); return a date, or None when empty."""
    if value in (None, ""):
        return None
    try:
        return getdate(value)
    except (ValueError, TypeError, frappe.ValidationError):
        raise ValueError(f"{field} must be a valid date (YYYY-MM-DD).")

def validate_date_range(start_date, end_date):
    if start_date and end_date and end_date < start_date:
        raise ValueError("end_date cannot be before start_date.")

def validate_bool(value, field: str):
    """Accept true/false, 1/0 or their string forms; return a bool, or None when not sent."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.strip().lower() in ("1", "true", "yes"):
        return True
    if isinstance(value, str) and value.strip().lower() in ("0", "false", "no"):
        return False
    raise ValueError(f"{field} must be true or false.")

def validate_trial(trial_enabled, trial_end_date, start_date):
    """trial_end_date is only kept when the trial is enabled, and then it is required."""
    if not trial_enabled:
        return None
    if not trial_end_date:
        raise ValueError("trial_end_date is required when trial_enabled is true.")
    if start_date and trial_end_date < start_date:
        raise ValueError("trial_end_date cannot be before start_date.")
    return trial_end_date
