from .constant import DOCTYPE
from .service import create_subscription, delete_subscription, update_subscription
from auth_api.user_management.utils import response
import frappe

@frappe.whitelist(allow_guest=True, methods=["POST"])
def create():
    data = frappe.request.get_json() or {}

    try:
        result = create_subscription(
            name                = data.get("masterSubscriptionName"),
            subscription_status = data.get("subscriptionStatus"),
            details             = data.get("details"),
        )

        return response.success(result, "Subscription created successfully.", http_status_code=201)

    except ValueError as e:
        return response.error(str(e))

@frappe.whitelist(allow_guest=False, methods=["PUT"])
def update():
    data = frappe.request.get_json() or {}

    try:
        result = update_subscription(
            name                = data.get("masterSubscriptionName"),
            subscription_status = data.get("subscriptionStatus"),
            details             = data.get("details"),
        )

        return response.success(result, "Subscription updated successfully.", http_status_code=200)

    except ValueError as e:
        return response.error(str(e))

@frappe.whitelist(allow_guest=False, methods=["DELETE"])
def delete():
    data = frappe.request.get_json(silent=True) or frappe.request.args or {}

    try:
        result = delete_subscription(name=data.get("masterSubscriptionName"))

        return response.success(result, "Subscription deleted successfully.", http_status_code=200)

    except ValueError as e:
        return response.error(str(e))
