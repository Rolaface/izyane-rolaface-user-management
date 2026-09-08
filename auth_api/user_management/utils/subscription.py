# myapp/subscription/get.py
import frappe
from frappe.utils import getdate

DOCTYPE = "Custom Subscription Management"
CACHE_KEY = "subscribed_modules"


def get_subscribed_modules():
    # cached = frappe.cache().get_value(CACHE_KEY)
    # if cached is not None:
    #     return cached

    rows = frappe.get_all(
        DOCTYPE,
        fields=[
            "name", "feature_code", "feature_label", "parent_custom_subscription_management",
            "is_group", "is_subscribed", "start_date", "end_date",
        ],
    )

    by_parent = {}
    for r in rows:
        by_parent.setdefault(r.parent_custom_subscription_management, []).append(r)

    today = getdate()

    def is_active(r):
        if not r.is_subscribed:
            return False
        if r.start_date and today < getdate(r.start_date):
            return False
        if r.end_date and today > getdate(r.end_date):
            return False
        return True

    def build(parent_name, ancestor_active=True, add_enabled=False):
        node = {}
        for r in by_parent.get(parent_name, []):
            active = ancestor_active and is_active(r)
            key = r.feature_label or r.feature_code
            if r.name == "lending":
                node[key] = active
            elif r.is_group:
                child = build(r.name, active)
                if add_enabled:
                    child = {"enabled": active, **child}
                node[key] = child   
            else:
                node[key] = active
        return node

    result = build(None, add_enabled=True)
    frappe.cache().set_value(CACHE_KEY, result, expires_in_sec=3600)
    return result