# auth_code_generator.py
import time
import random

# Rate-limiting dictionaries
IP_TRACKER = {}
EMAIL_TRACKER = {}
PHONE_TRACKER = {}
REQUEST_LIMIT = 3
TIME_FRAME = 30 * 60  # 30 minutes in seconds


def set_verification_code():
    """
    Generate a random 6-digit verification code.
    """
    return f"{random.randint(100000, 999999)}"


def check_rate_limit_ip(ip_address):
    # noinspection GrazieInspection
    """
        Check and update rate limits for the given IP address.

        Returns:
            (bool, str): (Success status, Message)
        """
    if not ip_address:
        return True, ""

    current_time = time.time()
    timestamps = IP_TRACKER.get(ip_address, [])

    # Remove timestamps older than TIME_FRAME
    IP_TRACKER[ip_address] = [t for t in timestamps if current_time - t < TIME_FRAME]

    if len(IP_TRACKER[ip_address]) >= REQUEST_LIMIT:
        return False, "Too many requests from this IP address. Try again later."

    # Record the current request
    IP_TRACKER[ip_address].append(current_time)
    return True, ""


def check_rate_limit_email(email):
    # noinspection GrazieInspection
    """
        Check and update rate limits for the given email address.

        Returns:
            (bool, str): (Success status, Message)
        """
    if not email:
        return True, ""

    current_time = time.time()
    timestamps = EMAIL_TRACKER.get(email, [])

    # Remove timestamps older than TIME_FRAME
    EMAIL_TRACKER[email] = [t for t in timestamps if current_time - t < TIME_FRAME]

    if len(EMAIL_TRACKER[email]) >= REQUEST_LIMIT:
        return False, "Too many requests to this email. Try again later."

    # Record the current request
    EMAIL_TRACKER[email].append(current_time)
    return True, ""


def check_rate_limit_phone(phone_number):
    # noinspection GrazieInspection
    """
        Check and update rate limits for the given phone number.

        Returns:
            (bool, str): (Success status, Message)
        """
    if not phone_number:
        return True, ""

    current_time = time.time()
    timestamps = PHONE_TRACKER.get(phone_number, [])

    # Remove timestamps older than TIME_FRAME
    PHONE_TRACKER[phone_number] = [t for t in timestamps if current_time - t < TIME_FRAME]

    if len(PHONE_TRACKER[phone_number]) >= REQUEST_LIMIT:
        return False, "Too many requests to this phone number. Try again later."

    # Record the current request
    PHONE_TRACKER[phone_number].append(current_time)
    return True, ""


# Example storage mechanism (in-memory for simplicity)
# In production, consider using a database or cache like Redis
VERIFICATION_CODES = {}

def store_verification_code(identifier, code, expiry=10 * 60):
    """
    Store the verification code with an optional expiry time.

    Parameters:
        identifier (str): The unique identifier (email or phone number).
        Code (str): The verification code.
        Expiry (int): Time in seconds before the code expires.
    """
    expiration_time = time.time() + expiry
    VERIFICATION_CODES[identifier] = {'code': code, 'expires_at': expiration_time}



def generate_verification_code(ip=None, identifier=None):

    # Initialize a list to collect error messages
    error_messages = []



    # Perform rate limit checks
    if ip:
        success, message = check_rate_limit_ip(ip)
        if not success:
            error_messages.append(message)

    if identifier == 'email':
        success, message = check_rate_limit_email(identifier)
        if not success:
            error_messages.append(message)

    else:
        success, message = check_rate_limit_phone(identifier)
        if not success:
            error_messages.append(message)

    if error_messages:
        # Concatenate all error messages
        return False, " ".join(error_messages)

    # All checks passed, generate and store the verification code
    code = set_verification_code()
    store_verification_code(identifier, code)
    return True, ""



def get_stored_code(identifier):
    """
    Retrieve the stored verification code for the given identifier.

    Parameters:
        identifier (str): The unique identifier (email or phone number).

    Returns:
        str or None: The stored verification code if valid, else None.
    """
    record = VERIFICATION_CODES.get(identifier)
    if not record:
        return None
    if time.time() > record['expires_at']:
        # Code has expired
        del VERIFICATION_CODES[identifier]
        return None
    return record['code']


def verify_code(identifier, provided_code):
    """
    Verify the provided code against the stored code for the identifier.

    Parameters:
        identifier (str): The unique identifier (email or phone number).
        Provided_code (str): The code provided by the user.

    Returns:
        bool: True if the code is valid, False otherwise.
    """
    stored_code = get_stored_code(identifier)
    if stored_code and stored_code == provided_code:
        # Optionally delete the code after successful verification
        del VERIFICATION_CODES[identifier]
        return True, ""
    elif stored_code and stored_code != provided_code:
        return False, "Code does not match"
    return False, "?????????????"
