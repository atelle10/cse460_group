from apps.core.models import Student, Membership, Club

class MembershipController:
    
    def join_club(self, student_id: int, club_id: int) -> Membership:
        try:
            student = Student.objects.get(user_id=student_id)
            club = Club.objects.get(club_id=club_id)
            
            existing_membership = Membership.objects.filter(
                student=student,
                club=club
            ).first()
            
            if existing_membership:
                if existing_membership.status == 'APPROVED':
                    raise ValueError("Student is already a member of the club")
                elif existing_membership.status == 'PENDING':
                    raise ValueError("Membership request is already pending")
                elif existing_membership.status == 'REJECTED':
                    raise ValueError("Membership request was rejected previously")
            
            membership = Membership.objects.create(
                student=student,
                club=club,
                status='PENDING'
            )
            return membership
        except Student.DoesNotExist:
            raise ValueError("Student does not exist")
        except Club.DoesNotExist:
            raise ValueError("Club does not exist")
        
    
    def get_membership_status(self, student_id: int, club_id: int):
            membership = Membership.objects.filter(
                student_id=student_id,
                club_id=club_id
            ).first()
            
            if membership:
                return membership.status
            return None

    def view_membership(self, membership_id: int):
        try:
            membership = Membership.objects.select_related('student', 'club').get(
                membership_id=membership_id
            )
            return membership
        except Membership.DoesNotExist:
            raise ValueError("Membership not found")
    
    def approve_member(self, membership_id: int):
        try:
            membership = Membership.objects.get(membership_id=membership_id)
            membership.approve()
            return membership
        except Membership.DoesNotExist:
            raise ValueError("Membership request not found")
    
    def reject_member(self, membership_id: int):
        try:
            membership = Membership.objects.get(membership_id=membership_id)
            membership.reject()
            return membership
        except Membership.DoesNotExist:
            raise ValueError("Membership request not found")
    
    def remove_member(self, membership_id: int):
        try:
            membership = Membership.objects.get(membership_id=membership_id)
            if membership.status == 'APPROVED':
                membership.club.members_count -= 1
                membership.club.save()
            membership.delete()
            return True
        except Membership.DoesNotExist:
            raise ValueError("Membership not found")
    
    def get_pending_requests(self, club_id: int):
        return Membership.objects.filter(
            club_id=club_id,
            status='PENDING'
        ).select_related('student')
    
    def get_approved_members(self, club_id: int):
        return Membership.objects.filter(
            club_id=club_id,
            status='APPROVED'
        ).select_related('student')
    
    def review_memberships(self, club_id: int):
        return Membership.objects.filter(
            club_id=club_id
        ).select_related('student').order_by('-joined_at')