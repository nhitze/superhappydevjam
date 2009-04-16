import cgi
import os
import feedparser

from google.appengine.api import users
from google.appengine.api import urlfetch

from google.appengine.ext import webapp
from google.appengine.ext import db

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Tweet(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        tweets_query = Tweet.all()
        tweets = tweets_query.fetch(10)
        
        if users.get_current_user():
          url = users.create_logout_url(self.request.uri)
          url_linktext = 'Logout'
        else:
          url = users.create_login_url(self.request.uri)
          url_linktext = 'Login'
        
        template_values = {
          'tweets': tweets,
          'url': url,
          'url_linktext': url_linktext,
          }
          
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))          
        
class FeedTweet(webapp.RequestHandler):
  def get(self):
      feed = feedparser.parse('http://search.twitter.com/search.atom?q=appengine')
      self.response.out.write(feed.feed.title)
#      tweet = Tweet()
#      tweet.content = 'test'
#      tweet.put()

application = webapp.WSGIApplication([('/feed', FeedTweet), ('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()