from auth_api.user_management.utils.subscription import get_subscribed_modules
from auth_api.user_management.repositories.user_repo import UserRepository
import frappe
from frappe.permissions import get_all_perms
class UserService:

    @staticmethod
    def signup(payload: dict) -> dict:
        try:
            frappe.db.begin()

            UserRepository.create_user(payload)

            return {
                "status": "success",
                "message": "User created successfully, Please check your email for login credentials"
            }

        except Exception:
            frappe.db.rollback()
            raise

    @staticmethod
    def get_users(page=1, page_size=10, search=""):

        limit_start = (page - 1) * page_size
        filters = [
            ["name", "not in", ["Administrator", "Guest"]],
        ]
        users = UserRepository.get_users(
            search=search,
            limit_start=limit_start,
            limit_page_length=page_size
        )

        total = frappe.db.count("User", filters=filters)

        total_pages = (total + page_size - 1) // page_size
        print(type(users))
        return {
            "status": "success",
            "data": users,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }
        }

    @staticmethod
    def update_user_details(payload:dict) -> dict:
        try:
            frappe.db.begin()
    
            UserRepository.update_user(payload["id"],payload)

            return {
                "status": "success",
                "message": "User updated successfully"
            }

        except Exception:
            frappe.db.rollback()
            raise
    
    @staticmethod
    def get_user(user_id) -> dict:
        user = frappe.get_doc("User", user_id)
        if not user:
            return{
                "status": "error",
                "message": "User not found"
            }
        roles = frappe.db.get_all(
                "Has Role",
                filters = {
                    "parent": user_id,
                    "parenttype": "User",
                }, pluck = "role",
            )          

        module_permissions_map = {}

        for role in roles:
            perms = get_all_perms(role)
            for perm in perms:

                module = perm.parent

                if not module:
                    continue

                if module not in module_permissions_map:
                    module_permissions_map[module] = {
                        "module": module,
                        "read": 0,
                        "write": 0,
                        "create": 0,
                        "delete": 0,
                        "report": 0,
                        "import": 0,
                        "export": 0,
                        "submit": 0,
                        "cancel": 0,
                    }

                module_permissions_map[module]["read"]   = max(module_permissions_map[module]["read"], perm.read)
                module_permissions_map[module]["write"]  = max(module_permissions_map[module]["write"], perm.write)
                module_permissions_map[module]["create"] = max(module_permissions_map[module]["create"], perm.create)
                module_permissions_map[module]["delete"] = max(module_permissions_map[module]["delete"], perm.delete)
                module_permissions_map[module]["report"] = max(module_permissions_map[module]["report"], perm.report)
                module_permissions_map[module]["import"] = max(module_permissions_map[module]["import"], perm.get("import") or 0)
                module_permissions_map[module]["export"] = max(module_permissions_map[module]["export"], perm.export)
                module_permissions_map[module]["submit"] = max(module_permissions_map[module]["submit"], perm.submit)
                module_permissions_map[module]["cancel"] = max(module_permissions_map[module]["cancel"], perm.cancel)

        modules_permissions = list(module_permissions_map.values())
        # ── Fetch Employee ID if this user is linked to an Employee ──────────────
        employee_id = frappe.db.get_value(
            "Employee",
            {"user_id": user_id},
            "name",
        )
        installed_apps = frappe.get_installed_apps()
        subscribed_modules = get_subscribed_modules()

        return {
                "userId": user.name,
                "employeeId": employee_id,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "middleName": user.middle_name,
                "fullName": user.full_name,
                "email": user.email,
                "gender": user.gender,
                "username": user.username,
                "language": user.language,
                "timezone": user.time_zone,
                "dob": user.birth_date,
                "phone": user.phone,
                "mobile_no":user.mobile_no,
                "roles": roles,
                "permission": modules_permissions,
                "is_zra_enabled":  True if "zra_smart_invoice" in installed_apps else False,
                # "subscribed_modules": installed_apps,
                "subscribed_modules": subscribed_modules

        }
