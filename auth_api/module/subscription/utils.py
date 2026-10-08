import json

from auth_api.module.subscription.validate import validate_details


def parse_details(details):
    if details is None:
        return None

    return json.dumps(validate_details(details))


def build_subscription_response(doc) -> dict:
    details = doc.details
    if isinstance(details, str):
        try:
            details = json.loads(details)
        except ValueError:
            pass

    return {
        "master_subscription_name": doc.master_subscription_name,
        "subscription_status":      doc.subscription_status,
        "details":                  details,
        "start_date":               str(doc.start_date) if doc.start_date else None,
        "end_date":                 str(doc.end_date) if doc.end_date else None,
        "trial_end_date":           str(doc.trial_end_date) if doc.trial_end_date else None,
    }
