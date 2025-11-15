from apps.controllers.club_controller import ClubController
from apps.controllers.membership_controller import MembershipController
from apps.core.models import ClubApplication, Club, Membership


"""Student portal facade that uses the club controller (for now)"""
class StudentPortalFacade:
    def __init__(self, club_controller: ClubController | None = None):
        self.ctrl = club_controller or ClubController()

    def create_club_application(self, student_id: int, club_data: dict) -> ClubApplication:
        return self.ctrl.create_club_app(student_id, club_data)

    def view_clubs(self) -> list[Club]:
        return list(self.ctrl.view_clubs())

    def view_club_details(self, club_id: int) -> Club:
        return self.ctrl.view_club_page(club_id)
    
    def join_club(self, student_id: int, club_id: int) -> Membership:
        controller = MembershipController()
        return controller.join_club(student_id, club_id)
    
    def get_membership_status(self, student_id: int, club_id: int) -> str:
        controller = MembershipController()
        return controller.get_membership_status(student_id, club_id)
    
    def search_clubs(self, query: str) -> list[Club]:
        all_clubs = self.ctrl.view_clubs()
        filtered_clubs = all_clubs.filter(name__icontains=query)
        return list(filtered_clubs)
    
    def search_events(self, query: str) -> list[Club]:
        pass
    
    def register_for_event(self, student_id: int, event_id: int):
        pass
    

    