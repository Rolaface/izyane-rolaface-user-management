# myapp/subscription/setup.py
import frappe
from frappe.utils import today

# (feature_code, feature_label_or_None, is_group_0_or_1,parent_feature_or_None)
# Ordered parent-before-child so inserts never hit a missing Link target.
DEFAULT_FEATURES = [
    # Roots
    ("erp", None, 1,None),
    ("hrms", None, 1,None),
    ("lending", None, 1,None),

    # erp children
    ("sales", None, 0,"erp"),
    ("customer", None, 0,"erp"),
    ("procurement", None, 0,"erp"),
    ("assets", None, 0,"erp"),
    ("accounting", None, 0,"erp"),
    ("inventory", None, 1,"erp"),
    ("settings", None, 1,"erp"),

    # erp.inventory children
    ("warehouse", None, 0,"inventory"),
    ("stockEntry", None, 0,"inventory"),
    ("item", None, 0,"inventory"),

    # erp.settings children
    ("bank", None, 0,"settings"),
    ("email", None, 0,"settings"),
    ("company", None, 0,"settings"),
    ("userAndRoles", None, 0,"settings"),
    ("scheduler", None, 0,"settings"),
    ("taxMain", None, 1,"settings"),

    # erp.settings.taxMain children
    ("itemTax", None, 0,"taxMain"),
    ("salesTax", None, 0,"taxMain"),
    ("taxCategory", None, 0,"taxMain"),

    # hrms children
    ("expenseManagement", None, 0,"hrms"),
    ("hrms_settings", "settings", 1,"hrms"),

    # hrms.settings children — codes prefixed to stay globally unique,
    # labels kept clean so the JSON output matches erp's shape
    ("hrms_bank", "bank", 0,"hrms_settings"),
    ("hrms_email", "email", 0,"hrms_settings"),
    ("hrms_company", "company", 0,"hrms_settings"),
    ("hrms_userAndRoles", "userAndRoles", 0,"hrms_settings"),
]

def ensure_default_features():
    for code, label, is_group,parent in DEFAULT_FEATURES:
        if frappe.db.exists("Custom Subscription Management", code):
            continue
        frappe.get_doc({
            "doctype": "Custom Subscription Management",
            "feature_code": code,
            "feature_label": label,
            "parent_custom_subscription_management": parent,
            "is_group": is_group,
            "is_subscribed": 1 if code != "lending" else 0,
            "start_date": today(),
        }).insert(ignore_permissions=True)
    frappe.db.commit()