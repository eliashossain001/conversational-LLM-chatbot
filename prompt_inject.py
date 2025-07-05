import re
import hmac
import hashlib

class SanitizationError(Exception):
    """Custom exception for input sanitization errors."""
    pass

def generate_signed_prompt(command, secret_key):
    """
    Generate a signed prompt using a secret key.
    """
    signature = hmac.new(secret_key.encode(), command.encode(), hashlib.sha256).hexdigest()
    return f"{command}.{signature}"

def verify_signed_prompt(user_input):
    """
    Verify that the input contains a valid signed prompt before any modification.
    """
    signed_prompt_pattern = re.compile(r'\$Sys\.command\.\d+\.[a-fA-F0-9]{64}')
    match = signed_prompt_pattern.search(user_input)
    if not match:
        raise ValueError("Signed Prompt Error: Input lacks a valid signed prompt.")
    return match.group()  # Return the matched signed prompt for further validation

def validate_signature(signed_prompt, secret_key):
    """
    Validate the cryptographic signature of the signed prompt.
    """
    try:
        # Extract command ID and verify signature
        command, command_id, signature = re.split(r'\.', signed_prompt, maxsplit=2)
        expected_signature = hmac.new(secret_key.encode(), command_id.encode(), hashlib.sha256).hexdigest()

        if signature != expected_signature:
            raise ValueError("Signed Prompt Error: Invalid cryptographic signature.")
        return True
    except Exception as e:
        raise ValueError(f"Signature Validation Error: {e}")

def sanitize_input(user_input, allow_signed_prompts=False):
    """
    Sanitize user input while preserving signed prompts if allowed.
    Raises a SanitizationError for issues related to harmful patterns or input length.
    """
    original_input = user_input
    signed_prompt = None

    # Extract and temporarily remove signed prompt if allowed
    if allow_signed_prompts:
        signed_prompt = verify_signed_prompt(user_input)
        user_input = user_input.replace(signed_prompt, "")  # Temporarily remove the signed prompt

    # Check input length before other validations
    max_length = 500
    if len(user_input) > max_length:
        raise SanitizationError("Length Error: Input length exceeds the allowed limit. Please shorten your query.")

    # Forbidden content detection
    harmful_patterns = re.compile(r'\b(ignore|bypass|shutdown|system|exec|call|os\..*|--|;|#)\b', re.IGNORECASE)
    if harmful_patterns.search(user_input):
        raise SanitizationError("Forbidden Content Error: Input contains harmful patterns or forbidden content.")

    # Sanitize the input by removing unwanted characters
    sanitized_input = re.sub(r'[^\w\s.,?!-]', '', user_input)

    # Normalize and trim whitespace
    sanitized_input = sanitized_input.strip()

    # Reinsert signed prompt if allowed
    if allow_signed_prompts and signed_prompt:
        sanitized_input = signed_prompt + " " + sanitized_input.strip()

    # Return sanitized input without raising unnecessary errors
    return sanitized_input

def validate_input(user_input):
    """
    Validate input against a list of forbidden patterns.
    """
    forbidden_patterns = re.compile(r'\b(delete|drop|shutdown|system|access admin data|malicious code)\b', re.IGNORECASE)
    if forbidden_patterns.search(user_input):
        raise ValueError("Validation Error: Input contains forbidden content. Forbidden terms were detected in your query.")
    return True

def process_input(user_input, secret_key=None):
    """
    Process user input by verifying signed prompts, sanitizing, and validating.
    Provides distinct error messages for different scenarios.
    """
    try:
        # Step 1: Verify signed prompt if present
        signed_prompt = None
        if secret_key:
            try:
                signed_prompt = verify_signed_prompt(user_input)
                validate_signature(signed_prompt, secret_key)
            except ValueError as signature_error:
                raise ValueError(f"Signature Error: {signature_error}")

        # Step 2: Sanitize input
        try:
            sanitized_input = sanitize_input(user_input, allow_signed_prompts=bool(signed_prompt))
        except SanitizationError as sanitization_error:
            raise ValueError(f"Sanitization Error: {sanitization_error}")

        # Step 3: Validate input
        try:
            validate_input(sanitized_input)
        except ValueError as validation_error:
            raise ValueError(f"Validation Error: {validation_error}")

        return sanitized_input

    except ValueError as error:
        # Catch and return the specific error
        raise ValueError(f"Processing Error: {error}")
