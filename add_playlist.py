import sys
import fileinput

#declare vars
FILEPATH = "/home/pi/Public/server/stream.html"
playlistName = None
#a big hardcoded block that is the basis for this 'form filling'
theBigList = ["space",
			  "<a href=\"/playlist.",
			  playlistName,
			  "\">\n",
			  "space",
			  "  <div class=\"playlist-container\">\n",
			  "space",
			  "    <img src=\"/resources/playlists/",
			  playlistName,
			  ".png\" alt=\"",
			  playlistName, 
			  " playlist image\" class=\"playlist-image\">\n",
			  "space",
			  "    <div class=\"playlist-overlay\"></div>\n",
			  "space",
			  "    <div class=\"playlist-text\">",
			  playlistName,
			  "</div>\n",
			  "space",
			  "  </div>\n",
			  "space",
			  "</a>\n",
			  "<!-- PYTHON SCRIPT MARKER-->"]

def main():
	spacingStr = "" #it doesn't like being at the top and idk why
	#grab playlist name to add
	playlistName = sys.argv[1]
	
	#search through file for marker
	with fileinput.FileInput(FILEPATH, inplace = True, backup ='.bak') as f:
		for line in f:
			if "<!-- PYTHON SCRIPT MARKER-->" in line:
				pass
				#add proper spacing to the strings
				for i in range(len(theBigList)):
					if theBigList[i] == "space":
						theBigList[i] = spacingStr
				#replace the blanks with the playlist name
				for i in range(len(theBigList)):
					if theBigList[i] == None:
						theBigList[i] = playlistName
				output = "".join(theBigList)
				print(line.replace("<!-- PYTHON SCRIPT MARKER-->", output), end='')
			else:
				spacingStr = " "*max(len(line)-5, 0)
				print(line, end='')
	eprint(playlistName,"successfully added.")
#for debug
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__=="__main__":
	main()
