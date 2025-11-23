from django.shortcuts import render, redirect
from django.views import View
from apps.core.models import Student, Admin, ClubLeader, Club, Membership, Event, Flag, User, Announcement, Registration
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
        user_type = request.session.get('user_type')
        if user_type not in ['student', 'admin']:
            return redirect('login')

        if event_id:
            try:
                event = self.facade.view_event(event_id)
                student_id = request.session.get('user_id')
                registration_status = 'NOT_REGISTERED'
                if user_type == 'student':
                    registration_status = self.facade.get_registration_status(student_id, event_id)

                registered_members = Registration.objects.filter(
                    event_id=event_id,
                    status='REGISTERED'
                ).select_related('student')[:50]

                return render(request, 'portal/event_detail.html', {
                    'event': event,
                    'username': request.session.get('username'),
                    'registration_status': registration_status,
                    'user_type': user_type,
                    'registered_members': registered_members
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
            club_members = []
            user_type = request.session.get('user_type')
            if membership_status == 'APPROVED' or user_type == 'admin':
                club_members = self.club_mgmt_facade.get_club_members(club_id, limit=1000)
            approved_count = Membership.objects.filter(club_id=club_id, status='APPROVED').count()
            return render(request, 'portal/club_detail.html', {
                'club': club,
                'club_events': club_events,
                'username': request.session.get('username'),
                'membership_status': membership_status,
                'club_members': club_members,
                'approved_members_count': approved_count,
                'user_type': user_type
            })

        action = request.GET.get('action')
        if action == 'apply':
            return render(request, 'portal/club_application_form.html', {
                'username': request.session.get('username')
            })

        clubs = self.facade.view_clubs()

        search_query = request.GET.get('search', '')
        filter_location = request.GET.get('location', '')
        sort_by = request.GET.get('sort', 'date_asc')

        filter_payload = {}
        if search_query:
            filter_payload['query'] = search_query
        if filter_location:
            filter_payload['location'] = filter_location
        filter_payload['sort'] = sort_by

        events = self.facade.search_events(filter_payload) if filter_payload else self.facade.view_events()

        user_id = request.session.get('user_id')
        student = Student.objects.get(user_id=user_id)
        is_club_leader = ClubLeader.objects.filter(username=student.username + "_leader").exists()
        my_clubs = [
            membership.club for membership in
            Membership.objects.filter(student_id=user_id, status='APPROVED').select_related('club')
        ]
        my_club_ids = {club.club_id for club in my_clubs}
        available_clubs = [club for club in clubs if club.club_id not in my_club_ids]

        return render(request, 'portal/student_home.html', {
            'clubs': available_clubs,
            'events': events,
            'username': request.session.get('username'),
            'is_club_leader': is_club_leader,
            'my_clubs': my_clubs,
            'search_query': search_query,
            'filter_location': filter_location,
            'sort_by': sort_by
        })

    def post(self, request, club_id=None, event_id=None):
        user_type = request.session.get('user_type')
        if user_type not in ['student', 'admin']:
            return redirect('login')

        student_id = request.session.get('user_id')
        action = request.POST.get('action')

        if action == 'register' and event_id:
            try:
                self.facade.register_for_event(student_id, event_id)
                event = self.facade.view_event(event_id)
                registration_status = self.facade.get_registration_status(student_id, event_id)
                return render(request, 'portal/event_detail.html', {
                    'event': event,
                    'username': request.session.get('username'),
                    'registration_status': registration_status,
                    'user_type': request.session.get('user_type'),
                    'success': 'Successfully registered for event!'
                })
            except ValueError as e:
                event = self.facade.view_event(event_id)
                registration_status = self.facade.get_registration_status(student_id, event_id)
                return render(request, 'portal/event_detail.html', {
                    'event': event,
                    'username': request.session.get('username'),
                    'registration_status': registration_status,
                    'user_type': request.session.get('user_type'),
                    'error': str(e)
                })

        if action == 'flag_event' and event_id:
            reason = request.POST.get('reason', '').strip()
            if not reason:
                event = self.facade.view_event(event_id)
                registration_status = self.facade.get_registration_status(student_id, event_id)
                return render(request, 'portal/event_detail.html', {
                    'event': event,
                    'username': request.session.get('username'),
                    'registration_status': registration_status,
                    'user_type': request.session.get('user_type'),
                    'error': 'Please provide a reason for reporting this event'
                })
            try:
                event = Event.objects.get(event_id=event_id)
                user = User.objects.get(user_id=student_id)
                Flag.objects.create(
                    target='event',
                    creator=user,
                    event=event,
                    reason=reason,
                    severity_rank=1
                )
                event = self.facade.view_event(event_id)
                registration_status = self.facade.get_registration_status(student_id, event_id)
                return render(request, 'portal/event_detail.html', {
                    'event': event,
                    'username': request.session.get('username'),
                    'registration_status': registration_status,
                    'user_type': request.session.get('user_type'),
                    'success': 'Report submitted successfully. An admin will review it.'
                })
            except Exception as e:
                event = self.facade.view_event(event_id)
                registration_status = self.facade.get_registration_status(student_id, event_id)
                return render(request, 'portal/event_detail.html', {
                    'event': event,
                    'username': request.session.get('username'),
                    'registration_status': registration_status,
                    'user_type': request.session.get('user_type'),
                    'error': str(e)
                })

        if action == 'cancel_registration' and event_id:
            try:
                self.facade.cancel_registration(student_id, event_id)
                event = self.facade.view_event(event_id)
                registration_status = self.facade.get_registration_status(student_id, event_id)
                return render(request, 'portal/event_detail.html', {
                    'event': event,
                    'username': request.session.get('username'),
                    'registration_status': registration_status,
                    'user_type': request.session.get('user_type'),
                    'success': 'Registration cancelled successfully!'
                })
            except ValueError as e:
                event = self.facade.view_event(event_id)
                registration_status = self.facade.get_registration_status(student_id, event_id)
                return render(request, 'portal/event_detail.html', {
                    'event': event,
                    'username': request.session.get('username'),
                    'registration_status': registration_status,
                    'user_type': request.session.get('user_type'),
                    'error': str(e)
                })

        if action == 'delete_event' and event_id:
            if user_type != 'admin':
                return redirect('login')
            try:
                event = Event.objects.get(event_id=event_id)
                event.delete()
                return redirect('flagged_content')
            except Event.DoesNotExist:
                return redirect('flagged_content')

        if action == 'delete_announcement' and club_id:
            if user_type != 'admin':
                return redirect('login')
            announcement_id = request.POST.get('announcement_id')
            try:
                announcement = Announcement.objects.get(announcement_id=announcement_id)
                announcement.delete()
                return redirect('flagged_content')
            except Announcement.DoesNotExist:
                return redirect('flagged_content')

        if action == 'flag_announcement' and club_id:
            announcement_id = request.POST.get('announcement_id')
            reason = request.POST.get('reason', '').strip()
            user_type = request.session.get('user_type')
            if not reason:
                club = self.facade.view_club_details(club_id)
                membership_status = self.facade.get_membership_status(student_id, club_id)
                club_events = self.facade.search_events({'club_id': club_id})
                club_members = []
                if membership_status == 'APPROVED' or user_type == 'admin':
                    club_members = self.club_mgmt_facade.get_club_members(club_id, limit=1000)
                approved_count = Membership.objects.filter(club_id=club_id, status='APPROVED').count()
                return render(request, 'portal/club_detail.html', {
                    'club': club,
                    'club_events': club_events,
                    'username': request.session.get('username'),
                    'membership_status': membership_status,
                    'club_members': club_members,
                    'approved_members_count': approved_count,
                    'user_type': user_type,
                    'error': 'Please provide a reason for reporting'
                })
            try:
                announcement = Announcement.objects.get(announcement_id=announcement_id)
                user = User.objects.get(user_id=student_id)
                Flag.objects.create(
                    target='announcement',
                    creator=user,
                    announcement=announcement,
                    reason=reason,
                    severity_rank=1
                )
                club = self.facade.view_club_details(club_id)
                membership_status = self.facade.get_membership_status(student_id, club_id)
                club_events = self.facade.search_events({'club_id': club_id})
                club_members = []
                if membership_status == 'APPROVED' or user_type == 'admin':
                    club_members = self.club_mgmt_facade.get_club_members(club_id, limit=1000)
                approved_count = Membership.objects.filter(club_id=club_id, status='APPROVED').count()
                return render(request, 'portal/club_detail.html', {
                    'club': club,
                    'club_events': club_events,
                    'username': request.session.get('username'),
                    'membership_status': membership_status,
                    'club_members': club_members,
                    'approved_members_count': approved_count,
                    'user_type': user_type,
                    'success': 'Report submitted successfully'
                })
            except Exception as e:
                club = self.facade.view_club_details(club_id)
                membership_status = self.facade.get_membership_status(student_id, club_id)
                club_events = self.facade.search_events({'club_id': club_id})
                club_members = []
                if membership_status == 'APPROVED' or user_type == 'admin':
                    club_members = self.club_mgmt_facade.get_club_members(club_id, limit=1000)
                approved_count = Membership.objects.filter(club_id=club_id, status='APPROVED').count()
                return render(request, 'portal/club_detail.html', {
                    'club': club,
                    'club_events': club_events,
                    'username': request.session.get('username'),
                    'membership_status': membership_status,
                    'club_members': club_members,
                    'approved_members_count': approved_count,
                    'user_type': user_type,
                    'error': str(e)
                })

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
        action = request.GET.get('action')

        try:
            club_leader = ClubLeader.objects.get(username=username + "_leader")
        except ClubLeader.DoesNotExist:
            return redirect('student_home')

        try:
            club = Club.objects.get(club_leader=club_leader)
            pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
            approved_members = Membership.objects.filter(club=club, status='APPROVED').select_related('student').order_by('-approved_at')
            announcements = self.club_mgmt_facade.view_announcements(club.club_id)
            club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))

            if action == 'create_event':
                return render(request, 'club_leader/event_creation_form.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader
                })

            if action == 'edit_event':
                event_id = request.GET.get('event_id')
                try:
                    event = Event.objects.get(event_id=event_id, club=club)
                    return render(request, 'club_leader/event_edit_form.html', {
                        'event': event,
                        'club': club,
                        'username': request.session.get('username'),
                        'club_leader': club_leader
                    })
                except Event.DoesNotExist:
                    return redirect('club_leader_dashboard')

        except Club.DoesNotExist:
            club = None
            pending_requests = []
            approved_members = []
            announcements = []
            club_events = []

        return render(request, 'club_leader/dashboard.html', {
            'club': club,
            'username': request.session.get('username'),
            'club_leader': club_leader,
            'pending_requests': pending_requests,
            'approved_members': approved_members,
            'announcements': announcements,
            'club_events': club_events
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
                club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'club_events': club_events,
                    'success': 'Club details updated successfully!'
                })
            except ValueError as e:
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'club_events': club_events,
                    'error': str(e)
                })

        if action == 'post_announcement':
            message = request.POST.get('message')
            if not message or not message.strip():
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'club_events': club_events,
                    'error': 'Announcement message cannot be empty'
                })
            
            try:
                self.club_mgmt_facade.post_announcement(club.club_id, club_leader.user_id, message)
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'club_events': club_events,
                    'success': 'Announcement posted successfully!'
                })
            except ValueError as e:
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'club_events': club_events,
                    'error': str(e)
                })

        if action == 'create_event':
            event_data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'location': request.POST.get('location'),
                'start_time': request.POST.get('start_time'),
                'end_time': request.POST.get('end_time'),
                'is_free': request.POST.get('is_free'),
                'cost': request.POST.get('cost'),
                'capacity': request.POST.get('capacity'),
            }
            try:
                self.club_mgmt_facade.create_event(club.club_id, club_leader.user_id, event_data)
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'club_events': club_events,
                    'success': 'Event created successfully!'
                })
            except ValueError as e:
                return render(request, 'club_leader/event_creation_form.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'error': str(e),
                    'form_data': event_data
                })

        if action == 'edit_event':
            event_id = request.POST.get('event_id')
            event_data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'location': request.POST.get('location'),
                'start_time': request.POST.get('start_time'),
                'end_time': request.POST.get('end_time'),
                'capacity': request.POST.get('capacity'),
            }
            try:
                self.club_mgmt_facade.edit_event(int(event_id), event_data)
                pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
                announcements = self.club_mgmt_facade.view_announcements(club.club_id)
                club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))
                return render(request, 'club_leader/dashboard.html', {
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'pending_requests': pending_requests,
                    'announcements': announcements,
                    'club_events': club_events,
                    'success': 'Event updated successfully!'
                })
            except ValueError as e:
                event = Event.objects.get(event_id=event_id)
                return render(request, 'club_leader/event_edit_form.html', {
                    'event': event,
                    'club': club,
                    'username': request.session.get('username'),
                    'club_leader': club_leader,
                    'error': str(e)
                })

        if action == 'delete_event':
            event_id = request.POST.get('event_id')
            try:
                self.club_mgmt_facade.delete_event_for_leader(int(event_id), club_leader.user_id)
                message = 'Event deleted successfully!'
            except ValueError as e:
                message = str(e)

            pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
            announcements = self.club_mgmt_facade.view_announcements(club.club_id)
            club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))

            return render(request, 'club_leader/dashboard.html', {
                'club': club,
                'username': request.session.get('username'),
                'club_leader': club_leader,
                'pending_requests': pending_requests,
                'announcements': announcements,
                'club_events': club_events,
                'success': message if 'successfully' in message else None,
                'error': None if 'successfully' in message else message
            })

        membership_id = request.POST.get('membership_id')

        try:
            if action == 'approve':
                self.club_mgmt_facade.approve_member(int(membership_id))
                message = 'Member approved successfully!'

            elif action == 'reject':
                self.club_mgmt_facade.deny_member(int(membership_id))
                message = 'Member request rejected'

            elif action == 'suspend_member':
                self.club_mgmt_facade.suspend_member(int(membership_id))
                message = 'Member suspended successfully'

            elif action == 'remove_member':
                self.club_mgmt_facade.remove_member(int(membership_id))
                message = 'Member removed successfully'

            else:
                message = 'Invalid action'

            pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
            approved_members = Membership.objects.filter(club=club, status='APPROVED').select_related('student').order_by('-approved_at')
            announcements = self.club_mgmt_facade.view_announcements(club.club_id)
            club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))

            return render(request, 'club_leader/dashboard.html', {
                'club': club,
                'username': request.session.get('username'),
                'club_leader': club_leader,
                'pending_requests': pending_requests,
                'approved_members': approved_members,
                'announcements': announcements,
                'club_events': club_events,
                'success': message
            })

        except ValueError as e:
            pending_requests = self.club_mgmt_facade.review_memberships(club.club_id)
            approved_members = Membership.objects.filter(club=club, status='APPROVED').select_related('student').order_by('-approved_at')
            announcements = self.club_mgmt_facade.view_announcements(club.club_id)
            club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))

            return render(request, 'club_leader/dashboard.html', {
                'club': club,
                'username': request.session.get('username'),
                'club_leader': club_leader,
                'pending_requests': pending_requests,
                'approved_members': approved_members,
                'announcements': announcements,
                'club_events': club_events,
                'error': str(e)
            })



class AdminDashboardView(View):

    facade = AdminFacade()

    def get(self, request):
        if request.session.get('user_type') != 'admin':
            return redirect('login')

        view_type = request.GET.get('view')

        if view_type == 'flagged':
            flags = Flag.objects.select_related('creator', 'event', 'announcement').order_by('-created_at')
            return render(request, 'admin/flagged_content.html', {
                'username': request.session.get('username'),
                'flags': flags
            })

        if view_type == 'club_detail':
            club_id = request.GET.get('club_id')
            try:
                club = Club.objects.select_related('club_leader').get(club_id=club_id)
                club_events = list(club.events.filter(status='UPCOMING').order_by('start_time'))
                club_members = []
                approved_count = Membership.objects.filter(club_id=club_id, status='APPROVED').count()
                memberships = Membership.objects.filter(
                    club_id=club_id,
                    status='APPROVED'
                ).select_related('student')[:1000]
                club_members = [m.student for m in memberships]

                return render(request, 'admin/club_detail.html', {
                    'club': club,
                    'club_events': club_events,
                    'club_members': club_members,
                    'approved_members_count': approved_count,
                    'username': request.session.get('username')
                })
            except Club.DoesNotExist:
                return redirect('admin_dashboard')

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
        flag_id = request.POST.get('flag_id')

        if action in ['mark_reviewed', 'resolve_flag', 'dismiss_flag']:
            try:
                flag = Flag.objects.get(flag_id=flag_id)
                admin_id = request.session.get('user_id')

                if action == 'mark_reviewed':
                    flag.mark_reviewed()
                    message = 'Flag marked as reviewed'
                elif action == 'resolve_flag':
                    flag.resolve(admin_id, 'RESOLVED')
                    message = 'Flag resolved successfully'
                elif action == 'dismiss_flag':
                    flag.resolve(admin_id, 'DISMISSED')
                    message = 'Flag dismissed'

                flags = Flag.objects.select_related('creator', 'event', 'announcement').order_by('-created_at')
                return render(request, 'admin/flagged_content.html', {
                    'username': request.session.get('username'),
                    'flags': flags,
                    'success': message
                })
            except Flag.DoesNotExist:
                flags = Flag.objects.select_related('creator', 'event', 'announcement').order_by('-created_at')
                return render(request, 'admin/flagged_content.html', {
                    'username': request.session.get('username'),
                    'flags': flags,
                    'error': 'Flag not found'
                })

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
