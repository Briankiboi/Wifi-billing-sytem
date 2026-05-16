import routeros_api
import logging
from django.conf import settings
from .models import RouterLog

logger = logging.getLogger(__name__)

class MikroTikError(Exception):
    """Custom exception for MikroTik API errors."""
    pass

class MockMikroTikResource:
    """Simulates a MikroTik API resource (e.g., /ip/hotspot/user)."""
    def add(self, **kwargs):
        logger.info(f"[MOCK] Added resource with params: {kwargs}")
        return [{'.id': '*MOCK_ID*'}]

    def get(self, **kwargs):
        logger.info(f"[MOCK] GET resource with params: {kwargs}")
        return []

    def set(self, id, **kwargs):
        logger.info(f"[MOCK] SET resource {id} with params: {kwargs}")
        return True

    def remove(self, id):
        logger.info(f"[MOCK] REMOVED resource {id}")
        return True

class MockMikroTikAPI:
    """Simulates the MikroTik API object."""
    def get_resource(self, path):
        return MockMikroTikResource()

class RouterOSClient:
    """Handles connection management with Mock support."""
    def __init__(self, router):
        self.router = router
        self.connection = None
        self.api = None
        self.is_mock = getattr(settings, 'MIKROTIK_MOCK_MODE', False)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        if self.is_mock:
            logger.info(f"[MOCK] Simulating connection to router {self.router.ip_address}")
            self.api = MockMikroTikAPI()
            return self.api

        try:
            use_ssl = self.router.api_port == 8729
            self.connection = routeros_api.RouterOsApiPool(
                self.router.ip_address,
                username=self.router.username,
                password=self.router.decrypted_password,
                port=self.router.api_port,
                use_ssl=use_ssl,
                ssl_verify=False,
                plaintext_login=True
            )
            self.api = self.connection.get_api()
            return self.api
        except Exception as e:
            RouterLog.objects.create(
                router=self.router,
                level='ERROR',
                message=f"Connection failed: {str(e)}"
            )
            raise MikroTikError(f"Could not connect to {self.router.ip_address}: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()

class HotspotService:
    def __init__(self, api, router):
        self.api = api
        self.router = router
        self.resource = self.api.get_resource('/ip/hotspot/user')
        self.active_resource = self.api.get_resource('/ip/hotspot/active')

    def create_user(self, name, password, profile, limit_uptime=None, comment=""):
        try:
            params = {'name': name, 'password': password, 'profile': profile, 'comment': comment}
            if limit_uptime: params['limit-uptime'] = limit_uptime
            return self.resource.add(**params)
        except Exception as e:
            logger.error(f"Failed to create hotspot user {name}: {e}")
            raise MikroTikError(str(e))

    def disable_user(self, name):
        user = self.resource.get(name=name)
        if user or getattr(settings, 'MIKROTIK_MOCK_MODE', False):
            user_id = user[0]['id'] if user else '*MOCK*'
            self.resource.set(id=user_id, disabled='yes')
            self.disconnect_active_user(name)
            return True
        return False

    def delete_user(self, name):
        user = self.resource.get(name=name)
        if user or getattr(settings, 'MIKROTIK_MOCK_MODE', False):
            user_id = user[0]['id'] if user else '*MOCK*'
            self.resource.remove(id=user_id)
            self.disconnect_active_user(name)
            return True
        return False

    def disconnect_active_user(self, name):
        active = self.active_resource.get(user=name)
        for session in active:
            self.active_resource.remove(id=session['id'])

class QueueService:
    def __init__(self, api, router):
        self.api = api
        self.router = router
        self.resource = self.api.get_resource('/queue/simple')

    def create_queue(self, name, target_ip, limit_at="1M/1M", max_limit="2M/2M"):
        try:
            return self.resource.add(name=name, target=target_ip, max_limit=max_limit, limit_at=limit_at)
        except Exception as e:
            logger.error(f"Failed to create queue for {name}: {e}")
            raise MikroTikError(str(e))

    def remove_queue(self, name):
        queue = self.resource.get(name=name)
        if queue or getattr(settings, 'MIKROTIK_MOCK_MODE', False):
            queue_id = queue[0]['id'] if queue else '*MOCK*'
            self.resource.remove(id=queue_id)
            return True
        return False
