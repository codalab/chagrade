from django.conf import settings
from django.core.mail import send_mail, send_mass_mail


def send_chagrade_mail(users, subject, message, html_message):
    emails = [user.email for user in users]
    send_mail(subject=subject, message=message, html_message=html_message, from_email=settings.SENDGRID_FROM_EMAIL, recipient_list=emails)


def send_klass_mail(klass, subject, message):
    # May not be perfect due to the fact that message is probably a non-html message.
    # Get all of the students, and make a tuple that contains elements where each one is a student/email.
    # Format: (subject, message, from_email, to_email)
    datatuple = tuple([(subject, message, settings.SENDGRID_FROM_EMAIL, [student.user.email]) for student in klass.enrolled_students.all()])
    send_mass_mail(datatuple)
