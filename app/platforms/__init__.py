from .aws import AWSPlatform
from .local import LocalPlatform
from .base import LogPlatform
from .els import ElasticsearchPlatform
from .google import GoogleCloudPlatform
from .azure import AzurePlatform

def get_platform_handler(platform_type: str) -> LogPlatform:
    """Get the appropriate platform handler."""
    handlers = {
        'aws': AWSPlatform(),
        'local': LocalPlatform(),
        'els': ElasticsearchPlatform(),
        'gcp': GoogleCloudPlatform(),
        'azure': AzurePlatform(),
        # Add more platform handlers here
    }
    return handlers.get(platform_type)

__all__ = ['get_platform_handler', 'AWSPlatform', 'LogPlatform', 'ElasticsearchPlatform', 'GoogleCloudPlatform', 'AzurePlatform'] 