from auth_api.role_management.services.role_service import create_role, get_all_roles, get_role, update_role, update_role_status
from auth_api.user_management.utils import response
from custom_api.permission import require_permission
import frappe

@frappe.whitelist(allow_guest=False, methods=["POST"])
@require_permission("Role", "create")
def create():
    data = frappe.request.get_json()

    role_name   = data.get("role")
    permission = data.get("permission", [])

    try:
        result = create_role(role_name=role_name, permission=permission)

        return response.success(result, http_status_code=200)

    except ValueError as e:
        return response.error(str(e))

@frappe.whitelist(allow_guest=False, methods=["GET"])
@require_permission("Role", "read")
def get():
    data = frappe.request.args

    try:
        page=int(data.get("page", 1))
        page_size=int(data.get("page_size", 10))

        search      = data.get("search", "").strip() or None
        order_by    = data.get("order_by", "creation desc")
        result = get_all_roles(page, page_size, search, order_by=order_by)

        return response.send_response_list(
                            status = "success",
                            message = "Roles fetched successfully.",
                            data = result,
                            status_code = 200,
                            http_status = 200,
                        )

    except ValueError as e:
        return response.error(str(e))

@frappe.whitelist(allow_guest=False, methods=["GET"])
@require_permission("Role", "read")
def get_by_id():
    role_name = frappe.request.args.get("id")

    if not role_name:
        return response.error("role is required.")

    try:
        result = get_role(role_name)

        return response.success(result, http_status_code=200)

    except ValueError as e:
        return response.error(str(e))

@frappe.whitelist(allow_guest=False, methods=["PUT"])
@require_permission("Role", "write")
def update():
    data = frappe.request.get_json()

    role_id   = data.get("role_id")
    permission = data.get("permission", [])

    try:
        result = update_role(role_id=role_id, permissions=permission)

        return response.success(result,"Roles Permission Updated successfully", http_status_code=200)

    except ValueError as e:
        return response.error(str(e))
    
@frappe.whitelist(allow_guest=False, methods=["PUT"])
@require_permission("Role", "write")
def update_status():
    data = frappe.request.get_json()

    role_id     = data.get("id")
    is_disabled = data.get("isDisabled")
    if not role_id:
        return response.error("Role is required")
    try:
        result = update_role_status(role_id=role_id, is_disabled=is_disabled)
        return response.success(result, f"Role {'disabled' if is_disabled else 'enabled'} successfully.")

    except Exception as err:
        response.error(str(err))