# ICT/filters.py
from datetime import datetime
import timeago

def init_filters(app):
    @app.template_filter('timeago')
    def timeago_filter(date):
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return date
        return timeago.format(date, datetime.utcnow())