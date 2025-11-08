from apps.controllers.admin_controller import AdminController
from apps.core.models import ClubApplication, Club


class AdminFacade:
    def __init__(self, admin_controller: AdminController | None = None):
        self.ctrl = admin_controller or AdminController()

    def view_pending_applications(self) -> list[ClubApplication]:
        return list(ClubApplication.objects.filter(status='PENDING').order_by('-created_at'))

    def approve_club(self, application_id: int) -> bool:
        return self.ctrl.approve_club(application_id)

    def deny_club(self, application_id: int, reason: str = "") -> bool:
        return self.ctrl.reject_club(application_id, reason)

    def view_clubs(self) -> list[Club]:
        return list(Club.objects.filter(is_active=True).order_by('name'))