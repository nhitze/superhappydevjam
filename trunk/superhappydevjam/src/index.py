import cgi
import os
import feedparser
import re
import urllib

from xml.dom import minidom

from google.appengine.api import users
from google.appengine.api import urlfetch

from google.appengine.ext import webapp
from google.appengine.ext import db

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Tweet(db.Model):
  author = db.StringProperty()
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
     
class VerifyYahoo(webapp.RequestHandler):
    def get(self):
        values = '';
        path = os.path.join(os.path.dirname(__file__), 'verify.html')
        self.response.out.write(template.render(path, values))          
        
class ReadYquery(webapp.RequestHandler):
    def get(self):
        
        import yaml
        f = open('test.yaml')
        dataMap = yaml.load(f)
        f.close()    

        query = cgi.escape(self.request.get('text'))
        if(query == ''):
            query = 'appengine'

        api = cgi.escape(self.request.get('queryapi'))
        if(api == ''):
            api = 'search'
            
        method = cgi.escape(self.request.get('querymethod'))
        if(method == ''):
            method = 'web'

        dataMap['config'][api][method]['name']    
        
        YQUERY_URL = 'http://query.yahooapis.com/v1/public/yql?q=SELECT%20*%20FROM%20'+dataMap['config'][api][method]['name']+'(10)%20WHERE%20query="'+dataMap['config'][api][method]['key']+'"'
        dom = minidom.parse(urllib.urlopen(YQUERY_URL))
        results = dom.getElementsByTagName('result')
        
        value = []
        for result in results:
            value.append({'title':result.getElementsByTagName('title')[0].firstChild.data,
                          'url':result.getElementsByTagName('url')[0].firstChild.data})            
        
        template_values = {'result':value}
        
        path = os.path.join(os.path.dirname(__file__), dataMap['config']['search']['web']['name'] + '.html')
        self.response.out.write(template.render(path, template_values)) 
        
class FeedTweet(webapp.RequestHandler):
  def get(self):
      feed = feedparser.parse('http://search.twitter.com/search.atom?lang=de&q=+appengine+google')
      for entry in feed.entries:
          tweet = Tweet()
          tweet.content = entry.title
          rgx = re.search('([^\s]+)', entry.author).group(0) 
          tweet.author = rgx
          tweet.put()

application = webapp.WSGIApplication([('/read', ReadYquery),
                                      ('/feed', FeedTweet), 
                                      ('/', MainPage)
                                      ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()