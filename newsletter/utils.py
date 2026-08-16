from django.core import signing

UNSUBSCRIBE_SALT = 'newsletter-unsubscribe'


def generate_unsubscribe_token(email):
    """A signed, tamper-proof token embedding the email — lets someone
    unsubscribe via a plain link with no login required, while preventing
    anyone from unsubscribing an address that isn't theirs (the token can't
    be forged without SECRET_KEY, unlike a raw ?email= query param)."""
    return signing.dumps(email, salt=UNSUBSCRIBE_SALT)


def verify_unsubscribe_token(token, max_age_seconds=60 * 60 * 24 * 365):
    """Returns the email if the token is valid and not expired, else None."""
    try:
        return signing.loads(token, salt=UNSUBSCRIBE_SALT, max_age=max_age_seconds)
    except signing.BadSignature:
        return None
