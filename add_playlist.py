import sys
import fileinput

#declare vars
playlistName = None
# commandline arguements:
# 1st arguement: filepath to file to change
# 2nd arguement and beyond: name of playlists to add

def main():
    spacingStr = "" #it doesn't like being at the top and idk why
    #grab playlist name to add

    try:
        FILEPATH = sys.argv[1]
    except:
        FILEPATH = "server/test.html"
        
    playlistNames = sys.argv[2:]
    if playlistNames == []:
        playlistNames = ["TESTING"]
    
    
    #get base string to drop in
    baseString = []
    with fileinput.FileInput("add_playlist_form.html") as f:
        for line in f:
            baseString.append(line)
    baseString = "".join(baseString)

    #search through file for marker
    with fileinput.FileInput(FILEPATH, inplace = True, backup ='.bak') as f:
        for line in f:
            if "<!-- PYTHON SCRIPT MARKER-->" in line:
                output = ""
                for name in playlistNames:
                    temp = baseString.replace("INPUT", name) # fill in name
                    # TODO deal with indentation even though it isnt 100% nessecary:
                    output += temp
                output += line #python script marker
                print(output[:-1], end='')
            else:
                print(line, end='')
    eprint(playlistNames,"successfully added.")
       
#def get
                                 
#for debug
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__=="__main__":
    main()
