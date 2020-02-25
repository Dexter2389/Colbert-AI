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

import webvtt
import glob
import os.path
import re

import download

DATA_DIR = os.path.join(download.DATA_DIR, "captions")


def main():
    speaker_jon = lambda text: re.match(r"&gt;&gt; (Jon:|JON:|jon:) (.*)$", text)
    speaker_stephen = lambda text: re.match(r"&gt;&gt; (Stephen:|STEPHEN:|stephen:) (.*)$", text)
    speaker = r"&gt;&gt; (Stephen|STEPHEN|stephen)*(Jon|JON|jon)*:?(.*)$"
    vtt = webvtt.WebVTT()
    vtt_files = glob.iglob(f"{DATA_DIR}/*.vtt")
    txt_file = os.path.join(DATA_DIR, "../", "captions.txt")
    with open(txt_file, "w+") as f:
        for vtt_file in vtt_files:
            stephen_speaking = True
            for caption in vtt.read(vtt_file):
                text = caption.text
                if speaker_jon(text):
                    stephen_speaking = False
                    continue
                if speaker_stephen(text):
                    stephen_speaking = True
                    text = "".join(x[1] for x in re.findall(r"&gt;&gt; (Stephen:|STEPHEN:|stephen:) (.*)$", text+<"|endoftext|">))
                    # print(text)
                if not stephen_speaking:
                    continue
                # print(text)
                text = re.sub(speaker, r"\3", text, flags=re.M)
                print(text.strip("\n "), file=f, end=" ")
                # print(text)


if __name__ == '__main__':
    main()
