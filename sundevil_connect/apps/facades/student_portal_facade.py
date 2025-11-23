from apps.controllers.club_controller import ClubController
from apps.controllers.membership_controller import MembershipController
from apps.controllers.search_controller import SearchController
from apps.controllers.event_controller import EventController
from apps.core.models import Club, Membership, Event, Registration, Student

"""Student portal facade that uses the club controller (for now)"""
class StudentPortalFacade:
    def __init__(self, club_controller: ClubController | None = None):
        self.ctrl = club_controller or ClubController()
        self.membership_controller = MembershipController()
        self.search_ctrl = SearchController()
        self.event_ctrl = EventController() 

    def view_clubs(self) -> list[Club]:
        return list(self.ctrl.view_clubs())

    def view_club_details(self, club_id: int) -> Club:
        return self.ctrl.view_club_page(club_id)
    
    def join_club(self, student_id: int, club_id: int) -> Membership:
        return self.membership_controller.join_club(student_id, club_id)
    
    def get_membership_status(self, student_id: int, club_id: int) -> str:
        return self.membership_controller.get_membership_status(student_id, club_id)
    
    def search_clubs(self, query: str) -> list[Club]:
        all_clubs = self.ctrl.view_clubs()
        filtered_clubs = all_clubs.filter(name__icontains=query)
        return list(filtered_clubs)
    
    def search_events(self, filter_payload) -> list[Club]:
        return self.search_ctrl.search_events(filter_payload)

    def view_events(self) -> list[Event]:
        return list(Event.objects.filter(status='UPCOMING').select_related('club').order_by('start_time'))

    def view_event(self, event_id: int):
        try:
            return Event.objects.select_related('club').get(event_id=event_id)
        except Event.DoesNotExist:
            raise ValueError("Event does not exist.")

    def register_for_event(self, student_id: int, event_id: int) -> Registration:
        return self.event_ctrl.register_for_event(student_id, event_id)

    def cancel_registration(self, student_id: int, event_id: int) -> bool:
        return self.event_ctrl.cancel_registration(student_id, event_id)

    def get_registration_status(self, student_id: int, event_id: int) -> str:
        try:
            student = Student.objects.get(user_id=student_id)
            event = Event.objects.get(event_id=event_id)
            registration = Registration.objects.get(student=student, event=event)
            return registration.status
        except (Student.DoesNotExist, Event.DoesNotExist, Registration.DoesNotExist):
            return 'NOT_REGISTERED'
