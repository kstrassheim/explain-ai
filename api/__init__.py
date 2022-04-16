from .auth import urls as auth_urls
from .explain import urls as explain_urls
from .item import urls as item_urls
urls = auth_urls + explain_urls + item_urls