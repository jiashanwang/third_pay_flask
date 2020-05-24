from application import app

from web.controllers.index import index_page

app.register_blueprint(index_page,url_prefix="/index")
