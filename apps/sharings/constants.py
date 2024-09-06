class PermissionLevels:
    """
    User can share its diagrams with other users using following permission levels:
    - view-only: user can only view shared diagram;
    - view-copy: user can view and copy shared diagram to his/her own account;
    - view-edit: user can view, copy, and edit shared diagram.
    """

    VIEWONLY = "view-only"
    VIEWCOPY = "view-copy"
    VIEWEDIT = "view-edit"

    CHOICES = (
        (VIEWONLY, "View"),
        (VIEWCOPY, "View & Copy"),
        (VIEWEDIT, "View & Edit"),
    )
