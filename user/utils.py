import re
from .models import User

def is_valid_email(email):
	pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
	return bool(re.match(pattern, email))

def validate_passwords(password, confirm_password):

	errors = []

	if password != confirm_password:
		errors.append('passwords do not match')

	if len(password) < 6:
		errors.append('Password must be at least 6 characters long')

	return errors

def validate_registration_data(
	first_name, 
	last_name,
	email,
	username,
	password,
	confirm_password
):
	errors = []

	if not all(first_name and last_name and email and username and password and confirm_password):
		errors.append('All fields are required')

	errors.extend(validate_passwords(password, confirm_password))

	if not is_valid_email(email):
		errors.append('Invalid email entered')

	if User.objects.filter(username=username).exists():
		errors.append('A user with this username already exists')

	if User.objects.filter(email=email).exists():
		errors.append('A user with this email already exists')

	return errors