from django.db.models import Count, Q
from .models import Router, RouterGroup
from apps.billing.models import HotspotSession

class RouterSelector:
    """Service to select the best router for a session."""
    
    @staticmethod
    def get_best_router(group_id=None):
        """
        Selects a router based on:
        1. Online status (Must be True)
        2. Group (Optional)
        3. Load Balancing (Least active sessions)
        """
        queryset = Router.objects.filter(is_online=True)
        
        if group_id:
            queryset = queryset.filter(group_id=group_id)
            
        # Failover logic: If no routers in group are online, try any online router
        if not queryset.exists():
            queryset = Router.objects.filter(is_online=True)
            
        if not queryset.exists():
            return None

        # Load balancing: Get router with least active sessions
        # Note: This is a simple implementation. In a huge scale, cache this.
        router = queryset.annotate(
            active_count=Count('hotspotsession', filter=Q(hotspotsession__is_active=True))
        ).order_by('active_count').first()
        
        return router
