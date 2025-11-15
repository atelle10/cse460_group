from apps.controllers.membership_controller import MembershipController
from apps.controllers.club_controller import ClubController
from apps.core.models import Membership, Club, ClubApplication

"""Club leader portal facade that uses the club controller and membership controller"""
class ClubMgmtFacade:
    
    def __init__(self):
        self.membership_ctrl = MembershipController()
        self.club_ctrl = ClubController()
    
    def review_memberships(self, club_id: int) -> list[Membership]:
        return self.membership_ctrl.review_memberships(club_id)
    
    def approve_member(self, membership_id: int) -> Membership:
        return self.membership_ctrl.approve_member(membership_id)
    
    def deny_member(self, membership_id: int) -> Membership:
        return self.membership_ctrl.reject_member(membership_id)
    
    def suspend_member(self, membership_id: int) -> None:
        return self.membership_ctrl.suspend_member(membership_id)
    
    def remove_member(self, membership_id: int) -> bool:
        return self.membership_ctrl.remove_member(membership_id)
    
    def create_new_club(self, student_id: int, club_data: dict) -> ClubApplication:
        return self.club_ctrl.create_club_app(student_id, club_data)

    def edit_club_details(self, club_id: int, new_data: dict) -> Club:
        return self.club_ctrl.edit_club_details(club_id, new_data)

    def post_announcement(self, club_id: int, leader_id: int, message: str):
        pass
    
    def delete_event(self, event_id: int) -> bool:
        pass
    
    def create_event(self, club_id: int, event_data: dict):
        pass