
#[START imports]
import logging
import os
import cloudstorage as gcs
import webapp2
import folium

from google.appengine.api import app_identity
#[END imports]



#[START retries]
my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)
#[END retries]



class MainPage(webapp2.RequestHandler):
    """Main page for GCS demo application."""

    #[START get_default_bucket]
    def get(self):
        bucket_name = os.environ.get('BUCKET_NAME',
                                     app_identity.get_default_gcs_bucket_name())

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Demo GCS Application running from Version: '
                            + os.environ['CURRENT_VERSION_ID'] + '\n')
        self.response.write('Using bucket name: ' + bucket_name + '\n\n')
        #[END get_default_bucket]

        bucket = '/' + bucket_name
        filename = bucket + '/demo-testfile'
        self.tmp_filenames_to_clean_up = []

        try:
          self.create_file(filename)
          self.response.write('\n\n')

          self.read_file(filename)
          self.response.write('\n\n')


        except Exception, e:
          logging.exception(e)
          self.response.write('\n\nThere was an error running the demo! '
                              'Please check the logs for more details.\n')

        else:
          self.response.write('\n\nThe demo ran successfully!\n')

    #[START write]
    def create_file(self, filename):

        self.response.write('Creating file %s\n' % filename)

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(filename,
                        'w',
                        content_type='text/plain',
                        options={'x-goog-meta-foo': 'foo',
                                 'x-goog-meta-bar': 'bar'},
                        retry_params=write_retry_params)
        gcs_file.write('abcde\n')
        gcs_file.write('f'*1024*4 + '\n')
        gcs_file.close()
        self.tmp_filenames_to_clean_up.append(filename)
    #[END write]

    #[START read]
    def read_file(self, filename):
        self.response.write('Abbreviated file content (first line and last 1K):\n')

        gcs_file = gcs.open(filename)
        self.response.write(gcs_file.readline())
        gcs_file.seek(-1024, os.SEEK_END)
        self.response.write(gcs_file.read())
        gcs_file.close()
    #[END read]




app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)


