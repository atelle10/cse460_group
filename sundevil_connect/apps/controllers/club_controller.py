from typing import Dict
from django.db.models import QuerySet
from apps.core.models import ClubApplication, Student, Club
from apps.core.models import Membership


""" This file defines the club controller that will handle all logic for clubs"""
class ClubController:
    def create_club_app(self, student_id: int, payload: Dict) -> ClubApplication:
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

    def edit_club_details(self, club_id: int, payload: Dict) -> Club:
        pass

    def post_announcement(self, club_id: int, leader_id: int, message: str):
        pass

    def view_club_page(self, club_id: int) -> Club:
        return Club.objects.get(club_id=club_id)

    def view_announcements(self):
        pass

    def view_clubs(self) -> QuerySet[Club]:
        return Club.objects.filter(is_active=True).order_by('name')
 
    
    