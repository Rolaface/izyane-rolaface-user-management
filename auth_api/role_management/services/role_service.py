from auth_api.role_management.constant import ALWAYS_INCLUDED_ROLES
from auth_api.role_management.services.permission_service import create_permission
from auth_api.role_management.utils.role_utils import _parse_order_by, delete_removed_permissions, validate_role_exists, validate_role_name, build_role_doc
import frappe
from frappe.permissions import get_all_perms
from auth_api.role_management.utils.permission_mapper import expand_with_linked_permissions
from frappe.utils import cint
from frappe.query_builder.functions import Count

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

def get_all_roles(page=1, page_size=10, search: str = None, order_by: str = "creation desc") -> dict:
    page = max(1, cint(page))
    page_size = max(1, min(cint(page_size) or 10, 100))
    limit_start = (page - 1) * page_size

    Role = frappe.qb.DocType("Role")

    # Custom roles plus the roles we always show (Employee)
    condition = (Role.is_custom == 1) | (Role.name.isin(ALWAYS_INCLUDED_ROLES))

    if search:
        like = f"%{search.strip()}%"
        condition &= (Role.name.like(like)) | (Role.role_name.like(like))

    # Total uses the same condition as the data query, so pagination always matches
    total = (
        frappe.qb.from_(Role)
        .select(Count("*"))
        .where(condition)
    ).run()[0][0]

    sort_field, sort_order = _parse_order_by(order_by)

    roles = (
        frappe.qb.from_(Role)
        .select(Role.name, Role.role_name, Role.disabled)
        .where(condition)
        .orderby(Role[sort_field], order=sort_order)
        .orderby(Role.name)  # tie-breaker for stable paging
        .limit(page_size)
        .offset(limit_start)
    ).run(as_dict=True)

    normalized = [
        {"Id": r.name, "roleName": r.role_name, "disabled": r.disabled}
        for r in roles
    ]

    total_pages = max(1, -(-total // page_size))

    return {
        "data": normalized,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
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