from .constant import DOCTYPE
from .service import create_subscription, delete_subscription, update_subscription
from auth_api.user_management.utils import response
import frappe

@frappe.whitelist(allow_guest=True, methods=["POST"])
def create():
    data = frappe.request.get_json() or {}

    try:
        result = create_subscription(
            name                = data.get("master_subscription_name"),
            subscription_status = data.get("subscription_status"),
            details             = data.get("details"),
            start_date          = data.get("start_date"),
            end_date            = data.get("end_date"),
            trial_enabled       = data.get("trial_enabled"),
            trial_end_date      = data.get("trial_end_date"),
        )

        return response.success(result, "Subscription created successfully.", http_status_code=201)

    except ValueError as e:
        return response.error(str(e))

@frappe.whitelist(allow_guest=True, methods=["PUT"])
def update():
    data = frappe.request.get_json() or {}

    try:
        result = update_subscription(
            name                = data.get("master_subscription_name"),
            subscription_status = data.get("subscription_status"),
            details             = data.get("details"),
            start_date          = data.get("start_date"),
            end_date            = data.get("end_date"),
            trial_enabled       = data.get("trial_enabled"),
            trial_end_date      = data.get("trial_end_date"),
        )

        return response.success(result, "Subscription updated successfully.", http_status_code=200)

    except ValueError as e:
        return response.error(str(e))

@frappe.whitelist(allow_guest=True, methods=["DELETE"])
def delete():
    data = frappe.request.get_json(silent=True) or frappe.request.args or {}

    try:
        result = delete_subscription(name=data.get("master_subscription_name"))

        return response.success(result, "Subscription deleted successfully.", http_status_code=200)

    except ValueError as e:
        return response.error(str(e))
