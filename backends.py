"""
Sendmail email backend class.

Credits: https://djangosnippets.org/snippets/1864/
"""
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from subprocess import Popen, PIPE
from emails.signers import DKIMSigner


class EmailBackend(BaseEmailBackend):
    """
    Специальная обертка для отправки писем стандартным способом, но через sendmail и с DKIM-подписью
    """

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return
        num_sent = 0
        #

        #
        for message in email_messages:
            if self._send(message):
                num_sent += 1
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False

        _dkim_signer = DKIMSigner(privkey=settings.DKIM_PRIVATE_KEY, domain=settings.DKIM_DOMAIN,
                                  selector=settings.DKIM_SELECTOR)
        msg3 = email_message.message()

        dkim_header = _dkim_signer.get_sign_header(msg3.as_bytes())
        if dkim_header:
            msg3._headers.insert(0, dkim_header)

        try:
            # -t: Read message for recipients
            ps = Popen(['/usr/sbin/sendmail', '-t'], stdin=PIPE, stderr=PIPE)
            ps.stdin.write(msg3.as_bytes())
            (stdout, stderr) = ps.communicate()
        except:
            if not self.fail_silently:
                raise
            return False
        if ps.returncode:
            if not self.fail_silently:
                error = stderr if stderr else stdout
                raise Exception('send_messages failed: %s' % error)
            return False
        return True
