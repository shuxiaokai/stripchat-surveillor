# stripchat-surveillor

The surveillor.py-script records models from [stripchat](https://stripchat.com/) / [xhamsterlive](https://xhamsterlive.com/) continuously by out-of-rowser-usage of their API.

This script is tested in Ubuntu and with ffmpeg version 4.2.4-1ubuntu0.1. It seems to also work on Windows 10 if set up correctly. If it works on other platforms is not known.

## Start Up (Ubuntu):
Download this repo, then in the directory of the repo:

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
* If you want to initiate concatenation of all videos manually, in Linux, execute `python3 -c 'import surveillor; surveillor.video_stitcher()'` from the command line.
* To concatenate and h264-transcode all videos, on Linux, execute `python3 -c 'import surveillor; surveillor.process_vids()'` from the command line. This is performance-intensive.
