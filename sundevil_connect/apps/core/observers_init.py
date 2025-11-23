from apps.controllers.notifier_factory import NotifierFactory
from apps.core.models import Event, Registration, Membership, ClubApplication


def initialize_observers():
    notifier = NotifierFactory.create_notifier('email')

    Event.attach_observer(notifier)
    Registration.attach_observer(notifier)
    Membership.attach_observer(notifier)
    ClubApplication.attach_observer(notifier)

    print("Notification observers initialized successfully")
