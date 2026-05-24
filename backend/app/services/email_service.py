"""
Email Service for Earning Notifications
Sends earning alerts to beneficiary
"""

import os
import smtplib
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class EmailService:
    """
    Handles email notifications for earnings
    """
    
    def __init__(self):
        self.logger = logging.getLogger('EmailService')
        
        # In production, these would be real SMTP credentials
        # For now, we generate email content that can be viewed/sent manually
        self.sent_emails_dir = "./sent_emails"
        os.makedirs(self.sent_emails_dir, exist_ok=True)
    
    def send_earning_notification(
        self,
        to_email: str,
        subject: str,
        body: str,
        wallet_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send or save earning notification email
        """
        
        # Create email content
        email_id = f"email_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(to_email) % 10000}"
        
        full_email = f"""
FROM: Autonomous AI Earning System <earnings@autonomous-ai.local>
TO: {to_email}
SUBJECT: {subject}
DATE: {datetime.utcnow().isoformat()}

{body}

---
AUTONOMOUS EARNING SYSTEM - SECURE NOTIFICATION
Wallet ID: {wallet_info.get('wallet_id', 'N/A')}
Secret Code: {wallet_info.get('secret_code', 'N/A')}
Generated: {datetime.utcnow().isoformat()}
"""
        
        # Save to file (simulating sent email)
        email_file = os.path.join(self.sent_emails_dir, f"{email_id}.txt")
        with open(email_file, 'w') as f:
            f.write(full_email)
        
        self.logger.info(f"📧 Earning notification saved: {email_file}")
        
        return {
            "success": True,
            "email_id": email_id,
            "recipient": to_email,
            "subject": subject,
            "saved_to": email_file,
            "status": "saved_locally"  # In production: "sent_via_smtp"
        }
    
    def get_email_history(self, email_address: str) -> list:
        """Get history of sent emails to address"""
        emails = []
        
        for filename in os.listdir(self.sent_emails_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.sent_emails_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                    if email_address in content:
                        emails.append({
                            "filename": filename,
                            "content": content,
                            "timestamp": filename.split('_')[1] if '_' in filename else "unknown"
                        })
        
        return sorted(emails, key=lambda x: x["timestamp"], reverse=True)


# Global instance
_email_service: Optional[EmailService] = None

def get_email_service() -> EmailService:
    """Get or create email service"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
