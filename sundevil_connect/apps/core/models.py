from django.db import models

class User(models.Model):
    user_id: str = models.AutoField(primary_key=True)
    username: str = models.CharField(max_length=150, unique=True)
    email: str = models.EmailField()
    first_name: str = models.CharField(max_length=30)
    last_name: str = models.CharField(max_length=30)
    created_at: str = models.DateTimeField(auto_now_add=True)
    
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

    def __str__(self):
        return self.name


class ClubApplication(models.Model):
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

    def __str__(self):
        return f"Application by {self.student.username} - {self.status}"