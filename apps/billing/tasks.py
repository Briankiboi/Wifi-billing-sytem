import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from apps.billing.models import Transaction, HotspotSession, BandwidthUsage
from apps.routers.utils import RouterOSClient, HotspotService, QueueService, MikroTikError
from apps.accounts.models import UserDevice, User

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def activate_internet_session(self, transaction_id):
    """
    Main activation workflow.
    1. Verify transaction status
    2. Ensure Device/User records exist
    3. Create MikroTik Hotspot User
    4. Create MikroTik Simple Queue (optional)
    5. Save Session Record
    """
    try:
        with transaction.atomic():
            tx = Transaction.objects.select_for_update().get(id=transaction_id)
            if tx.status != 'COMPLETED':
                logger.warning(f"Attempted to activate incomplete transaction {tx.id}")
                return
            
            # 1. Get or Create User & Device
            user, _ = User.objects.get_or_create(phone_number=tx.user_phone)
            device, _ = UserDevice.objects.get_or_create(
                mac_address=tx.user_mac,
                defaults={'user': user}
            )

            # 2. MikroTik Integration
            with RouterOSClient(tx.router) as client:
                hs_service = HotspotService(client.api, tx.router)
                queue_service = QueueService(client.api, tx.router)
                
                # Create/Update Hotspot User
                # Profile name should exist in MikroTik (e.g., '1Mbps_Unlimited')
                profile = tx.package.name.replace(" ", "_")
                
                mikrotik_user = hs_service.create_user(
                    name=tx.user_mac,
                    password=tx.user_mac,
                    profile=profile,
                    comment=f"M-PESA:{tx.mpesa_code}"
                )

                if not mikrotik_user:
                    raise MikroTikError("MikroTik returned empty response during user creation")

                # 3. Create Session Record
                end_time = timezone.now() + tx.package.duration
                session = HotspotSession.objects.create(
                    user=user,
                    device=device,
                    package=tx.package,
                    router=tx.router,
                    transaction=tx,
                    end_time=end_time,
                    mikrotik_id=mikrotik_user[0]['.id']
                )

                logger.info(f"Successfully activated session {session.id} for MAC {tx.user_mac}")
                
    except (MikroTikError, Exception) as exc:
        logger.error(f"Activation failed for TX {transaction_id}: {exc}")
        # Retry for network-related failures
        raise self.retry(exc=exc)

@shared_task
def deactivate_expired_sessions():
    """Periodic task to sweep and disconnect expired sessions."""
    now = timezone.now()
    expired_sessions = HotspotSession.objects.filter(
        end_time__lte=now,
        is_active=True
    ).select_related('router', 'device')
    
    for session in expired_sessions:
        try:
            with RouterOSClient(session.router) as client:
                hs_service = HotspotService(client.api, session.router)
                queue_service = QueueService(client.api, session.router)
                
                # 1. Remove Hotspot User & Disconnect Active Session
                hs_service.delete_user(session.device.mac_address)
                
                # 2. Remove Simple Queue
                queue_service.remove_queue(session.device.mac_address)
                
                # 3. Mark as inactive in DB
                session.is_active = False
                session.save()
                
                logger.info(f"Terminated expired session {session.id} for MAC {session.device.mac_address}")
                
        except MikroTikError as e:
            logger.error(f"Router {session.router.name} offline during deactivation of {session.id}: {e}")
            # We don't mark as inactive here so the next sweep will try again
        except Exception as e:
            logger.error(f"Critical error during session deactivation {session.id}: {e}")

@shared_task
def deactivate_session(session_id):
    """Specific task to disconnect a single session at its expiry time."""
    try:
        session = HotspotSession.objects.get(id=session_id, is_active=True)
        with RouterOSClient(session.router) as client:
            hs_service = HotspotService(client.api, session.router)
            if hs_service.delete_user(session.device.mac_address):
                session.is_active = False
                session.save()
                logger.info(f"Session {session_id} deactivated on expiry.")
    except Exception as e:
        logger.error(f"Failed to deactivate session {session_id}: {e}")

@shared_task
def reconcile_pending_payments():
    """Checks for PENDING transactions and queries Safaricom for status."""
    five_minutes_ago = timezone.now() - timezone.timedelta(minutes=5)
    pending_transactions = Transaction.objects.filter(
        status='PENDING',
        created_at__lte=five_minutes_ago
    )
    
    from .mpesa import MpesaClient
    mpesa = MpesaClient()
    for tx in pending_transactions:
        try:
            result = mpesa.query_stk_status(tx.checkout_request_id)
            if not result:
                continue
                
            result_code = str(result.get('ResultCode'))
            if result_code == '0':
                tx.status = 'COMPLETED'
                tx.save()
                activate_internet_session.delay(tx.id)
            elif result_code in ['1032', '1037', '1']: 
                tx.status = 'FAILED'
                tx.result_description = result.get('ResultDesc')
                tx.save()
        except Exception as e:
            logger.error(f"Reconciliation failed for {tx.checkout_request_id}: {e}")
