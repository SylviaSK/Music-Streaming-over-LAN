import sys
import fileinput

pythonMarker = "<!--PYTHON SCRIPT MARKER-->"


# commandline arguements:
# 1st arguement: filepath to file to change
# 2nd arguement and beyond: name of playlists to add
class HTML_Writer:
    def __init__(self, htmlFilepath = "server/test.html", formFilepath = "add_playlist_form.html"):
        self.htmlFilepath = htmlFilepath
        self.htmlString = HTML_Writer.file_to_string(htmlFilepath) 
        self.formString = HTML_Writer.file_to_string(formFilepath)

    def file_to_string(filepath):
        baseString = []
        num = 0
        with fileinput.FileInput(filepath) as f:
            for line in f:
                if "\n" in line:
                    num += 1
                baseString.append(line)
        eprint(num)
        return "".join(baseString)


    def create_multiple_playlists(self, playlistNames):
        if type(playlistNames) == type(''):
            playlistNames = [playlistNames]

        for playlist in playlistNames:
            self.create_playlist(playlist)


    def create_playlist(self, playlist):
        #Check if playlist is in already, and skip
        if "<!-- Playlist: " + playlist + " -->" in self.htmlString:
            eprint(playlist, "was not added, as it was found in the file")
            return

        #search through file for marker
        with fileinput.FileInput(self.htmlFilepath, inplace = True, backup ='.bak') as f:
            for line in f:
                if pythonMarker in line:
                    try:
                        eprint(line)
                        indentation = line[:-1].replace(pythonMarker, "") #cut off \n and marker
                        eprint(indentation + "! This is the indentation test")
                        output = self.formString.replace("INPUT", playlist) # fill in name
                        output = output.replace("\n", "\n" + indentation)
                        output += pythonMarker
                        output = indentation + output
                        print(output, end='\n')
                    except:
                        eprint("Unable to add playlist during write process, defaulting to rewriting the base")
                        print(line, end='')
                else:
                    print(line, end='')
        eprint(playlist,"successfully added.")



#for debug
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__=="__main__":
    try:
        filepath = sys.argv[1]
    except:
        filepath = "server/test.html"
        
    #grab playlist name to add

    playlistNames = sys.argv[2:]
    if playlistNames == []:
        playlistNames = ["TESTING"]

    writer = HTML_Writer()
    writer.create_multiple_playlists(playlistNames)
