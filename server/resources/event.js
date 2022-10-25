

// When an artist image is clicked, swap shown/hidden of all child playlist things
jQuery(function(){
  jQuery('.artist-overlay').click(function(){
	var artist = jQuery(this).closest('.artist-wrapper').data('artist');
	var parent = jQuery(this).closest('.flexWrap');
	var artistObject = jQuery(this).closest('.artist-wrapper')
	console.log(artist)
	console.log(parent)
	
	var artistPlaylists = parent.find('[data-artist="' + artist + '"]').filter('.playlist-wrapper')
	console.log(artistPlaylists) 
	 
	if (artistPlaylists.is(":hidden") ){
		artistPlaylists.fadeIn()}
	else { artistPlaylists.fadeOut()}
	artistObject.fadeOut()
    });
});
