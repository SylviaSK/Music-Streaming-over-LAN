# server.py
# Note: This requires xdotool and vlc installed
import http.server # Our http server handler for http requests
import socketserver # Establish the TCP Socket connections
import subprocess
import copy #reduce to j deepcopy if i remember
import sys
import cgi
from collections import namedtuple

#dummy class to enable .kill() to be called on currentStream before it
#gets assigned to a real subprocess
class killBox():
    def kill():
        return
## Initialize from config
#with open config
debug = True
PORT = 8000
errorMessagePage = "server/resources/error.html"
#use cvlc to remove interface, vlc to keep
templatePlaylistArgs = ['vlc', 'server/resources/playlists/', '--sout=#transcode{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100,scodec=none}:duplicate{dst=http{dst=:8080/stream.mp3},dst=display}', '--sout-keep', '-L']
nextSongCommand = ['xdotool', 'key', 'alt+l', 'key', 'x']
prevSongCommand = ['xdotool', 'key', 'alt+l', 'key', 'v']

ResponseStatus = namedtuple("HTTPStatus", ["code", "message"])
NO_CONTENT = ResponseStatus(code=204, message="No Content")
currentStream = killBox
temporarySubprocess = killBox

with open(errorMessagePage) as file:
    errorMessagePage = file.read()


        
def playPlaylist(playlist):
    global currentStream
    currentStream.kill()
    temp = copy.deepcopy(templatePlaylistArgs)
    temp[1] += playlist + ".xspf" #callingObject.path[10:].replace("%20", " ") 
    print("Swapping to playlist", playlist)
    currentStream = subprocess.Popen(temp)
    
def handleControls(controls):
    if controls == "nextSong" :
            temporaryCommandlineCall(nextSongCommand)
            eprint("Skipping current Song")
    elif controls == "prevSong":
        temporaryCommandlineCall(prevSongCommand)
        eprint("Going back to previous Song")

# creates a commandline call that will be killed when this function is called again.
# TODO: aen improvement would involve making this spin off a new thread/child and just killing it as soon as it completes
def temporaryCommandlineCall(command):
    global temporarySubprocess
    temporarySubprocess.kill()
    temporarySubprocess = subprocess.Popen(command)
    


class httpRequestHandler(http.server.SimpleHTTPRequestHandler):
            
    def do_GET(self):
        if self.path == "/":
            self.path = "/stream.html"
            
        self.path = "/server" + self.path
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
 
    def do_POST(self):
        #self.printContents()
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE':self.headers['Content-Type']}
        )
        
        # pull up the playlist
        playlistName = form.getvalue("playlistName")
        print(playlistName)
        if playlistName != None:
            playPlaylist(playlistName)
            eprint("Playing:", playlistName)
            self.send_response(NO_CONTENT.code, NO_CONTENT.message)
            self.end_headers()
            return
        
        # song controls
        controls = form.getvalue("controls")
        print(controls)
        if controls != None:
            handleControls(controls)
            self.send_response(NO_CONTENT.code, NO_CONTENT.message)
            self.end_headers()
            return
        
    def send_error(self, code, message=None):
        handleButtonLinks(self)
            
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
    if debug:
        print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    handler = httpRequestHandler
     
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("Http Server Serving at port", PORT)
        httpd.serve_forever()
    

