#!/var/www/user118263/data/myenv/bin/python
from wsgiref.handlers import CGIHandler
from app import app 
CGIHandler().run(app)