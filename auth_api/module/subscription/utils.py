import json

from auth_api.module.subscription.validate import validate_details


def parse_details(details):
    if details is None:
        return None

    return json.dumps(validate_details(details))


def build_subscription_response(doc) -> dict:
    details = doc.status
    if isinstance(details, str):
        try:
            details = json.loads(details)
        except ValueError:
            pass

    return {
        "masterSubscriptionName": doc.master_subscription_name,
        "subscriptionStatus":     doc.subscription_status,
        "details":                details,
    }
