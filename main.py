
#[START imports]
import logging
import os
import cloudstorage as gcs
import webapp2
import folium
import json
import urllib2
from google.appengine.api import app_identity
#[END imports]

killings = urllib2.urlopen("https://raw.githubusercontent.com/joshbegley/the-counted/master/skeleton.json")
data = json.load(killings)  



webpage_header = r"""<!DOCTYPE html>
                <html>          
                <head> 
                <title>Mapping police killings - armed versus unarmed</title> 
                <meta name="description" content="Coordinates of police killings across the United States of America, colored according to whether the victim was armed or unarmed. Mouse-over to discover facts about the killing, such as the age, name, and race of the victim, and the cause of death."> 
                <meta charset="utf-8"/>
                <meta name="author" content="Peter Phalen"/> 
                <link rel="icon" type="image/png" href="../images/icon-code-fork-16x16.png" sizes="16x16"> 
                <link rel="icon" type="image/png" href="../images/icon-code-fork-32x32.png" sizes="32x32"> 
                <link rel="icon" type="image/x-icon" href="../images/favicon.ico"> 
                <link rel="shortcut icon" type="image/x-icon" href="../images/favicon.ico"/> 
                <meta property="og:url" content="https://www.peterphalen.com/datavisualization/map-police-killings.html"/> 
                <meta property="og:title" content="Mapping police killings"/> 
                <meta property="og:description" content="Interactive map of police killings in the United States. Generated using data from The Guardian's The Counted project."/> 
                <meta property="og:image" content="https://www.peterphalen.com/images/police-killings-map-img.png"/> 
                <meta property="twitter:card" content="summary_large_image"/> 
                <meta property="twitter:creator" content="@peterphalen"/> 
                <meta property="twitter:description" content="Interactive map of police killings in the United States. Generated using data from The Guardian'\s The Counted project."/> 
                <meta name="twitter:image" content="https://www.peterphalen.com/images/police-killings-map-img.png"/> type" content="text/html; charset=UTF-8" />
                 """
        
            


#[START retries]
my_default_retry_params = gcs.RetryParams(initial_delay=5,
                                          max_delay=30,
                                          backoff_factor=2,
                                          max_retry_period=200)
gcs.set_default_retry_params(my_default_retry_params)
#[END retries]


#[MAP definition]
map_killings = folium.Map(location=[39.8282, -98.5795], zoom_start=5)

#iterate markers
for i in range(0, len(data)):
    map_killings.simple_marker([data[i]['lat'], data[i]['long']], popup=data[i]['name'])


class MainPage(webapp2.RequestHandler):
    """Main page for GCS demo application."""

    #[START get_default_bucket]
    def get(self):


        bucket_name = os.environ.get('BUCKET_NAME',
                                     app_identity.get_default_gcs_bucket_name())

        self.response.headers['Content-Type'] = 'text/plain'

        bucket = '/' + bucket_name
        filename = bucket + '/demo-testfile'
        self.tmp_filenames_to_clean_up = []

        try:
            self.create_file(filename)
            self.response.write('\n\n')

            gcs_file = gcs.open(filename)
            map_html = gcs_file.read()
            map_html = map_html[150:len(map_html)] #drop opening headers
            full_webpage_html = webpage_header + map_html + "\n\n</html>"

            self.response.write(full_webpage_html)
            gcs_file.close()
            self.response.write('\n\n')


        except Exception, e:
          logging.exception(e)
          self.response.write('\n\nThere was an error running the demo! '
                              'Please check the logs for more details.\n')

        else:
          pass

    #[START write]
    def create_file(self, filename):


        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(filename,
                        'w',
                        content_type='text/plain',
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar'},
                        retry_params=write_retry_params)
        map_killings.create_map(gcs_file)
        gcs_file.close()
        self.tmp_filenames_to_clean_up.append(filename)
    #[END write]





app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)


