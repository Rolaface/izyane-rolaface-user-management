from auth_api.user_management.api.schema import SignupSchema, UpdateUserSchema
from auth_api.user_management.utils import response
from auth_api.user_management.utils.pydantic_errors import format_pydantic_errors
import frappe
from auth_api.user_management.services import auth_service, user_service
from pydantic import ValidationError
from frappe.core.doctype.user.user import reset_password

@frappe.whitelist(allow_guest=True, methods=["POST"])
def login(usr, pwd):
    try:
        user_data = auth_service.login_user(usr, pwd)
        if user_data.get("status") == "error":
            return response.error(user_data.get("message"))
        return response.success(user_data.get("message"), http_status_code=200)
    except frappe.exceptions.AuthenticationError as e:
        return response.unauthorized(str(e))

@frappe.whitelist(allow_guest=False, methods=["POST"])
def signup(**payload):
    try:
        data = SignupSchema(**payload).model_dump()
        user = user_service.UserService.signup(data)
        if user.get("status") == "error":
            return response.error(user.get("message"))
        return response.success(user.get("message"), http_status_code=201)
    except ValidationError as e:
        return response.validation_error(format_pydantic_errors(e))

@frappe.whitelist(allow_guest=True, methods=["POST"])
def forgot_password(email: str):
    try:
        user = frappe.get_doc("User", email)

        reset_password(user=email)
        return response.success(
                                "Password reset link sent to your email, Please check your inbox", 
                                http_status_code=200
                            )
    except Exception as e:
        return response.error(str(e),
                                http_status_code=500
                            )
    
@frappe.whitelist(allow_guest=True, methods=["POST"])
def logout():
    # Please add SID in cookies to logout properly.
    try:
        frappe.local.login_manager.logout()
        return response.success("Logged out successfully")
    except Exception as e:
        return response.error("Unable to process your request, Please try again later",
                                http_status_code=500
                            )

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get():

    data = frappe.local.form_dict
    page = int(data.get("page", 1))
    page_size = int(data.get("page_size", 10))
    search = data.get("search")
    
    roles = data.get("roles")
    if roles and isinstance(roles, str):
        try:
            roles = frappe.parse_json(roles)
        except Exception:
            roles = [r.strip() for r in roles.split(",")]

    user_response = user_service.UserService.get_users(page, page_size, search, roles)
    
    return response.send_response_list(
        status="success",
        message="Users fetched successfully.",
        data=user_response,
        status_code=200,
        http_status=200,
    )

@frappe.whitelist(allow_guest=False, methods=["PUT"])
def update(**payload):
    try:
        data = UpdateUserSchema(**payload).model_dump()
        user = user_service.UserService.update_user_details(data)
        if user.get("status") == "error":
            return response.error(user.get("message"))
        return response.success(user.get("message"), http_status_code=201)
    except ValidationError as e:
        return response.validation_error(format_pydantic_errors(e))
    
@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_user_by_id():
    user_id = frappe.request.args.get("id")
    
    user_detail = user_service.UserService.get_user(user_id)
    
    return response.success(user_detail, http_status_code=201)

@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_login_user():
    user = frappe.get_doc('User', frappe.session.user)
    user_detail = user_service.UserService.get_user(user.name)
    return response.success(user_detail, http_status_code=201)
    