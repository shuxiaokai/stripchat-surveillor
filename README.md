# stripchat-surveillor

The surveillor.py-script records models from [stripchat](https://stripchat.com/) / [xhamsterlive](https://xhamsterlive.com/) continuously by out-of-rowser-usage of their API. It is written in python and utilises ffmpeg.

## Start Up:
For this script to function, [ffmpeg](https://ffmpeg.org/download.html#build-linux) needs to be installed on your system! Since it is written in Python, Python needs to be installed on your system as well.

After making sure ffmpeg is installed, download this repo and then in the directory of the repo:

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
* If you want to initiate concatenation of all videos manually, open terminal in the script location and then execute `python3 -c 'import surveillor; surveillor.video_stitcher()'` from the command line.
* To concatenate and h264-transcode all videos, on Linux, execute `python3 -c 'import surveillor; surveillor.process_vids()'` from the command line. This is performance-intensive.
