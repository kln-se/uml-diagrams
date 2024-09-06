PASSWORD_MIN_LENGTH = 8
PASSWORD_SPECIAL_CHARS = '!@#$%^&*()_+,.?":{}|<>'


class UserRoles:
    """
    User roles and role names, displayed in the admin panel.
    """

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    CHOICES = (
        (USER, "User"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    )
