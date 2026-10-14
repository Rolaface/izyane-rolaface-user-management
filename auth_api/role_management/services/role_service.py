from auth_api.role_management.services.permission_service import create_permission
from auth_api.role_management.utils.role_utils import build_role_search_filter, delete_removed_permissions, validate_role_exists, validate_role_name, build_role_doc
import frappe
from frappe.permissions import get_all_perms
from auth_api.role_management.utils.permission_mapper import expand_with_linked_permissions

def create_role(role_name: str, permission: list = []) -> dict:
   
    validate_role_name(role_name)

    role_data = build_role_doc(role_name)

    role = frappe.get_doc(role_data)
    role.insert(ignore_permissions=True)

    expanded_permissions = expand_with_linked_permissions(permission)

    create_permission(expanded_permissions, role.name)

    return {"roleId": role.name}

def update_role(role_id: str, permissions: list = []) -> dict:

    expanded_permissions = expand_with_linked_permissions(permissions)

    create_permission(expanded_permissions, role_id)
    incoming_modules = [perm["module"] for perm in expanded_permissions if perm.get("module")]

    delete_removed_permissions(role_id, incoming_modules)
    return {"roleId": role_id}

def update_role_status(role_id: str, is_disabled: bool):
    frappe.db.set_value("Role", role_id, "disabled", int(is_disabled))
    frappe.db.commit()

    return {
        "roleId":   role_id,
        "disabled": is_disabled,
    }

def get_all_roles(page, page_size, search: str = None, order_by: str = "creation desc") -> dict:
    filters    = {"is_custom": 1}

    or_filters    = build_role_search_filter(search=search)
    limit_start   = (page - 1) * page_size

    total = frappe.db.count("Role", filters=filters) #@TODO: If Filters are added, then only incule is_cutom: 1 filters

    roles = frappe.db.get_all(
        doctype = "Role",
        filters = filters,
        or_filters = or_filters or None,
        fields = ["name", "role_name", "disabled"],
        order_by = order_by,
        limit_start  = limit_start,
        limit_page_length = page_size,
    )

    normalized = [
        {
            "Id": role.name,
            "roleName": role.role_name,
            "disabled": role.disabled
        }
        for role in roles
    ]

    employee_role = frappe.db.get_value("Role", "Employee", ["name", "role_name", "disabled"], as_dict=True)

    if employee_role and not any(r["Id"] == "Employee" for r in normalized):
        normalized.append({
            "Id":       employee_role.name,
            "roleName": employee_role.role_name,
            "disabled": employee_role.disabled,
        })
        total += 1

    total_pages = max(1, -(-total // page_size))

    return {
        "data": normalized,
        "pagination": {
            "page":        page,
            "page_size":   page_size,
            "total":       total,
            "total_pages": total_pages,
            "has_next":    page < total_pages,
            "has_prev":    page > 1,
        },
    }

def get_role(role_name: str) -> dict:

    validate_role_exists(role_name)

    role = frappe.db.get_value(
                "Role",
                role_name,
                ["name", "role_name"],
                as_dict=True,
            )

    perms = get_all_perms(role_name)
    permissions = [
        {
            "module": perm.parent,
            "read": perm.read,
            "write": perm.write,
            "create": perm.create,
            "delete": perm.delete,
            "report": perm.report,
            "import": perm.get("import"),
            "export": perm.export,
            "submit": perm.submit,
            "cancel": perm.cancel,
        }
        for perm in perms
    ]

    return {
        "roleId":      role.name,
        "roleName":    role.role_name,
        "permissions": permissions,
    }