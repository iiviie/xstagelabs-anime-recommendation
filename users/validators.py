from django.core.exceptions import ValidationError
import re

def validate_password_strength(password):
    """
    Validate that the password meets the following criteria:
    1. At least 8 characters long
    2. Contains at least one uppercase letter
    3. Contains at least one lowercase letter
    4. Contains at least one digit
    5. Contains at least one special character
    """
    if len(password) < 8:
        raise ValidationError(
            'Password must be at least 8 characters long.',
            code='password_too_short'
        )
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            'Password must contain at least one uppercase letter.',
            code='password_no_upper'
        )
    
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            'Password must contain at least one lowercase letter.',
            code='password_no_lower'
        )
    
    if not re.search(r'\d', password):
        raise ValidationError(
            'Password must contain at least one digit.',
            code='password_no_digit'
        )
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(
            'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).',
            code='password_no_special'
        ) 