import frappe

from auth_api.module.subscription.constant import DEFAULT_SUBSCRIPTION_STATUS, DOCTYPE
from auth_api.module.subscription.utils import build_subscription_response, parse_details
from auth_api.module.subscription.validate import (
    validate_subscription_exists,
    validate_subscription_name,
    validate_subscription_not_exists,
    validate_subscription_status,
)


def create_subscription(name: str, subscription_status: str = None, details=None) -> dict:
    validate_subscription_name(name)
    name = name.strip()

    subscription_status = subscription_status or DEFAULT_SUBSCRIPTION_STATUS
    validate_subscription_status(subscription_status)
    validate_subscription_not_exists(name)

    doc = frappe.get_doc({
        "doctype":                  DOCTYPE,
        "master_subscription_name": name,
        "subscription_status":      subscription_status,
        "status":                   parse_details(details),
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return build_subscription_response(doc)


def update_subscription(name: str, subscription_status: str = None, details=None) -> dict:
    validate_subscription_name(name)
    validate_subscription_exists(name)
    validate_subscription_status(subscription_status)

    doc = frappe.get_doc(DOCTYPE, name)

    if subscription_status:
        doc.subscription_status = subscription_status

    if details is not None:
        doc.status = parse_details(details)

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return build_subscription_response(doc)


def delete_subscription(name: str) -> dict:
    validate_subscription_name(name)
    validate_subscription_exists(name)

    frappe.delete_doc(DOCTYPE, name, ignore_permissions=True)
    frappe.db.commit()

    return {"masterSubscriptionName": name}
