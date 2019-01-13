import os
import secrets
from PIL import Image
from flask import url_for,current_app
from flask_mail import Message
from blogapp import mail

def save_picture(picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(picture.filename)
    f_name = random_hex + f_ext

    saving_path = os.path.join(current_app.root_path, 'static/profile_pics',f_name)

    output_size = (125,125)
    i=Image.open(picture)
    i.thumbnail(output_size)
    i.save(saving_path)

    return f_name

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                   sender='noreply@demo.com',
                   recipients=[user.email])
    msg.body = f''' To reset the password, visit the following link:
{url_for('users.reset_password',token=token, _external=True)}

If you didn't make this request, then please ignore the email.
'''
    mail.send(msg)
