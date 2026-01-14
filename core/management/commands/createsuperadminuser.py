# core/management/commands/createsuperadminuser.py

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superadmin user with role="superadmin"'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the superadmin')
        parser.add_argument('--email', type=str, help='Email for the superadmin')
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            dest='interactive',
            default=True,
            help='Do NOT prompt for input (non-interactive mode)',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        interactive = options['interactive']

        # Prepare arguments for the original createsuperuser
        createsuperuser_args = {}
        if username:
            createsuperuser_args['username'] = username
        if email:
            createsuperuser_args['email'] = email
        createsuperuser_args['interactive'] = interactive

        # Call the built-in createsuperuser command
        try:
            call_command('createsuperuser', **createsuperuser_args)
        except Exception as e:
            raise CommandError(f"Failed to create base user: {str(e)}")

        # Find the most recently created user and update role
        try:
            # Get newest user by date_joined (safe in development)
            latest_user = User.objects.order_by('-date_joined').first()
            if not latest_user:
                raise CommandError("No user was created.")

            if latest_user.role != 'superadmin':
                latest_user.role = 'superadmin'
                latest_user.save(update_fields=['role'])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Superadmin created successfully: {latest_user.username} (role = superadmin)"
                    )
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(f"User {latest_user.username} is already superadmin.")
                )

        except Exception as e:
            raise CommandError(f"Could not set superadmin role: {str(e)}")