from datetime import datetime
from django.utils import timezone
from apps.core.models import Event, Club, ClubLeader, Student, Registration, Membership

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
        event_type = payload.get('event_type', 'IN_PERSON')
        capacity_raw = payload.get('capacity')

        if not title or not description or not location or not start_time_raw or not end_time_raw:
            raise ValueError("Title, description, location, start time, and end time are required")

        if event_type not in ['IN_PERSON', 'VIRTUAL']:
            raise ValueError("Invalid event type")

        try:
            start_time = datetime.fromisoformat(start_time_raw)
            end_time = datetime.fromisoformat(end_time_raw)
        except (ValueError, TypeError):
            raise ValueError("Invalid date format. Please use the date/time picker.")

        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
        if timezone.is_naive(end_time):
            end_time = timezone.make_aware(end_time, timezone.get_current_timezone())

        if end_time <= start_time:
            raise ValueError("End time must be after start time")

        capacity = None
        if capacity_raw not in [None, '', 'None']:
            try:
                capacity_val = int(capacity_raw)
            except (TypeError, ValueError):
                raise ValueError("Capacity must be an integer")
            if capacity_val <= 0:
                raise ValueError("Capacity must be greater than zero")
            capacity = capacity_val

        event = Event.objects.create(
            club=club,
            title=title,
            description=description,
            location=location,
            start_time=start_time,
            end_time=end_time,
            event_type=event_type,
            is_free=True,
            cost=0,
            capacity=capacity
        )

        # Notify
        member_emails = [m.student.email for m in Membership.objects.filter(club=club, status='APPROVED').select_related('student')]
        Event.notify_observers('EVENT_CREATED', {
            'member_emails': member_emails,
            'event_title': event.title,
            'event_date': event.start_time.strftime('%B %d, %Y')
        })

        return event
    
    def update_event(self, event_id: int, payload: dict) -> Event:
        try:
            event = Event.objects.select_related('club__club_leader').get(event_id=event_id)
        except Event.DoesNotExist:
            raise ValueError("Event does not exist")

        title = (payload.get('title') or '').strip()
        description = (payload.get('description') or '').strip()
        location = (payload.get('location') or '').strip()
        start_time_raw = payload.get('start_time')
        end_time_raw = payload.get('end_time')
        event_type = payload.get('event_type', event.event_type)
        capacity_raw = payload.get('capacity')

        if not title or not description or not location or not start_time_raw or not end_time_raw:
            raise ValueError("Title, description, location, start time, and end time are required")

        if event_type not in ['IN_PERSON', 'VIRTUAL']:
            raise ValueError("Invalid event type")

        try:
            start_time = datetime.fromisoformat(start_time_raw)
            end_time = datetime.fromisoformat(end_time_raw)
        except (ValueError, TypeError):
            raise ValueError("Invalid date format. Please use the date/time picker.")

        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time, timezone.get_current_timezone())
        if timezone.is_naive(end_time):
            end_time = timezone.make_aware(end_time, timezone.get_current_timezone())

        if end_time <= start_time:
            raise ValueError("End time must be after start time")

        capacity = None
        if capacity_raw not in [None, '', 'None']:
            try:
                capacity_val = int(capacity_raw)
            except (TypeError, ValueError):
                raise ValueError("Capacity must be an integer")
            if capacity_val <= 0:
                raise ValueError("Capacity must be greater than zero")
            if capacity_val < event.registered_count:
                raise ValueError(f"Capacity cannot be less than current registrations ({event.registered_count})")
            capacity = capacity_val

        event.title = title
        event.description = description
        event.location = location
        event.start_time = start_time
        event.end_time = end_time
        event.event_type = event_type
        event.capacity = capacity
        event.save()

        # Notify
        member_emails = [m.student.email for m in Membership.objects.filter(club=event.club, status='APPROVED').select_related('student')]
        Event.notify_observers('EVENT_UPDATED', {
            'member_emails': member_emails,
            'event_title': event.title
        })

        return event
    
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
    
    def register_for_event(self, student_id: int, event_id: int) -> Registration:
        try:
            student = Student.objects.get(user_id=student_id)
        except Student.DoesNotExist:
            raise ValueError("Student not found")

        try:
            event = Event.objects.get(event_id=event_id)
        except Event.DoesNotExist:
            raise ValueError("Event not found")

        if event.status == 'CANCELLED':
            raise ValueError("Cannot register for a cancelled event")

        if event.at_capacity():
            raise ValueError("Event is at full capacity")

        if Registration.objects.filter(student=student, event=event, status='REGISTERED').exists():
            raise ValueError("Already registered for this event")

        registration = Registration.objects.create(
            student=student,
            event=event,
            status='REGISTERED',
            payment_status='NOT_REQUIRED'
        )
        registration.confirm()

        # Notify
        if event.club.club_leader:
            Registration.notify_observers('EVENT_REGISTRATION', {
                'club_leader_email': event.club.club_leader.email,
                'student_name': f"{student.first_name} {student.last_name}",
                'event_title': event.title
            })

        return registration

    def cancel_registration(self, student_id: int, event_id: int) -> bool:
        try:
            student = Student.objects.get(user_id=student_id)
        except Student.DoesNotExist:
            raise ValueError("Student not found")

        try:
            event = Event.objects.get(event_id=event_id)
        except Event.DoesNotExist:
            raise ValueError("Event not found")

        try:
            registration = Registration.objects.get(student=student, event=event, status='REGISTERED')
        except Registration.DoesNotExist:
            raise ValueError("No active registration found for this event")

        registration.cancel()
        return True