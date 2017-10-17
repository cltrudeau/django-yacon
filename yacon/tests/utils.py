from django.core import management

def create_test_site():
    management.call_command('yacon_add_site', 'my_name', 'my_domain.com')
    management.call_command('yacon_create_defaults')
    management.call_command('yacon_create_test_data')
