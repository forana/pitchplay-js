PitchPlay
==========
This is a javascript library (with data generated via python script) for playing midi notes in a web browser.

Browsers supported: theoretically, the latest chrome, firefox, and IE (10+) should work, but I can't guarantee it.

[Check out the demo!](http://alexforan.com/pitchplay-js/)

Dependencies for build script (build.py):
- fluidsynth, or another program that can convert midi to wave
- oggenc, or another program that can convert wave to ogg
- lame, or another program that can convert wave to mp3
- python 2.7+

The python script has some decently robust documentation; run it with --help for usage info.

More info on MIDI pitches: http://www.phys.unsw.edu.au/jw/notes.html<br/>
More info on MIDI instruments: http://www.midi.org/techspecs/gm1sound.php<br/>
The GS soundfont included in this repo is free for personal and commercial use: http://www.schristiancollins.com/generaluser.php<br/>

written 2013 Alex Foran