import vlc
import time
import threading
import queue
import re
import os
try:
    import youtube_dl
except:
    youtube_dl = None

done = False

class Player(threading.Thread):
    def __init__(self,threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print("Player Initialised\nReady")
        self.play()
        print("Quitting")
    def play(self):
        p = None
        playing = False
        while not done:
            if p == None:
                print("Nothing Playing")
                next = self.q.get()
                if next:
                    print("Something in queue. Putting it on.")
                    p = vlc.MediaPlayer(next)
                    p.play()
                    playing = True
            elif p.get_state() == State.Ended:
                print("Finished")
                p = None
                playing = False
            else:
                print(p.get_state())
            time.sleep(1)

class Downloader(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': "mp3",
            'outtmpl': '%(id)s',
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'outtmpl': "audiofiles/%(id)s",
        }
    def run(self):
        print("Downloader Initialised\nReady")
        self.download()
        print("Quitting")
    def download(self):
        self._yt = youtube_dl.YoutubeDL(self.opts)
        yt_link = re.compile(r'^(https?\:\/\/)?(www\.|m\.)?(youtube\.com|youtu\.?be)\/.+$')
        while not done:
            next = self.q.get()
            if next:
                if yt_link.match(next):
                    url = next
                else:
                    url = "ytsearch:" + next
                id = self._yt.extract_info(url, download=False)["entries"][0]["id"]
                if not os.path.isfile('audiofiles/' + id):
                    self._yt.download([url])
                play_queue.put("audiofiles/{}".format(id))
                print("Added to queue")
            time.sleep(1)

dl_queue = queue.Queue(0)
play_queue = queue.Queue(0)
dl_thread = Downloader(1,"Downloader",dl_queue)
play_thread = Player(2,"Player",play_queue)
dl_thread.start()
play_thread.start()
while not done:
    print("\nType video link or title to add to queue or type exit to quit")
    url = input("Video: ")
    if url == "exit":
        done = True
        break
    else:
        dl_queue.put(url)
        print("Added to download queue")
dl_thread.join()
play_thread.join()
print("Closing")

#p = vlc.MediaPlayer("file:///twenty one pilots - Stressed Out Parody (21 hydrants music video)-leSvUKji4CE.mp3")
#p.play()
#while p.get_state() != "State.Ended":
#    print(p.get_state())
#    time.sleep(1)

# ydl_opts = {
    # 'format': 'bestaudio/best',
    # 'postprocessors': [{
        # 'key': 'FFmpegExtractAudio',
        # 'preferredcodec': 'mp3',
        # 'preferredquality': '192',
    # }],
# }
# done = False
# while not done:
    # try:
        # url = input("Video: ")
        # if url.startswith("http"):
            # pass
        # else:
            # url = "ytsearch:" + url
        # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # ydl.download([url])
    # except KeyboardInterrupt:
        # done = True
        # print("Closing")