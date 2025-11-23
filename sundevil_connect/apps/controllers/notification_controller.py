from abc import ABC, abstractmethod
from typing import List, Dict


class IObserver(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Dict):
        pass


class ISubject:
    _observers: List[IObserver] = []

    @classmethod
    def attach_observer(cls, observer: IObserver):
        if observer not in cls._observers:
            cls._observers.append(observer)

    @classmethod
    def detach_observer(cls, observer: IObserver):
        if observer in cls._observers:
            cls._observers.remove(observer)

    @classmethod
    def notify_observers(cls, event_type: str, data: Dict):
        for observer in cls._observers:
            observer.update(event_type, data)


class EmailNotifier(IObserver):
    def update(self, event_type: str, data: Dict):
        if event_type == 'MEMBERSHIP_APPROVED':
            self.send_notification(
                recipient_email=data.get('student_email'),
                subject='Membership Approved',
                message=f"Your membership request for {data.get('club_name')} has been approved."
            )

        elif event_type == 'EVENT_REGISTRATION':
            self.send_notification(
                recipient_email=data.get('club_leader_email'),
                subject='New Event Registration',
                message=f"{data.get('student_name')} has registered for {data.get('event_title')}."
            )

        elif event_type == 'CLUB_APPLICATION_CREATED':
            admin_emails = data.get('admin_emails', [])
            for email in admin_emails:
                self.send_notification(
                    recipient_email=email,
                    subject='New Club Application',
                    message=f"A new club application has been submitted: {data.get('club_name')}."
                )

        elif event_type == 'EVENT_CREATED':
            member_emails = data.get('member_emails', [])
            for email in member_emails:
                self.send_notification(
                    recipient_email=email,
                    subject='New Event Created',
                    message=f"A new event has been created: {data.get('event_title')} on {data.get('event_date')}."
                )

        elif event_type == 'EVENT_UPDATED':
            member_emails = data.get('member_emails', [])
            for email in member_emails:
                self.send_notification(
                    recipient_email=email,
                    subject='Event Updated',
                    message=f"The event {data.get('event_title')} has been updated. Check the event page for details."
                )

    # Simulate email send out.
    def send_notification(self, recipient_email: str, subject: str, message: str):
        print(f"Email sent to: {recipient_email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("-" * 30)
