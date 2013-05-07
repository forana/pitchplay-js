import os
import tempfile
import base64
import json
import argparse

DEFAULT_VELOCITY = 100

SOUNDFONT = "gs-1.4.4.sf2"
CMD_CONVERT_WAV = "fluidsynth -F %(out)s -r 16000 -L 1 " + SOUNDFONT + " %(in)s"
CMD_CONVERT_MP3 = "lame %(in)s %(out)s"
CMD_CONVERT_OGG = "oggenc -o %(out)s --downmix -q 1 %(in)s"

"""
Utility to convert a hexidecimal string to the corresponding string containing the represented characters.
"""
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

"""
Execute a command, printing both the names and the results. This is done to give the user a sense of progress, but also
to show errors, since I have no quick and easy way to detect / show these.
"""
def execCmd(cmd):
	#print "`" + cmd + "`"
	os.system(cmd)

"""
Given an existing MIDI file, creates an OGG and an MP3 converted copy, using a wave file as a middleman.
"""
def makeConversions(midiFile, wavFile, oggFile, mp3File):
	execCmd(CMD_CONVERT_WAV % {"in": midiFile, "out": wavFile})
	execCmd(CMD_CONVERT_OGG % {"in": wavFile, "out": oggFile})
	execCmd(CMD_CONVERT_MP3 % {"in": wavFile, "out": mp3File})

"""
Base 64 URL encode a single file as a URL, returning the result.
"""
def b64EncodeFile(file, mime):
	return "data:" + mime + ";base64," + base64.b64encode(open(file, "rb").read())

"""
Build and returns a dictionary of the base64 URL representations of both ogg and mp3 versions of an instrument through various configurations.

	instrument: the MIDI instrument index of the desired instrument.
	pitchMin: the lowest MIDI pitch to generate.
	pitchMax: the highest MIDI pitch to generate. All pitches between the min and max (inclusive) will be generated.
	duration: the number of half-beats for which to sustain each pitch, at 120 BPM at 4/4 time.
	velocity: the velocity with which to strike each note.
"""
def buildBase64URLDict(instrument, pitchMin, pitchMax, duration, velocity):
	obj = {}
	d = tempfile.gettempdir()
	midiFile = os.path.join(d, "temp.mid")
	wavFile = os.path.join(d, "temp.wav")
	oggFile = os.path.join(d, "temp.ogg")
	mp3File = os.path.join(d, "temp.mp3")
	for pitch in range(pitchMin, pitchMax + 1):
		buildFile(instrument, pitch, velocity, duration, midiFile)
		makeConversions(midiFile, wavFile, oggFile, mp3File)
		obj[pitch] = {"ogg": b64EncodeFile(oggFile, "audio/ogg"), "mp3": b64EncodeFile(mp3File, "audio/mp3")}
	os.remove(midiFile)
	os.remove(wavFile)
	os.remove(oggFile)
	os.remove(mp3File)
	return obj

parser = argparse.ArgumentParser(description = "Generate a JSON file containing base64-encoded mp3 and ogg versions of single notes being played.")
parser.add_argument("instrument", type=int, help = "MIDI index of the instrument to use.")
parser.add_argument("pitchMin", type=int, help = "Minimum MIDI pitch to generate (middle C = 60, min = 0).")
parser.add_argument("pitchMax", type=int, help = "Maximum MIDI pitch to generate (middle C = 60, max = 127).")
parser.add_argument("duration", type=int, help = "Number of half-beats for which to play each pitch, at 120BPM in 4/4 time.")
parser.add_argument("outfile", type=str, help = "File to write the output to.")
args = parser.parse_args()

dict = buildBase64URLDict(args.instrument, args.pitchMin, args.pitchMax, args.duration, DEFAULT_VELOCITY)
json.dump(dict, open(args.outfile, 'w'))
