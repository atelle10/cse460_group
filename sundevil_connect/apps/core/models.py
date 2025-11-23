from django.db import models
from django.utils import timezone
from typing import Dict
from apps.controllers.notification_controller import ISubject


"""This file defines the entities described in the class diagram for our system (Models for the django framework)"""
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self) -> str:
        return self.username


class Student(User):
    privacy_level = models.IntegerField(default=0)
    topics_of_interest = models.JSONField(default=list)
    major = models.CharField(max_length=100, blank=True)
    college_year = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'students'



class ClubLeader(Student):
    title = models.CharField(max_length=100)
    leader_start_date = models.DateField()

    class Meta:
        db_table = 'club_leaders'

class Admin(User):
    admin_level = models.IntegerField(default=1)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'admins'



class Club(models.Model):
    club_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120, db_index=True)
    description = models.TextField()
    location = models.CharField(max_length=120)
    categories = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    members_count = models.IntegerField(default=0)
    leaders_count = models.IntegerField(default=0)
    club_leader = models.ForeignKey(
        ClubLeader,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_clubs'
    )

    class Meta:
        db_table = 'club'


class ClubApplication(models.Model, ISubject):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('UNDER_REVIEW', 'Under Review'),
    ]

    application_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    metadata = models.JSONField()
    is_approved = models.BooleanField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'club_applications'


    def mark_under_review(self):
        self.status = 'UNDER_REVIEW'
        self.save()



class Membership(models.Model, ISubject):
    ALL_MEMBERSHIP_STATUSES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    membership_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='memberships')
    status = models.CharField(max_length=20, choices=ALL_MEMBERSHIP_STATUSES, default='PENDING')
    joined_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'memberships'
        unique_together = ('student', 'club')

    def approve(self):
        self.status = 'APPROVED'
        self.approved_at = timezone.now()
        self.save()
        self.club.members_count += 1
        self.club.save()

    def reject(self):
        self.status = 'REJECTED'
        self.save()



class Announcement(models.Model):
    announcement_id = models.AutoField(primary_key=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='announcements')
    creator = models.ForeignKey(ClubLeader, on_delete=models.SET_NULL, null=True, related_name='announcements')
    message = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-is_pinned', '-created_at']
    
    def edit_announcement(self, message: str):
        self.message = message
        self.save()



class Event(models.Model, ISubject):
    EVENT_STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    EVENT_TYPE_CHOICES = [
        ('IN_PERSON', 'In Person'),
        ('VIRTUAL', 'Virtual'),
    ]

    event_id = models.AutoField(primary_key=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='IN_PERSON')
    is_free = models.BooleanField(default=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    categories = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='UPCOMING')
    capacity = models.IntegerField(null=True, blank=True)
    registered_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'events'
        ordering = ['start_time']
    
    def is_paid(self) -> bool:
        return not self.is_free
    
    def at_capacity(self) -> bool:
        if self.capacity is None:
            return False
        return self.registered_count >= self.capacity

    def cancel(self):
        self.status = 'CANCELLED'
        self.save()


class Registration(models.Model, ISubject):
    REGISTRATION_STATUS_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('NOT_REQUIRED', 'Not Required'),
    ]

    registration_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=20, choices=REGISTRATION_STATUS_CHOICES, default='REGISTERED')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='NOT_REQUIRED')
    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'registrations'
        unique_together = ('student', 'event')
        ordering = ['-registered_at']

    def confirm(self):
        self.status = 'REGISTERED'
        self.save()
        self.event.registered_count += 1
        self.event.save()

    def cancel(self):
        if self.status == 'REGISTERED':
            self.status = 'CANCELLED'
            self.cancelled_at = timezone.now()
            self.save()
            self.event.registered_count -= 1
            self.event.save()


class Flag(models.Model):
    FLAG_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('UNDER_REVIEW', 'Under Review'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]

    flag_id = models.AutoField(primary_key=True)
    severity_rank = models.IntegerField(default=1)
    target = models.CharField(max_length=50)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flags_created')
    reviewed = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='flags')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, null=True, blank=True, related_name='flags')
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=FLAG_STATUS_CHOICES, default='PENDING')
    resolved_by = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, related_name='flags_resolved')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'flags'
        ordering = ['-created_at']

    def mark_reviewed(self):
        self.reviewed = True
        self.status = 'UNDER_REVIEW'
        self.save()

    def resolve(self, admin_id: int, decision: str):
        admin = Admin.objects.get(user_id=admin_id)
        self.reviewed = True
        self.status = decision
        self.resolved_by = admin
        self.resolved_at = timezone.now()
        self.save()

