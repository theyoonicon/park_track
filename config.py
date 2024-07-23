import os

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'park.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

# SQLALCHEMY_DATABASE_URI는 데이터베이스 접속 주소
# SQLALCHEMY_TRACK_MODIFICATIONS는 SQLAlchemy의 이벤트를 처리하는 옵션

# 앞으로 모델을 추가하거나 변경할 때는
# flask db migrate 명령과 flask db upgrade 명령만 사용할 것이다.
# 즉, 앞으로 데이터베이스 관리를 위해 여러분이 반드시 알아야 할 명령어는 다음 2가지이다.