from apps.controllers.notification_controller import IObserver, EmailNotifier


class NotifierFactory:
    @staticmethod
    def create_notifier(notifier_type: str = 'email') -> IObserver:
        if notifier_type == 'email':
            return EmailNotifier()
        raise ValueError(f"Unknown notifier type: {notifier_type}")
