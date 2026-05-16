from celery import shared_task
from django.utils import timezone
from .models import Router, RouterLog
from .utils import RouterOSClient, MikroTikError
import logging

logger = logging.getLogger(__name__)

@shared_task
def monitor_routers_health():
    """Periodic task to check if routers are online (with Mock support)."""
    is_mock = getattr(settings, 'MIKROTIK_MOCK_MODE', False)
    routers = Router.objects.all()
    
    for router in routers:
        if is_mock:
            router.is_online = True
            router.save()
            continue

        was_online = router.is_online
        try:
            with RouterOSClient(router) as client:
                # If we get here, connection was successful
                router.is_online = True
                router.save()
                
                if not was_online:
                    RouterLog.objects.create(
                        router=router,
                        level='INFO',
                        message="Router back online"
                    )
        except Exception:
            router.is_online = False
            router.save()
            
            if was_online:
                RouterLog.objects.create(
                    router=router,
                    level='CRITICAL',
                    message="Router went offline!"
                )
                logger.error(f"Router {router.name} ({router.ip_address}) is OFFLINE")
