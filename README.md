This script records models from stripchat.com/xhamsterlive.com continuously by exploiting a publically accessible API of the site and agnostic hls-routing.

This script is tested in Ubuntu and with ffmpeg version 4.2.4-1ubuntu0.1. If it functions for other operating systems or ffmpeg binaries is not known.

#Start Up (in Ubuntu):

'''console
pip install -r requirements.txt
'''

'''console
python3 surveillor.py <model usernames in lower-case, separated by space>
'''

To ease repeated recording of a long list of followed models, create models_followed.txt and write each model username in lower-case separated by newline into this text file. Then execute script without arguments.

#Analytics

as of the commit-date of this README-file, analytics.py, when executed, generates a sqlite3-db from the data in /data_dump json-files. Generates one table for each model found in the json-files. Only content of the tables is date and time tags for when the model was on-line. Serves as the backbone for future show-schedule-predictor-functionality or other analytics-based functionalities.
