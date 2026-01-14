from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a new admin user with role="admin"'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username')
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--noinput', action='store_true', help='Non-interactive mode')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        noinput = options['noinput']

        if not noinput:
            if not username:
                username = input('Username: ')
            if not email:
                email = input('Email address: ')
            password = input('Password: ')
            password_confirm = input('Password (again): ')
            if password != password_confirm:
                raise CommandError("Passwords do not match.")
        else:
            # Non-interactive mode → use a default password (change in real scripts)
            password = 'adminpass123'

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            user.is_staff = True
            user.is_superuser = False
            user.role = 'admin'               # ← this is the important line
            user.save()

            self.stdout.write(self.style.SUCCESS(
                f'Admin user created: {username} (role=admin, is_staff=True)'
            ))
        except Exception as e:
            raise CommandError(f'Failed to create admin user: {str(e)}')
