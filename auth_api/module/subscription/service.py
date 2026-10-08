import frappe
from frappe.utils import getdate, today

from auth_api.module.subscription.constant import DEFAULT_SUBSCRIPTION_STATUS, DOCTYPE, LIVE_SUBSCRIPTION_STATUSES
from auth_api.module.subscription.utils import build_subscribed_modules, build_subscription_response, parse_details
from auth_api.module.subscription.validate import (
    validate_bool,
    validate_date,
    validate_date_range,
    validate_subscription_exists,
    validate_subscription_name,
    validate_subscription_not_exists,
    validate_subscription_status,
    validate_trial,
)


def create_subscription(name: str, subscription_status: str = None, details=None,
                        start_date=None, end_date=None, trial_enabled=None, trial_end_date=None) -> dict:
    validate_subscription_name(name)
    name = name.strip()

    subscription_status = subscription_status or DEFAULT_SUBSCRIPTION_STATUS
    validate_subscription_status(subscription_status)
    start_date = validate_date(start_date, "start_date")
    end_date = validate_date(end_date, "end_date")
    validate_date_range(start_date, end_date)
    trial_end_date = validate_trial(
        validate_bool(trial_enabled, "trial_enabled"), validate_date(trial_end_date, "trial_end_date"), start_date
    )
    validate_subscription_not_exists(name)

    doc = frappe.get_doc({
        "doctype":                  DOCTYPE,
        "master_subscription_name": name,
        "subscription_status":      subscription_status,
        "details":                   parse_details(details),
        "start_date":               start_date,
        "end_date":                 end_date,
        "trial_end_date":           trial_end_date,
    })
    doc.insert(ignore_permissions=True)
    # frappe.db.commit()

    return build_subscription_response(doc)


def update_subscription(name: str, subscription_status: str = None, details=None,
                        start_date=None, end_date=None, trial_enabled=None, trial_end_date=None) -> dict:
    validate_subscription_name(name)
    validate_subscription_exists(name)
    validate_subscription_status(subscription_status)
    start_date = validate_date(start_date, "start_date")
    end_date = validate_date(end_date, "end_date")
    trial_enabled = validate_bool(trial_enabled, "trial_enabled")
    trial_end_date = validate_date(trial_end_date, "trial_end_date")

    doc = frappe.get_doc(DOCTYPE, name)

    if subscription_status:
        doc.subscription_status = subscription_status

    if details is not None:
        doc.details = parse_details(details)

    if start_date:
        doc.start_date = start_date
    if end_date:
        doc.end_date = end_date
    doc_start = getdate(doc.start_date) if doc.start_date else None
    validate_date_range(doc_start, getdate(doc.end_date) if doc.end_date else None)

    if trial_enabled is not None:  # only touch the trial when the flag is sent
        doc.trial_end_date = validate_trial(trial_enabled, trial_end_date, doc_start)

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return build_subscription_response(doc)


def delete_subscription(name: str) -> dict:
    validate_subscription_name(name)
    validate_subscription_exists(name)

    frappe.delete_doc(DOCTYPE, name, ignore_permissions=True)
    frappe.db.commit()

    return {"master_subscription_name": name}


def get_subscribed_modules() -> dict:

    details = frappe.get_all(
        DOCTYPE,
        filters={"subscription_status": ["in", LIVE_SUBSCRIPTION_STATUSES], "start_date": ["<=", today()]},
        or_filters=[["end_date", "is", "not set"], ["end_date", ">", today()]],
        pluck="details",
    )
    return build_subscribed_modules(details)
