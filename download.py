# MIT License
#
# Copyright (c) 2019 Shubham Rao
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import youtube_dl
import os.path

PLAYLIST_URL = 'https://www.youtube.com/playlist?list=PLiZxWe0ejyv8CSMylrxb6Nx4Ii2RHbu_j'

DATA_DIR = "data/"
opts = {

    # Don't download video
    'skip_download': True,
    'downloadarchive': os.path.join(DATA_DIR, "archive"),

    # Subtitle Options
    'writesubtitles': True,
    'subtitlelangs': 'en',
    'subtitleformat': 'vtt',

    # File Options
    'restrictfilenames': True,
    'nooverwrites': True,
    'outtmpl': os.path.join(DATA_DIR, "%(playlist_index)s.%(ext)s"),

    # Misc. Options
    'playlistrandom': True,
    'ignoreerrors': True,
    'quiet': True,
    'forcefilename': True,
}


def main():
    with youtube_dl.YoutubeDL(opts) as ydl:
        ydl.download([PLAYLIST_URL])


if __name__ == '__main__':
    main()
