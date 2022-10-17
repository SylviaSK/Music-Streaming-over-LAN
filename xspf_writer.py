import eyed3

class XSPFWriter:
    #TO
    ESCAPING_MAP = {   
        "%": "%25",
        ";": "%3B",
        "&": "&amp;",
        "#": "%23",
        "`": "%60",
        "^": "%5E",
        "[": "%5B",
        "]": "%5D",
        "{": "%7B",
        "}": "%7D",
        "\\": "%5C",
        "|": "%7C",
        "<": "%3C",
        ">": "%3E",
        "?": "%3F",
        "'": "&#39;",
        '"': "%22",
        " ": "%20"
    }

    #open new file
    def __init__(self, filepath : str, filename : str):
        if filepath != "" and filepath[-1] != "/":
            filepath += "/"
        if filename[-5] != ".xspf":
            if filename.count(".") == 0:
                filename += ".xspf"
            else:
                raise Exception("Filepath contains '.' but does not end in .xspf")
        self.f = open(filepath + filename, "w")
        self.filepath = filepath

        self.filename = filename
        self.indentLvl = 0
        self.numTracks = 0
        
        
    def write(self, txt : str):
        writeStr = "	" * self.indentLvl + txt + "\n"
        self.f.write(writeStr)
        
        
    def _escape_location(self, location):
        for unescaped, escaped in XSPFWriter.ESCAPING_MAP.items():
            location = location.replace( unescaped, escaped)
        return location
        

    def _write_atribute(self, atribute : str, value : str):
        if str(value) == "None":
            return
        self.write("<" + atribute + ">" + value + "</" + atribute + ">")
        

    #add basic XSPF/VLC info
    def begin(self):
        self.write('<?xml version="1.0" encoding="UTF-8"?>')
        self.write('<playlist xmlns="http://xspf.org/ns/0/" xmlns:vlc="http://www.videolan.org/vlc/playlist/ns/0/" version="1">')
        self.indentLvl += 1
        self.write('<title>Playlist</title>')
        self.write('<trackList>')
        self.indentLvl += 1


    def write_track(self, trackInfo : dict):
        self.write('<track>')
        self.indentLvl += 1
        
        for item in trackInfo.items():
            self._write_atribute(item[0], str(item[1]))
            
        self.write('<extension application="http://www.videolan.org/vlc/playlist/0">')
        self.indentLvl += 1
        self.write('<vlc:id>' + str(self.numTracks) + '</vlc:id>')
        self.indentLvl -= 1
        self.write('</extension>')
        self.indentLvl -= 1
        self.write('</track>')
        self.numTracks += 1


    #add ending VLC/XSPF info
    def end(self):
        self.indentLvl -= 1
        self.write('</trackList>')
        self.write('<extension application="http://www.videolan.org/vlc/playlist/0">')
        self.indentLvl += 1
        for i in range(self.numTracks):
            self.write('<vlc:item tid="' + str(i) + '"/>')
        self.indentLvl -= 1
        self.write('</extension>')
        self.indentLvl -= 1
        self.write('</playlist>')


    def write_track_from_file(self, filepath : str):
        self.write_track(self.get_info(filepath))
    
    
    def get_info(self, filepath : str):
        track = eyed3.load(filepath)
        out = dict()
        out['location'] = "file://" + self._escape_location(filepath)
        out['title'] = track.tag.title 
        out['creator'] = track.tag.artist
        out['album'] = track.tag.album
        out['duration'] = int(track.info.time_secs * 1000)
        return out
        
    def write_playlist_from_filepath_list(self, filepathList):
        self.begin()
        for track in filepathList:
            self.write_track_from_file(track)
        self.end()
        
        
if __name__ == "__main__":
    xspf = XSPFWriter("", "testoutput.xspf")
    xspf.write_playlist_from_filepath_list(["FFXIV OST - Alexander: Cruise Chaser's Theme (Exponential Entropy).mp3"])
