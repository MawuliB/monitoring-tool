from .aws import AWSPlatform
from .local import LocalPlatform
from .base import LogPlatform

def get_platform_handler(platform_type: str) -> LogPlatform:
    """Get the appropriate platform handler."""
    handlers = {
        'aws': AWSPlatform(),
        'local': LocalPlatform(),
        # Add more platform handlers here
    }
    return handlers.get(platform_type)

__all__ = ['get_platform_handler', 'AWSPlatform', 'LogPlatform'] 