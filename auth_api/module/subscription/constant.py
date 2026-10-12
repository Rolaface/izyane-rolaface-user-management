DOCTYPE = "Custom Subscription Details"

DEFAULT_SUBSCRIPTION_STATUS = "Active"

SUBSCRIPTION_STATUSES = ("Active", "Trialing", "Scheduled", "Expired", "Cancelled")

LIVE_SUBSCRIPTION_STATUSES = ("Scheduled", "Trialing", "Active")
CANCELLED_SUBSCRIPTION_STATUS = "Cancelled"

# when every subscription has expired the site is read-only (database level, whatever the HTTP method)...
# ...except for these calls, so users can still sign in / out and the master can sync a renewal
READ_ONLY_EXEMPT_METHODS = (
    "login",
    "logout",
    "auth_api.user_management.api.auth.login",
    "auth_api.user_management.api.auth.logout",
    "auth_api.user_management.api.auth.forgot_password",
    "auth_api.module.subscription.api.create",
    "auth_api.module.subscription.api.update",
    "auth_api.module.subscription.api.delete",
)
SUBSCRIPTION_EXPIRED_TITLE = "Subscription Expired"
SUBSCRIPTION_EXPIRED_MESSAGE = (
                                    "Your subscription has expired, so this action is blocked. "
                                    "You can still view your data. Renew your subscription to continue making changes."
                                )