PASSWORD_MIN_LENGTH = 8
PASSWORD_SPECIAL_CHARS = '!@#$%^&*(),.?":{}|<>'


class UserRoles:
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    CHOICES = (
        (USER, "User"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    )
    """User roles and role names, displayed in the admin panel."""
