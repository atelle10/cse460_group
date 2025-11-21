from datetime import datetime
from django.utils import timezone
from apps.core.models import Event, Club, ClubLeader

class EventController:

    def create_event(self, club_id: int, leader_id: int, payload: dict) -> Event:
        try:
            club = Club.objects.get(club_id=club_id)
        except Club.DoesNotExist:
            raise ValueError("Club does not exist")

        try:
            leader = ClubLeader.objects.get(user_id=leader_id)
        except ClubLeader.DoesNotExist:
            raise ValueError("Club leader not found")

        if club.club_leader != leader:
            raise ValueError("Only the club leader can create events")

        title = (payload.get('title') or '').strip()
        description = (payload.get('description') or '').strip()
        location = (payload.get('location') or '').strip()
        start_time_raw = payload.get('start_time')
        end_time_raw = payload.get('end_time')
        is_free_flag = payload.get('is_free')
        cost_raw = payload.get('cost')
        capacity_raw = payload.get('capacity')

        if not title or not description or not location or not start_time_raw or not end_time_raw:
            raise ValueError("Title, description, location, start time, and end time are required")

        try:
            start_time = datetime.fromisoformat(start_time_raw)
            end_time = datetime.fromisoformat(end_time_raw)
        except (ValueError, TypeError):
            raise ValueError("Invalid date format. Please use the date/time picker.")

        # Make datetimes timezone-aware if they are naïve
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
        if timezone.is_naive(end_time):
            end_time = timezone.make_aware(end_time, timezone.get_current_timezone())

        if end_time <= start_time:
            raise ValueError("End time must be after start time")

        is_free = str(is_free_flag).lower() in ['true', '1', 'on', 'yes']
        if not is_free:
            try:
                cost = float(cost_raw)
            except (TypeError, ValueError):
                raise ValueError("Cost must be a number")
            if cost < 0:
                raise ValueError("Cost cannot be negative")
        else:
            cost = 0

        capacity = None
        if capacity_raw not in [None, '', 'None']:
            try:
                capacity_val = int(capacity_raw)
            except (TypeError, ValueError):
                raise ValueError("Capacity must be an integer")
            if capacity_val <= 0:
                raise ValueError("Capacity must be greater than zero")
            capacity = capacity_val

        return Event.objects.create(
            club=club,
            title=title,
            description=description,
            location=location,
            start_time=start_time,
            end_time=end_time,
            is_free=is_free,
            cost=cost,
            capacity=capacity
        )
    
    def update_event(self, event_id: int, payload: dict):
        pass
    
    def delete_event(self, event_id: int, leader_id: int) -> bool:
        try:
            event = Event.objects.select_related('club__club_leader').get(event_id=event_id)
        except Event.DoesNotExist:
            raise ValueError("Event does not exist")

        club = event.club
        if not club.club_leader or club.club_leader.user_id != leader_id:
            raise ValueError("Only the club leader can delete events")

        event.delete()
        return True
    
    def register_for_event(self, student_id: int, event_id: int):
        pass
    
    def cancel_registration(self, student_id: int, event_id: int) -> bool:
        pass
    
    def check_in(self, registration_id: int):
        pass
