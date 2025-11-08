from apps.controllers.club_controller import ClubController
from apps.core.models import ClubApplication, Club

class StudentPortalFacade:
    def __init__(self, club_controller: ClubController | None = None):
        self.ctrl = club_controller or ClubController()

    def create_club_application(self, student_id: int, club_data: dict) -> ClubApplication:
        return self.ctrl.create_club_app(student_id, club_data)

    def view_clubs(self) -> list[Club]:
        return list(self.ctrl.view_clubs())

    def view_club_details(self, club_id: int) -> Club:
        return self.ctrl.view_club_page(club_id)