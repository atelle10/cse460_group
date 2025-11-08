from django.shortcuts import render, redirect
from django.views import View
from apps.core.models import Student, Admin, ClubLeader, Club
from apps.facades.student_portal_facade import StudentPortalFacade
from apps.facades.admin_facade import AdminFacade


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
            return redirect('admin_dashboard')
        except Admin.DoesNotExist:
            pass

        try:
            student = Student.objects.get(username=username, password=password)
            request.session['user_id'] = student.user_id
            request.session['user_type'] = 'student'
            request.session['username'] = student.username
            return redirect('student_home')
        except Student.DoesNotExist:
            pass

        return render(request, 'auth/login.html', {
            'error': 'Invalid username or password'
        })



class StudentPortalView(View):

    facade = StudentPortalFacade()

    def get(self, request, club_id=None):
        if request.session.get('user_type') != 'student':
            return redirect('login')

        if club_id:
            club = self.facade.view_club_details(club_id)
            return render(request, 'portal/club_detail.html', {
                'club': club,
                'username': request.session.get('username')
            })

        action = request.GET.get('action')

        if action == 'apply':
            return render(request, 'portal/club_application_form.html', {
                'username': request.session.get('username')
            })

        clubs = self.facade.view_clubs()
        user_id = request.session.get('user_id')
        student = Student.objects.get(user_id=user_id)
        is_club_leader = ClubLeader.objects.filter(username=student.username + "_leader").exists()

        return render(request, 'portal/student_home.html', {
            'clubs': clubs,
            'username': request.session.get('username'),
            'is_club_leader': is_club_leader
        })

    def post(self, request):
        if request.session.get('user_type') != 'student':
            return redirect('login')

        student_id = request.session.get('user_id')

        club_data = {
            'name': request.POST.get('club_name'),
            'description': request.POST.get('description'),
            'location': request.POST.get('location'),
            'categories': [cat.strip() for cat in request.POST.get('categories', '').split(',') if cat.strip()]
        }

        try:
            self.facade.create_club_application(student_id, club_data)

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
        except Club.DoesNotExist:
            club = None

        return render(request, 'club_leader/dashboard.html', {
            'club': club,
            'username': request.session.get('username'),
            'club_leader': club_leader
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
