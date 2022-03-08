# stripchat-surveillor

The surveillor.py-script records models from [stripchat](https://stripchat.com/) / [xhamsterlive](https://xhamsterlive.com/) continuously by exploiting a publically accessible API of the site and agnostic hls-routing.

This script is tested in Ubuntu and with ffmpeg version 4.2.4-1ubuntu0.1. If it functions for other operating systems or ffmpeg binaries is not known.

## Start Up (in Ubuntu):

```console
pip install -r requirements.txt
```

```console
python3 surveillor.py <model usernames in lower-case, separated by space>
```

### Odds and Ends

* To ease repeated recording of a long list of followed models, create models_followed.txt and write each model username in lower-case separated by newline into this text file. Then execute script without arguments
* The recording-priority is set by the order in which model-usernames are listed in the models_followed.txt-file
* As default, the streaming-quality is set to 480p/16:9 and if not, whatever the default streaming-resolution and aspect-ratio happens to be set by the streamer (in this case, usually higher resolution and odd aspect ratios)
* As default, the number of concurrently streamed shows is equal the available number of threads. This assures that the script doesn't produce 'runaway' ffmpeg-processes
* For OpSec, while executing surveillor.py it is recommended to use a VPN-connection to a server operated by a privacy-focused VPN-service. Otherwise, there is the risk that the host triangulates you due to the unusually large response being requested to the API.

## Analytics

As of the commit-date of this README-file, analytics.py, when executed, generates a sqlite3-db from the data in /data_dump json-files. Generates one table for each model found in the json-files. Only content of the tables is date and time tags for when the model was on-line. Serves as the backbone for future show-schedule-predictor-functionality or other analytics-based functionalities.
