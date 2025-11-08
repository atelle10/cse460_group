from django.db.models import QuerySet
from apps.core.models import ClubApplication, Student, Club

class ClubController:
    def create_club_app(self, student_id: int, payload: dict) -> ClubApplication:
        student = Student.objects.get(user_id=student_id)
        
        existing = ClubApplication.objects.filter(
            student=student,
            status='PENDING'
        ).exists()
        if existing:
            raise ValueError("Student already has a pending application")
        
        application = ClubApplication.objects.create(
            student=student,
            metadata=payload,
            status='PENDING',
            is_approved=None
        )
        
        return application

    def view_clubs(self) -> QuerySet[Club]:
        return Club.objects.filter(is_active=True).order_by('name')

    def view_club_page(self, club_id: int) -> Club:
        return Club.objects.get(club_id=club_id)
    