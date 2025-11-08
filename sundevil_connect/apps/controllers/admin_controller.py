from django.utils import timezone
from apps.core.models import ClubApplication, Club, ClubLeader, Student


""" This file defines the admin controller that will handle all logic for admins"""
class AdminController:
    def review_club_application(self, application_id: int) -> ClubApplication:
        return ClubApplication.objects.get(application_id=application_id)

    def approve_club(self, application_id: int) -> bool:
        application = ClubApplication.objects.get(application_id=application_id)
        student = application.student

        
        # If the student already exists as a club leader, use that account
        try:
            club_leader = ClubLeader.objects.get(username=student.username)
        except ClubLeader.DoesNotExist:
            club_leader = ClubLeader.objects.create(
                #temp fix for username conflict
                username=student.username + "_leader",
                password=student.password,
                email=student.email,
                first_name=student.first_name,
                last_name=student.last_name,
                privacy_level=student.privacy_level,
                topics_of_interest=student.topics_of_interest,
                major=student.major,
                college_year=student.college_year,
                title="Founder",
                leader_start_date=timezone.now().date()
            )

        club = Club.objects.create(
            name=application.metadata['name'],
            description=application.metadata['description'],
            location=application.metadata['location'],
            categories=application.metadata.get('categories', []),
            is_active=True,
            members_count=1,
            leaders_count=1,
            club_leader=club_leader
        )

        application.status = 'APPROVED'
        application.is_approved = True
        application.save()

        return True

    def reject_club(self, application_id: int, reason: str) -> bool:
        application = ClubApplication.objects.get(application_id=application_id)

        application.status = 'REJECTED'
        application.is_approved = False
        application.save()

        return True

    def review_flag(self, flag_id: int):
        pass

    def resolve_flag(self, flag_id: int, decision: int) -> bool:
        pass