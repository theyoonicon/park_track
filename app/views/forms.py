from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError
from ..models import User

class RegistrationForm(FlaskForm):
    username = StringField('사용자 이름', 
                           validators=[DataRequired(message="사용자 이름을 입력해 주세요"), 
                                       Length(min=6, max=15, message="사용자 이름은 6자에서 15자 사이여야 합니다"), 
                                       Regexp('^[A-Za-z0-9]*$', 0, 
                                              '사용자 이름은 영문자와 숫자만 포함할 수 있습니다')])
    email = StringField('이메일', 
                        validators=[DataRequired(message="이메일을 입력해 주세요"), 
                                    Email(message='유효한 이메일 주소를 입력해 주세요')])
    password = PasswordField('비밀번호', 
                             validators=[DataRequired(message="비밀번호를 입력해 주세요"), 
                                         Length(min=8, message="비밀번호는 최소 8자 이상이어야 합니다"), 
                                         Regexp('(?=.*[a-z])', 0, 
                                                '비밀번호는 최소 하나의 소문자를 포함해야 합니다'),
                                         Regexp('(?=.*[0-9])', 0, 
                                                '비밀번호는 최소 하나의 숫자를 포함해야 합니다'),
                                         Regexp('(?=.*[!@#$%^&*()_+=-])', 0, 
                                                '비밀번호는 최소 하나의 특수문자를 포함해야 합니다')])
    confirm_password = PasswordField('비밀번호 확인', 
                                     validators=[DataRequired(message="비밀번호 확인을 입력해 주세요"), 
                                                 EqualTo('password', 
                                                         message='비밀번호가 일치하지 않습니다')])
    submit = SubmitField('회원가입')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('이미 사용 중인 사용자 이름입니다.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('이미 등록된 이메일 주소입니다.')
