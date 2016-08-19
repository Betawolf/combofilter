from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import configparser
import json
import sys
import re


class LocTracker:

  def __init__(self, filename):
    self.filename = filename
    self.locdict = {}

  def update(self, location, flush):
    #Update internal store.
    if location in self.locdict:
      self.locdict[location] += 1
    else:
      self.locdict[location] = 1
    
    #Write to file if requested.
    if flush:
      json.dump(self.locdict, open(self.filename,'w'))


class FilterListener(StreamListener):

    def __init__(self, cfg):
        op = cfg['output']
        self.tweetwriter = open(op['tweets_file'], "w")
        self.loctracker = LocTracker(op['location_file'])
        self.errfile = op['message_log']
        
        t = cfg['twitter']
        self.auth = OAuthHandler(t['consumer_key'], t['consumer_secret'])
        self.auth.set_access_token(t['access_token'],t['access_token_secret'])
        
        fil = cfg['filters'] 
        self.loclist = [float(x) for x in [fil['sw_lon'],fil['sw_lat'], fil['ne_lon'], fil['ne_lat']]]
        self.stream = Stream(self.auth, self)
        self.patterns = [re.compile('\\b{}\\b'.format(term.strip()), re.IGNORECASE) for term in fil['keywords'].split(',')]
        super().__init__()
    

    def on_data(self, data):
        
        d = json.loads(data)
        
        is_hit ='text' in d and any([pat.search(d['text']) for pat in self.patterns])
        
        if is_hit:
          self.outwriter.write(data)
          self.outwriter.write("\n")
        
        loc = None
        if d['place']:
          loc = d['place']['full_name']
        elif d['coordinates']:
          loc = d['coordinates']
          print(loc)
                
        self.loctracker.update(loc, is_hit)
        return True


    def write_message(self, status):
        open(self.errfile,'a').write(message+'\n')

    def on_limit(self, track):
      self.write_message("LIMIT: "+track)

    def on_warning(self, warning):
      self.write_message("WARN: "+warning)
    
    def on_error(self, status):
      self.write_message("ERR: "+status)
        
    def run(self):
      self.stream.filter(locations=self.loclist)


if __name__ == '__main__':

    cfgfile = "config.ini"
    if len(sys.argv) == 2:
      cfgfile = sys.argv[1] 

    cfg = configparser.ConfigParser()
    cfg.read(cfgfile)

    l = FilterListener(cfg)
    l.run()
