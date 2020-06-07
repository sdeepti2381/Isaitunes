from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.validators import InputRequired, Email
class FeedbackForm(Form):
    name = TextField("Name", [InputRequired("Please enter your name")])
    email = TextField("Email", [InputRequired("Please enter your email id"), Email("This field requires a valid email address.")])
    message = TextAreaField("Message", [InputRequired("Please include a message")])
    submit = SubmitField("Submit")

