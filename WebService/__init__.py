### 모듈 로딩
from flask import Flask, url_for

### Application Factory 함수
def create_app():
    ## Flask Server 인스턴스 생성
    app = Flask(__name__)
    
    ## Blueprint 인스턴스 등록 : 서브 카테고리에 해당하는 페이지 라우팅 기능
    from .views import rileyFilm_views
    
    app.register_blueprint(rileyFilm_views.bp)
    
    ## Flask Server 인스턴스 반환
    return app
