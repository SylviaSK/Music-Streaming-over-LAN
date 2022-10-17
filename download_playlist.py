import sys
import youtube_dl
import requests # to get image from the web
import shutil # to save it locally
import xspf_writer as xspf
import add_playlist 


 



class Logger:	
	def __init__(self):
		self.titles = []
		Logger.debug = self.titleTracker
		Logger.warning = self.fakeprint
		Logger.error = self.fakeprint
		
	
	def titleTracker(self, txt):
		# Grab title
		if sum([txt.count(temp) for temp in ["[youtube]", "[youtube:tab]", "[download]", "[ffmpeg]", "Deleting original file"]]) == 0:
			self.titles.append(txt)
			
		# Grab title from "[download] TITLE has already been recorded in archive"
		if txt.count("[download]") == 1 and txt.count("has already been recorded in archive") == 1:
			self.titles.append(txt[11:-37])
		
		# Print anything that gets sent into this function
		print("LOGGER:" + str(txt))		
	
	
	def fakeprint(a = "", b = "", c= ""):
		pass		
	



class PlaylistBuilder():
	def __init__(self, songFilepath = "/home/pi/Music/Playlists", playlistFilepath = "server/resources/playlists", imageFilepath = "server/resources/playlists", htmlFilepath = "server/stream.html"):
		self.songFilepath = PlaylistBuilder.filepath_validity(songFilepath)
		self.playlistFilepath = playlistFilepath
		self.imageFilepath = PlaylistBuilder.filepath_validity(imageFilepath)
		self.htmlFilepath = htmlFilepath
		self.html_writer = add_playlist.HTML_Writer("server/stream.html")
		self.build_ydl()
		
	def filepath_validity(filepath):
		if filepath != "" and filepath[-1] != "/":
			filepath += "/"
		return filepath
		
	def build_ydl(self):
		# Build ydl (as all thats needed beforehand is where to save the files)
		self.logger = Logger()
		downloaderargs = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
		'outtmpl': self.songFilepath+'%(title)s.%(ext)s',
		'download_archive' : self.songFilepath + 'archive.txt',
		'forcetitle' : True,
		'logger' : self.logger
		}
		self.ydl = youtube_dl.YoutubeDL(downloaderargs)
		
		
	def download_MP3(self, playlistURL):
		self.ydl.download([playlistURL])
		return #return list of songs?
	
	
	def download_image(self, imageURL, fileName):
		if imageURL is None:
			return
			
		if fileName[-4] != ".png":
			fileName += ".png"

		# Open the url image, set stream to True, this will return the stream content.
		r = requests.get(imageURL, stream = True)

		# Check if the image was retrieved successfully
		if r.status_code == 200:
			# Set decode_content value to True, otherwise the downloaded image file's size will be zero.
			r.raw.decode_content = True
			
			# Open a local file with wb ( write binary ) permission.
			with open(self.imageFilepath + fileName,'wb') as f:
				shutil.copyfileobj(r.raw, f)
				
			print('Image sucessfully Downloaded: ',fileName)
		else:
			print('Image Couldn\'t be retreived')
			
			
	def create_playlist(self, playlistName):
		w = xspf.XSPFWriter(self.playlistFilepath, playlistName)
		w.write_playlist_from_filepath_list([self.songFilepath + title + ".mp3" for title in self.logger.titles])
			
			
	def build_playlist(self, playlistName, playlistURL, imageURL):
		self.download_MP3(playlistURL)
		self.download_image(imageURL, playlistName)
		self.title_fix()
		self.create_playlist(playlistName)
		self.html_writer.create_playlist(playlistName)
		
	# change titles to match the requirements of the XSPF format. 
		# May move into write_playlist_from_filepath_list and its calls eventually
	def title_fix(self):
		newTitles = []
		replacementStrings = {
		":": " -",
		"\"": "'",
		"/":"_"
		}
		for title in self.logger.titles:
			for original, replacement in replacementStrings.items(): 
				title = title.replace(original, replacement)
			newTitles.append(title)
		self.logger.titles = newTitles
		print(newTitles)


def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)
	return
	
def update_playlist(playlistTitle, playlistURL, imageURL):
	pb = PlaylistBuilder()
	pb.build_playlist(playlistTitle, playlistURL, imageURL)


# Playlist name, Playlist URL, Image URL
if __name__=="__main__":
	pb = PlaylistBuilder()
	try:
		temp = sys.argv[4]
		print("Too many arguements")
	except:
		pb.update_playlist(sys.argv[1], sys.argv[2], sys.argv[3])

	
