import frappe
class UserRepository:
    @staticmethod
    def create_user(data: dict) -> frappe.model.document.Document:

        user = frappe.get_doc({
            "doctype": "User",
            "email": data["email"],
            "first_name": data["firstName"],
            "middle_name": data.get("middleName"),
            "last_name": data["lastName"],
            "username": data["username"],
            "language": data.get("language"),
            "time_zone": data.get("timezone"),
            "enabled": 1,
            "roles": [{"role": role} for role in data.get("roleIds", [])],
            "gender": data["gender"],
            "birth_date": data["dob"],
            "phone": data["phone"],
            "mobile_no": data["mobile_no"]
        })

        user.insert(ignore_permissions=True)
        return user
    
    @staticmethod
    def get_users(search=None, roles=None, limit_start=0, limit_page_length=10, exclude_current_user=True):
        
        filters = [
            ["name", "not in", ["Administrator", "Guest"]],
        ]
        
        if exclude_current_user and frappe.session.user:
            filters.append(["name", "!=", frappe.session.user])

        if roles:
            role_users = frappe.get_all(
                "Has Role",
                filters={"role": ["in", roles], "parenttype": "User"},
                pluck="parent"
            )
            
            if not role_users:
                return [], 0
                
            filters.append(["name", "in", role_users])

        or_filters = None
        if search:
            or_filters = [
                ["name", "like", f"%{search}%"],
                ["email", "like", f"%{search}%"],
                ["first_name", "like", f"%{search}%"],
                ["last_name", "like", f"%{search}%"],
                ["username", "like", f"%{search}%"],
            ]

        users = frappe.get_all(
            "User",
            or_filters=or_filters,
            filters=filters,
            fields=[
                "name as id",
                "email",
                "full_name as name",
                "username",
                "enabled",
                "creation"
            ],
            limit_start=limit_start,
            limit_page_length=limit_page_length,
            order_by="creation desc"
        )
        
        total = len(frappe.get_all("User", filters=filters, or_filters=or_filters, pluck="name"))
        return users, total

    @staticmethod
    def update_user(user_id: str, data: dict) -> frappe.model.document.Document:
        user = frappe.get_doc("User", user_id)

        field_map = {
            "firstName":  "first_name",
            "middleName": "middle_name",
            "lastName":   "last_name",
            "username":   "username",
            "language":   "language",
            "timezone":   "time_zone",
            "gender":     "gender",
            "dob":        "birth_date",
            "phone":      "phone",
            "mobile_no":  "mobile_no",
        }

        for payload_key, doc_field in field_map.items():
            if payload_key in data:
                setattr(user, doc_field, data[payload_key])

        if "roleIds" in data:
            user.set("roles", [{"role": role} for role in data["roleIds"]])

        user.save(ignore_permissions=True)
        return user