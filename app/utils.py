import tempfile, re
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from xhtml2pdf import pisa

def convert(source):
    pdf = tempfile.NamedTemporaryFile(delete = False, suffix = '.pdf')
    pisa_status = pisa.CreatePDF(source, dest = pdf)
    if pisa_status.err:
        print("Errore nella creazione del PDF:", pisa_status.err)
    pdf.close()
    return pdf.name

def is_password_valid(password):
    if len(password) < 8:
        return False, "La password deve contenere almeno 8 caratteri."
    if not re.search("[a-z]", password):
        return False, "La password deve contenere almeno una lettera minuscola."
    if not re.search("[A-Z]", password):
        return False, "La password deve contenere almeno una lettera maiuscola."
    if not re.search("[0-9]", password):
        return False, "La password deve contenere almeno un numero."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): 
        return False, "La password deve contenere almeno un simbolo."
    return True, ""

def is_email_valid(email):
    if User.query.filter_by(email=email).first() is not None:
        return False, "L'indirizzo email è già presente."
    return True, ""