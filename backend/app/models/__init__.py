"""Models package — import all models here so Flask-Migrate discovers them."""
from app.models.user import User  # noqa: F401
from app.models.analysis import Analysis  # noqa: F401
from app.models.token_blocklist import TokenBlocklist  # noqa: F401
from app.models.feedback import Feedback  # noqa: F401
