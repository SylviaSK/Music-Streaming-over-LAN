# server.py
# Note: This requires xdotool and vlc installed
from config_importer import grab_config
import http.server # Our http server handler for http requests
import socketserver # Establish the TCP Socket connections
import subprocess # run commands in commandprompt
import copy #reduce to j deepcopy if i remember
import sys #only used in eprint, if that ever gets removed kill this
import cgi #handle POST functionality
from collections import namedtuple #consider removing
import download_playlist
from time import sleep

#dummy class to enable .kill() to be called on currentStream before it
#gets assigned to a real subprocess
class killBox():
    def kill():
        return
    
## Initialize from config
config = grab_config("server.config")


templatePlaylistArgs = ['vlc', 'server/resources/playlists/', '--sout=#transcode{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100,scodec=none}:duplicate{dst=http{dst=:'+ str(config["streamport"]) +'/stream.mp3},dst=display}', '--sout-keep', '-L']
if not config["vlcinterface"]:
    templatePlaylistArgs[0] = "cvlc"
    
nextSongCommand = ['xdotool', 'key', 'alt+l', 'key', 'x']
prevSongCommand = ['xdotool', 'key', 'alt+l', 'key', 'v']

ResponseStatus = namedtuple("HTTPStatus", ["code", "message"])
NO_CONTENT = ResponseStatus(code=204, message="No Content")
currentStream = killBox
temporarySubprocess = killBox
addPlaylistSubprocessess = killBox
maxSocketBindAttempts = 60

with open(config["errorpage"]) as file:
    errorMessagePage = file.read()

        
def playPlaylist(form):
    playlist = form.getvalue("PLAYLISTNAME")
    
    global currentStream
    currentStream.kill()
    command = copy.deepcopy(templatePlaylistArgs)
    command[1] += playlist + ".xspf" 
    eprint("Swapping to playlist", playlist)
    currentStream = subprocess.Popen(command)
  
    
def handleControls(form):
    controls = form.getvalue("CONTROLS")
    
    if config["vlcinterface"]:
        if controls == "nextSong":
            temporaryCommandlineCall(nextSongCommand)
            eprint("Skipping current Song")
        elif controls == "prevSong":
            temporaryCommandlineCall(prevSongCommand)
            eprint("Going back to previous Song")
  
            
def createPlaylist(form):
    playlistTitle = form.getvalue("playlistName")
    playlistURL = form.getvalue("playlistURL")
    imageURL = form.getvalue("imageURL")
    
    print(f"playlistTitle: {playlistTitle}")
    print(f"playlistURL: {playlistTitle}")
    print(f"imageURL: {imageURL}")
    
    
    download_playlist.update_playlist( playlistTitle, playlistURL, imageURL) 
    

# creates a commandline call that will be killed when this function is called again.
# TODO: an improvement would involve making this spin off a new thread/child and just killing it as soon as it completes
    #maybe colapse subprocess handling into a class?
def temporaryCommandlineCall(command, container = temporarySubprocess):
    global addPlaylistSubprocessess
    global temporarySubprocess
    container.kill()
    container = subprocess.Popen(command)
    
class httpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = config["serverfolder"] + self.path
        if self.path == config["serverfolder"] + "/":
            self.path = config["streampage"]
            
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
 
    def do_POST(self):
        #self.printContents()
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE':self.headers['Content-Type']}
        )
        
        # handle forms
        for key, function in formValues.items():
            if form.getvalue(key)!= None:
                function(form)
        self.send_response(NO_CONTENT.code, NO_CONTENT.message)
        self.end_headers()
        return
        
    def send_error(self, code, message=None):            
        self.error_message_format = errorMessagePage
        http.server.SimpleHTTPRequestHandler.send_error(self, code, message)

    #prints every bit of info I know that a SimpleHTTPRequestHandler has
    def printContents(self):
        print("client_address:", self.client_address)
        print("close_connection:", self.close_connection)
        print("requestline:", self.requestline)
        print("command:", self.command)
        print("path:", self.path)
        print("request_version:", self.request_version)
        print("headers:", self.headers)
        print("rfile:", self.rfile)
        print("wfile:", self.wfile)


def eprint(*args, **kwargs):
    if config["debug"]:
        print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    print("Starting server...")
    global formValues
    socketBindCounter = 0
    formValues = {"PLAYLISTNAME": playPlaylist, "CONTROLS": handleControls, "ADDPLAYLIST": createPlaylist}
    while True:
        try:
            with socketserver.TCPServer((config["ip"], config["port"]), httpRequestHandler) as httpd:
                print("Http Server Serving at port", config["port"])
                httpd.serve_forever()
        except Exception as error:
            print(error)
            sleep(.1)
            if socketBindCounter >= maxSocketBindAttempts:
                print("Socket still bound, ending process")
                sleep(5)
                break
            else:
                socketBindCounter += 1
            continue
        
    

