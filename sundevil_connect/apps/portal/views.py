from django.shortcuts import render, redirect
from django.views import View
from apps.core.models import Student, Admin
from apps.facades.student_portal_facade import StudentPortalFacade
from apps.facades.admin_facade import AdminFacade

""" This file defines the views for the user creating instances of the facades."""

class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            student = Student.objects.get(username=username, password=password)
            request.session['user_id'] = student.user_id
            request.session['user_type'] = 'student'
            request.session['username'] = student.username
            return redirect('student_home')
        except Student.DoesNotExist:
            pass
        
        try:
            admin = Admin.objects.get(username=username, password=password)
            request.session['user_id'] = admin.user_id
            request.session['user_type'] = 'admin'
            request.session['username'] = admin.username
            return redirect('admin_dashboard')
        except Admin.DoesNotExist:
            pass
        
        return render(request, 'auth/login.html', {
            'error': 'Invalid username or password'
        })


class LogoutView(View):
    def post(self, request):
        request.session.flush()
        return redirect('login')
    


class StudentPortalView(View):
    
    facade = StudentPortalFacade()

    def get(self, request):
        if request.session.get('user_type') != 'student':
            return redirect('login')
        
        clubs = self.facade.view_clubs()
        
        return render(request, 'portal/student_home.html', {
            'clubs': clubs,
            'username': request.session.get('username')
        })



class ClubApplicationView(View):
    
    facade = StudentPortalFacade()

    def get(self, request):
        if request.session.get('user_type') != 'student':
            return redirect('login')
        
        return render(request, 'portal/club_application_form.html', {
            'username': request.session.get('username')
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
            return render(request, 'portal/student_home.html', {
                'success': 'Club application submitted successfully!',
                'clubs': self.facade.view_clubs(),
                'username': request.session.get('username')
            })
        except ValueError as e:
            return render(request, 'portal/club_application_form.html', {
                'error': str(e),
                'username': request.session.get('username')
            })


class AdminDashboardView(View):
    
    facade = AdminFacade()

    def get(self, request):
        if request.session.get('user_type') != 'admin':
            return redirect('login')
        
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