jwt_blacklist = set()

# 로그아웃 기능을 하는 클래스
class UserLogoutResource(Resource) :
    @jwt_required()
    def post(self) :

        jti = get_jwt()['jti']
        print(jti)

        jwt_blacklist.add(jti)

        return {'result' : 'success'}, 200