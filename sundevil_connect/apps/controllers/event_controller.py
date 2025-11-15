from apps.core.models import Event, Club

class EventController:
    
    def create_event(self, club_id: int, payload: dict):
        pass
    
    def update_event(self, event_id: int, payload: dict):
        pass
    
    def delete_event(self, event_id: int) -> bool:
        pass
    
    def register_for_event(self, student_id: int, event_id: int):
        pass
    
    def cancel_registration(self, student_id: int, event_id: int) -> bool:
        pass
    
    def check_in(self, registration_id: int):
        pass