from typing import Dict
from django.db.models import QuerySet
from apps.core.models import ClubApplication, Student, Club, ClubLeader, Announcement
from apps.core.models import Membership, Admin


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

        # Notify
        admin_emails = [admin.email for admin in Admin.objects.all()]
        ClubApplication.notify_observers('CLUB_APPLICATION_CREATED', {
            'admin_emails': admin_emails,
            'club_name': payload.get('name', 'Unknown Club')
        })

        return application

    def edit_club_details(self, club_id: int, leader_id: int, payload: Dict) -> Club:
        try:
            club = Club.objects.get(club_id=club_id)
            leader = ClubLeader.objects.get(user_id=leader_id)

            if club.club_leader != leader:
                raise ValueError("Only the club leader can edit club details")

            if 'name' in payload and payload['name']:
                club.name = payload['name']
            if 'description' in payload and payload['description']:
                club.description = payload['description']
            if 'location' in payload and payload['location']:
                club.location = payload['location']
            if 'categories' in payload:
                club.categories = payload['categories']

            club.save()
            return club

        except Club.DoesNotExist:
            raise ValueError("Club does not exist")
        except ClubLeader.DoesNotExist:
            raise ValueError("Club leader does not exist")

    def post_announcement(self, club_id: int, leader_id: int, message: str):
        try:
            club = Club.objects.get(club_id=club_id)
            leader = ClubLeader.objects.get(user_id=leader_id)
            
            if club.club_leader != leader:
                raise ValueError("Only the club leader can post announcements")
            
            announcement = Announcement.objects.create(
                club=club,
                creator=leader,
                message=message
            )
            
            return announcement
            
        except Club.DoesNotExist:
            raise ValueError("Club does not exist")
        except ClubLeader.DoesNotExist:
            raise ValueError("Club leader does not exist")

    def view_club_page(self, club_id: int) -> Club:
        return Club.objects.get(club_id=club_id)

    def view_announcements(self, club_id: int) -> QuerySet[Announcement]:
        return Announcement.objects.filter(club_id=club_id).select_related('creator')

    def view_clubs(self) -> QuerySet[Club]:
        return Club.objects.filter(is_active=True).order_by('name')
 
    
    