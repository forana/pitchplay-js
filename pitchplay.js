/*
2013 Alex Foran
*/
PitchPlay = {
	banks: {},

	load: function(url, targetBank, onSuccess, onError, onProgress) {
		var req = new XMLHttpRequest();
		var self = this;

		req.addEventListener("load", function(e) {
			self.banks[targetBank] = JSON.parse(req.responseText);
			if (onSuccess) {
				onSuccess();
			}
		});

		if (onError) {
			req.addEventListener("error", onError);
		}
		if (onProgress) {
			req.addEventListener("progress", onProgress);
		}

		req.open("get", url, true);
		req.send();
	},

	_createAudio: function(note) {
		var a = new Audio();
		var oggElement = document.createElement("source");
		oggElement.src = note.ogg;
		oggElement.type = "audio/ogg";
		a.appendChild(oggElement);
		var mp3Element = document.createElement("source");
		mp3Element.src = note.mp3;
		mp3Element.type = "audio/mp3";
		a.appendChild(mp3Element);
		return a;
	},

	play: function(bank, notes, offsets) {
		var totalOffset = 0;
		for (var i=0; i<notes.length; i++) {
			var offset = (i > 0 &&
				offsets &&
				offsets.length >= i) ?
				offsets[i - 1] :
				0;
			totalOffset += offset;

			setTimeout((function(note) {
				var audio = PitchPlay._createAudio(note);
				return function() {
					audio.play();
				}
			})(bank[notes[i]]), totalOffset);
		}
	}
};