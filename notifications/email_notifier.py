#!/usr/bin/env python3
"""
Email notification system for YouTube token expiration warnings.
Attempts to authenticate with YouTube and notifies when the token needs regeneration.
"""

import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

# Garantir acesso aos módulos do projeto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from video.youtube_publisher import YouTubePublisher


class EmailNotifier:
    """Manages email notifications for token expiration warnings"""
    
    def __init__(self, sender_email: str, recipient_email: str, app_password: str):
        """
        Initialize email notifier
        
        Args:
            sender_email: Gmail address to send from
            recipient_email: Email address to send to
            app_password: Gmail App Password (not regular password!)
        """
        self.sender_email = sender_email
        self.recipient_email = recipient_email
        self.app_password = app_password
        self.tracking_file = os.path.join(
            os.path.dirname(__file__), 
            'last_email_sent.json'
        )
        self.notification_interval_days = 6
    
    def token_requires_regeneration(self) -> bool:
        """
        Usa o YouTubePublisher para validar o token atual.
        Retorna True quando o token precisa ser regenerado.
        """
        print("[INFO] Validating YouTube token before sending notification...")
        try:
            publisher = YouTubePublisher()
            if publisher.authenticate():
                print("[SUCCESS] Token válido. Nenhum email necessário.")
                return False
            print("[WARNING] Token inválido detectado. Notificação será enviada.")
            return True
        except Exception as e:
            print(f"[ERROR] Falha ao validar token: {str(e)}")
            print("[WARNING] Assumindo que o token precisa ser regenerado.")
            return True
    
    def send_token_expiration_warning(self) -> bool:
        """
        Send email warning about YouTube token expiration
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = self.recipient_email
            message['Subject'] = "Atualizar token YouTubeVideoGenerator"
            
            # Email body in Portuguese (as requested)
            body = """
Olá!

Detectamos que o token do YouTube utilizado pelo projeto YouTubeVideoGenerator não pôde ser autenticado.
Isso normalmente acontece quando o token expira (após ~6 meses sem uso) ou quando o acesso é revogado manualmente.

PARA NORMALIZAR A PUBLICAÇÃO AUTOMÁTICA:

1. Execute localmente no seu computador:
   python config/generate_youtube_token.py

2. Siga as instruções no navegador para autenticar com a conta correta

3. Copie o novo token gerado:
   python config/copy_token_to_clipboard.py

4. Atualize o GitHub Secret:
   - Vá em: Settings → Secrets and variables → Actions
   - Encontre: YOUTUBE_TOKEN
   - Clique em "Update"
   - Cole o novo token
   - Salve!

IMPORTANTE:
- Este email é enviado apenas quando o token atual falha na autenticação
- Não responda a este email (é automático)
- Após atualizar o token, rode novamente o workflow no GitHub Actions

Para mais informações, consulte o README.md do projeto.

---
YouTubeVideoGenerator - Automated Notification System
"""
            
            message.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Connect to Gmail SMTP server
            print("[INFO] Connecting to Gmail SMTP server...")
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.app_password)
                text = message.as_string()
                server.sendmail(self.sender_email, self.recipient_email, text)
            
            print(f"[SUCCESS] Email sent successfully to {self.recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("[ERROR] Gmail authentication failed!")
            print("        Make sure you're using an App Password, not your regular Gmail password.")
            print("        Create one at: https://myaccount.google.com/apppasswords")
            return False
        
        except Exception as e:
            print(f"[ERROR] Failed to send email: {str(e)}")
            return False
    
    def update_last_sent_date(self):
        """Update tracking file with current date"""
        try:
            # Create notifications directory if it doesn't exist
            os.makedirs(os.path.dirname(self.tracking_file), exist_ok=True)
            
            data = {
                'last_sent_date': datetime.now().isoformat(),
                'last_sent_readable': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[INFO] Updated tracking file: {self.tracking_file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to update tracking file: {str(e)}")
    
    def run(self) -> str:
        """
        Main execution flow:
        1. Valida token
        2. Envia email se necessário
        """
        print("="*60)
        print("EMAIL NOTIFIER - YouTube Token Expiration Warning")
        print("="*60)
        if not self.token_requires_regeneration():
            return "token_ok"
        
        print("[INFO] Token inválido detectado. Enviando email de notificação...")
        
        if self.send_token_expiration_warning():
            self.update_last_sent_date()
            print("[SUCCESS] Email notification sent and tracked")
            return "sent"
        else:
            print("[ERROR] Failed to send email notification")
            return "failed"


def main():
    """
    Main function for standalone execution
    Reads configuration from environment variables
    """
    # Get configuration from environment
    sender_email = os.getenv('EMAIL_SENDER')
    recipient_email = os.getenv('EMAIL_RECIPIENT')
    app_password = os.getenv('EMAIL_PASSWORD')
    
    # Validate configuration
    if not sender_email:
        print("[ERROR] EMAIL_SENDER environment variable not set")
        print("        Set it with: export EMAIL_SENDER=your-email@gmail.com")
        return 1
    
    if not recipient_email:
        print("[ERROR] EMAIL_RECIPIENT environment variable not set")
        print("        Set it with: export EMAIL_RECIPIENT=recipient@gmail.com")
        return 1
    
    if not app_password:
        print("[ERROR] EMAIL_PASSWORD environment variable not set")
        print("        Set it with your Gmail App Password")
        print("        Create one at: https://myaccount.google.com/apppasswords")
        return 1
    
    # Create notifier and run
    notifier = EmailNotifier(sender_email, recipient_email, app_password)
    result = notifier.run()
    
    if result == "token_ok":
        return 0
    if result == "sent":
        return 2  # Non-zero exit to halt workflows when token attention is required
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

