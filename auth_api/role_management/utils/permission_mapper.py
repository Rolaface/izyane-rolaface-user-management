LINKED_DOCTYPE_PERMISSION_MAP = {
    "Customer": ["Address", "Contact", "Currency"],
    "Purchase Order": ["Cost Center", "Project", "Address"],
    "Supplier": ["Currency"],
    "Item": ["UOM", "Brand"],
    "Purchase Invoice": ["Cost Center", "Project", "Serial and Batch Bundle", "Address"],
    "Payment Entry": ["GL Entry", "Cost Center", "Project", "Party Type"],
    "Account": ["GL Entry", "Party Type"],
    "Sales Invoice": ["Cost Center", "Project", "Serial and Batch Bundle", "Address"],
    "Role": ["Custom DocPerm"],
    "Employee": ["Address", "Contact", "Department", "Designation", "Employee Grade", "Employment Type"],
    "Payroll Entry": ["Salary Component", "Salary Structure", "Income Tax Slab", "Payroll Period"],
    "Loan": ["Loan Security Assignment"],
    "Loan Restructure": ["Loan Repayment Schedule"],
    "Loan Disbursement": ["Loan Repayment Schedule", "Process Loan Interest Accrual", "Customer"],
    "Loan Repayment":["Loan Interest Accrual", "Loan Demand", "Journal Entry"],
}


def expand_with_linked_permissions(permissions: list) -> list:

    # ── Used a dict to merge linked permissions by module ─────────────────────
    # Key: linked_doctype, Value: merged ptype_map
    # This handles the case where multiple roots share the same linked doctype
    # e.g. Customer(read=0) + Supplier(read=1) → Currency gets read=1
    explicit_modules = {p["module"] for p in permissions}
    linked_map: dict = {}

    for permission in permissions:
        module          = permission["module"]
        linked_doctypes = LINKED_DOCTYPE_PERMISSION_MAP.get(module)

        if not linked_doctypes:
            continue

        # ── Inherit everything except the module key itself ───────────────────
        inherited_ptype_map = {k: v for k, v in permission.items() if k != "module"}

        if not inherited_ptype_map:
            continue

        for linked_doctype in linked_doctypes:
            # ── Skip if already explicitly defined in payload ─────────────────
            if linked_doctype in explicit_modules:
                continue

            if linked_doctype not in linked_map:
                # First root to claim this linked doctype
                linked_map[linked_doctype] = inherited_ptype_map.copy()
            else:
                # ── Merge — take the highest value (1 wins over 0) per ptype ──
                for ptype, value in inherited_ptype_map.items():
                    existing_value = linked_map[linked_doctype].get(ptype, 0)
                    linked_map[linked_doctype][ptype] = max(existing_value, value)

    # ── Build final linked permissions list from merged map ──────────────────
    linked_permissions = [
        {"module": doctype, **ptype_map}
        for doctype, ptype_map in linked_map.items()
    ]

    return permissions + linked_permissions