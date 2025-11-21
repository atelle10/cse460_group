from django.shortcuts import render, redirect
from django.views import View
from apps.core.models import Student, Admin, ClubLeader, Club
from apps.facades.student_portal_facade import StudentPortalFacade
from apps.facades.admin_facade import AdminFacade
from apps.facades.club_mgmt_facade import ClubMgmtFacade

"""This file defines the views """

class AuthView(View):
    def get(self, request, action=None):
        if action == 'logout':
            request.session.flush()
            return redirect('login')

        return render(request, 'auth/login.html')

    def post(self, request, action=None):
        if action == 'logout':
            request.session.flush()
            return redirect('login')

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            admin = Admin.objects.get(username=username, password=password)
            request.session['user_id'] = admin.user_id
            request.session['user_type'] = 'admin'
            request.session['username'] = admin.username
            request.session['first_name'] = admin.first_name
            request.session['last_name'] = admin.last_name
            return redirect('admin_dashboard')
        except Admin.DoesNotExist:
            pass

        try:
            student = Student.objects.get(username=username, password=password)
            request.session['user_id'] = student.user_id
            request.session['user_type'] = 'student'
            request.session['username'] = student.username
            request.session['first_name'] = student.first_name
            request.session['last_name'] = student.last_name
            return redirect('student_home')
        except Student.DoesNotExist:
            pass

        return render(request, 'auth/login.html', {
            'error': 'Invalid username or password'
        })

class RegistrationView(View):
    def get(self, request):
        return render(request, 'auth/register.html')

    def post(self, request):
        data = {
            'username': request.POST.get('username', '').strip(),
            'password': request.POST.get('password', '').strip(),
            'confirm': request.POST.get('password', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'first_name': request.POST.get('first_name', '').strip(),
            'last_name': request.POST.get('last_name', '').strip(),
            'major': request.POST.get('major', '').strip(),
            'college_year': request.POST.get('college_year') or None,
        }

        if data['password'] != data['confirm']:
            return render(request, 'auth/register.html', {'error': 'Passwords do not match', **data})
        
        if Student.objects.filter(username=data['username']).exists():
            return render(request, 'auth/register.html', {'error': 'Username already taken', **data})
        
        student = Student.objects.create(
            username=data['username'],
            password=data['password'],  # TODO: hash later
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            major=data['major'],
            college_year=data['college_year'] or None,
            topics_of_interest=[],
        )

        request.session['user_id'] = student.user_id
        request.session['user_type'] = 'student'
        request.session['username'] = student.username
        request.session['first_name'] = student.first_name
        request.session['last_name'] = student.last_name
        return redirect('student_home')

class StudentPortalView(View):

    facade = StudentPortalFacade()
    club_mgmt_facade = ClubMgmtFacade()

    def get(self, request, club_id=None, event_id=None):
        if request.session.get('user_type') != 'student':
            return redirect('login')

        if event_id:
            try:
                event = self.facade.view_event(event_id)
                return render(request, 'portal/event_detail.html', {
                    'event': event,
                    'username': request.session.get('username')
                })
            except ValueError as e:
                clubs = self.facade.view_clubs()
                user_id = request.session.get('user_id')
                student = Student.objects.get(user_id=user_id)
                is_club_leader = ClubLeader.objects.filter(username=student.username + "_leader").exists()
                return render(request, 'portal/student_home.html', {
                    'clubs': clubs,
                    'username': request.session.get('username'),
                    'is_club_leader': is_club_leader,
                    'error': str(e)
                })

        if club_id:
            club = self.facade.view_club_details(club_id)
            student_id = request.session.get('user_id')
            membership_status = self.facade.get_membership_status(student_id, club_id)
            club_events = self.facade.search_events({'club_id': club_id})
            return render(request, 'portal/club_detail.html', {
                'club': club,
                'club_events': club_events,
                'username': request.session.get('username'),
                'membership_status': membership_status
            })

        action = request.GET.get('action')
        if action == 'apply':
            return render(request, 'portal/club_application_form.html', {
                'username': request.session.get('username')
            })

        clubs = self.facade.view_clubs()
        events = self.facade.view_events()
        user_id = request.session.get('user_id')
        student = Student.objects.get(user_id=user_id)
        is_club_leader = ClubLeader.objects.filter(username=student.username + "_leader").exists()

        return render(request, 'portal/student_home.html', {
            'clubs': clubs,
            'events': events,
            'username': request.session.get('username'),
            'is_club_leader': is_club_leader
        })

    def post(self, request):
        if request.session.get('user_type') != 'student':
            return redirect('login')

        student_id = request.session.get('user_id')
        action = request.POST.get('action')
        
        if action == 'join_club':
            club_id = int(request.POST.get('club_id'))
            try:
                self.facade.join_club(student_id, int(club_id))
                club = self.facade.view_club_details(int(club_id))
                
                membership_status = self.facade.get_membership_status(student_id, int(club_id))
                
                return render(request, 'portal/club_detail.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'membership_status': membership_status,
                    'success': 'Club join request submitted successfully!'
                })
                
            except ValueError as e:
                club = self.facade.view_club_details(int(club_id))
                membership_status = self.facade.get_membership_status(student_id, int(club_id))
                return render(request, 'portal/club_detail.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'membership_status': membership_status,
                    'error': str(e)
                })
                
        
        club_data = {
            'name': request.POST.get('club_name'),
            'description': request.POST.get('description'),
            'location': request.POST.get('location'),
            'categories': [cat.strip() for cat in request.POST.get('categories', '').split(',') if cat.strip()]
        }

        try:
            self.club_mgmt_facade.create_new_club(student_id, club_data)

            user_id = request.session.get('user_id')
            student = Student.objects.get(user_id=user_id)
            is_club_leader = ClubLeader.objects.filter(username=student.username + "_leader").exists()

            return render(request, 'portal/student_home.html', {
                'success': 'Club application submitted successfully!',
                'clubs': self.facade.view_clubs(),
                'username': request.session.get('username'),
                'is_club_leader': is_club_leader
            })
        except ValueError as e:
            return render(request, 'portal/club_application_form.html', {
                'error': str(e),
                'username': request.session.get('username')
            })



class ClubLeaderView(View):
    
    club_mgmt_facade = ClubMgmtFacade()
    
    def get(self, request):
        if request.session.get('user_type') != 'student':
            return redirect('login')

        username = request.session.get('username')

        try:
            club_leader = ClubLeader.objects.get(username=username + "_leader")
        except ClubLeader.DoesNotExist:
            return redirect('student_home')

        try:
            club = Club.objects.get(club_leader=club_leader)
            pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
            announcements = self.club_mgmt_facade.view_announcements(club.club_id)
            
        except Club.DoesNotExist:
            club = None
            pending_requests = []
            announcements = []

        return render(request, 'club_leader/dashboard.html', {
            'club': club,
            'username': request.session.get('username'),
            'club_leader': club_leader,
            'pending_requests': pending_requests,
            'announcements': announcements
        })

    def post(self, request):
        if request.session.get('user_type') != 'student':
            return redirect('login')

        username = request.session.get('username')
        
        try:
            club_leader = ClubLeader.objects.get(username=username + "_leader")
        except ClubLeader.DoesNotExist:
            return redirect('student_home')

        try:
            club = Club.objects.get(club_leader=club_leader)
        except Club.DoesNotExist:
            return redirect('club_leader_dashboard')

        action = request.POST.get('action')

        if action == 'edit_club':
            club_data = {
                'name': request.POST.get('club_name'),
                'description': request.POST.get('description'),
                'location': request.POST.get('location'),
                'categories': [cat.strip() for cat in request.POST.get('categories', '').split(',') if cat.strip()]
            }

            try:
                self.club_mgmt_facade.edit_club_details(club.club_id, club_leader.user_id, club_data)
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                club = Club.objects.get(club_id=club.club_id)
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'success': 'Club details updated successfully!'
                })
            except ValueError as e:
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'error': str(e)
                })

        if action == 'post_announcement':
            message = request.POST.get('message')
            if not message or not message.strip():
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'error': 'Announcement message cannot be empty'
                })
            
            try:
                self.club_mgmt_facade.post_announcement(club.club_id, club_leader.user_id, message)
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'success': 'Announcement posted successfully!'
                })
            except ValueError as e:
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'error': str(e)
                })
        
        membership_id = request.POST.get('membership_id')
        
        try:
            if action == 'approve':
                self.club_mgmt_facade.approve_member(int(membership_id))
                message = 'Member approved successfully!'
                
            elif action == 'reject':
                self.club_mgmt_facade.deny_member(int(membership_id))
                message = 'Member request rejected'
            else:
                message = 'Invalid action'

            pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
            
            
            announcements = self.club_mgmt_facade.view_announcements(club.club_id)

            return render(request, 'club_leader/dashboard.html', {
                'club': club,
                'username': request.session.get('username'),
                'club_leader': club_leader,
                'pending_requests': pending_requests,
                'announcements': announcements,
                'success': message
            })

        except ValueError as e:
            pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
            announcements = self.club_mgmt_facade.view_announcements(club.club_id)
            
            return render(request, 'club_leader/dashboard.html', {
                'club': club,
                'username': request.session.get('username'),
                'club_leader': club_leader,
                'pending_requests': pending_requests,
                'announcements': announcements,
                'error': str(e)
            })



class AdminDashboardView(View):

    facade = AdminFacade()

    def get(self, request):
        if request.session.get('user_type') != 'admin':
            return redirect('login')

        view_type = request.GET.get('view')

        if view_type == 'flagged':
            return render(request, 'admin/flagged_content.html', {
                'username': request.session.get('username'),
                'flagged_items': []
            })

        pending_applications = self.facade.view_pending_applications()
        clubs = self.facade.view_clubs()

        return render(request, 'admin/dashboard.html', {
            'pending_applications': pending_applications,
            'clubs': clubs,
            'username': request.session.get('username')
        })

    def post(self, request):
        if request.session.get('user_type') != 'admin':
            return redirect('login')

        action = request.POST.get('action')
        application_id = request.POST.get('application_id')

        if action == 'approve':
            self.facade.approve_club(int(application_id))
            message = 'Club application approved successfully'
        elif action == 'reject':
            self.facade.deny_club(int(application_id))
            message = 'Club application rejected'
        else:
            message = 'Invalid'

        pending_applications = self.facade.view_pending_applications()
        clubs = self.facade.view_clubs()

        return render(request, 'admin/dashboard.html', {
            'pending_applications': pending_applications,
            'clubs': clubs,
            'username': request.session.get('username'),
            'success': message
        })
