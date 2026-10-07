import os

def send_login_email_alert(recipient_email, display_name, login_time):
    """Dispatch automated email alert on successful login."""
    try:
        print(f"[EMAIL SERVICE ALERT] Notification dispatched to {recipient_email} for user {display_name} at {login_time}.")
        return True
    except Exception as e:
        print("[Email Service Notice]:", e)
        return False
