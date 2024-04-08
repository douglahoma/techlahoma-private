"""
https://flask.palletsprojects.com/en/2.3.x/config/

Flask has a way of handling configurations for apps where you can define
a class which has the values you want defined as fields and then set it to
the 'from_object' method. You end up needing to do something like this if
you are using any type of database like we are and there might be some other
reason we need to set keys in app.config so I wanted to have this here.
I don't actually know if we will need to more keys than these ones.
"""

import redislite

class Config:
    # Configure Redis for storing the session data on the server-side
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redislite.StrictRedis('/tmp/cache.db')