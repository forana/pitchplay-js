import os
import tempfile
import base64
import json

SOUNDFONT = "gs-1.4.4.sf2"
CMD_CONVERT_WAV = "fluidsynth -F %(out)s -r 16000 -L 1 " + SOUNDFONT + " %(in)s"
CMD_CONVERT_MP3 = "lame %(in)s %(out)s"
CMD_CONVERT_OGG = "oggenc -o %(out)s --downmix -q 1 %(in)s"

def hexstr(s):
	assert len(s) % 2 == 0
	r = []
	for index in range(0, len(s), 2):
		r.append(chr(int(s[index:index+2], 16)))
	return "".join(r)

"""
Builds and writes out a midi file consisting of a single note being played.

	None of these parameters can exceed a value of 127.

	instrument: the index of the instrument.
	pitch: the MIDI pitch index of the note.
	velocity: the "intensity" with which to play the note.
	duration: number of half-beats for which to play the note (at 120BPM).

	outfile: relative filepath to write the data into.
"""
def buildFile(instrument, pitch, velocity, duration, outfile):
	assert instrument >= 0 and instrument <= 127
	assert pitch >= 0 and pitch <= 127
	assert velocity >= 0 and velocity <= 127
	assert duration > 0 and duration < 128 # maximum number that can be represented in a single variable-length byte

	header = "MThd"
	header += hexstr("00000006") # chunk length. always 6
	header += hexstr("0000") # format 0 (single track)
	header += hexstr("0001") # number of tracks
	header += hexstr("0002") # 2 ticks per beat

	track = "MTrk"
	track += hexstr("0000000B") # track length. cheating here - we'll always know the length is 12 bytes.
	track += hexstr("00C0") + chr(instrument) # set instrument
	track += hexstr("0090") + chr(pitch) + chr(velocity) # note on
	track += chr(duration) + chr(0x80) + chr(pitch) + chr(0) # apply duration and turn the note off afterwards
	track += hexstr("00FF2F") # end of track

	file = open(outfile, "wb")
	file.write(header)
	file.write(track)
	file.close()

def execCmd(cmd):
	print "`" + cmd + "`"
	print os.system(cmd)

def makeConversions(midiFile, wavFile, oggFile, mp3File):
	execCmd(CMD_CONVERT_WAV % {"in": midiFile, "out": wavFile})
	execCmd(CMD_CONVERT_OGG % {"in": wavFile, "out": oggFile})
	execCmd(CMD_CONVERT_MP3 % {"in": wavFile, "out": mp3File})

def b64EncodeFile(file):
	return base64.b64encode(open(file, "rb").read())

def buildBase64Obj(instruments, pitchMin, pitchMax, duration, velocity):
	obj = {}
	d = tempfile.gettempdir()
	midiFile = os.path.join(d, "temp.mid")
	wavFile = os.path.join(d, "temp.wav")
	oggFile = os.path.join(d, "temp.ogg")
	mp3File = os.path.join(d, "temp.mp3")
	for instrument in instruments:
		obj[instrument] = {}
		for pitch in range(pitchMin, pitchMax + 1):
			buildFile(instrument, pitch, velocity, duration, midiFile)
			makeConversions(midiFile, wavFile, oggFile, mp3File)
			obj[instrument][pitch] = {"ogg": b64EncodeFile(oggFile), "mp3": b64EncodeFile(mp3File)}
	os.remove(midiFile)
	os.remove(wavFile)
	os.remove(oggFile)
	os.remove(mp3File)
	return obj

obj = buildBase64Obj([1], 60, 65, 8, 127)
json.dump(obj, open("test.json", 'w'))

