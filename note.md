Expression 'parameters->channelCount <= maxChans' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 1514
Expression 'ValidateParameters( inputParameters, hostApi, StreamDirection_In )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 2818
Traceback (most recent call last):
  File "/home/alexalvarez/rpi-main/amulet_main.py", line 243, in <module>
    main()
  File "/home/alexalvarez/rpi-main/amulet_main.py", line 178, in main
    stream = audio.open(format=FORMAT,
             ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/dist-packages/pyaudio/__init__.py", line 639, in open
    stream = PyAudio.Stream(self, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/dist-packages/pyaudio/__init__.py", line 441, in __init__
    self._stream = pa.open(**arguments)
                   ^^^^^^^^^^^^^^^^^^^^
OSError: [Errno -9998] Invalid number of channels

ALSA lib pcm.c:2666:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.iec958
ALSA lib pcm.c:2666:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.iec958
ALSA lib pcm.c:2666:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.hdmi
ALSA lib pcm.c:2666:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.hdmi
ALSA lib pcm.c:2666:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.modem
ALSA lib pcm.c:2666:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.modem
ALSA lib pcm.c:2666:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.phoneline
ALSA lib pcm.c:2666:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.phoneline
Cannot connect to server socket err = No such file or directory
Cannot connect to server request channel
jack server is not running or cannot be started
JackShmReadWritePtr::~JackShmReadWritePtr - Init not done for -1, skipping unlock
JackShmReadWritePtr::~JackShmReadWritePtr - Init not done for -1, skipping unlock
Device 0: bcm2835 HDMI 1: - (hw:0,0)
  Input channels: 0
  Output channels: 8
  Default sample rate: 44100.0
Device 1: bcm2835 HDMI 1: - (hw:0,1)
  Input channels: 0
  Output channels: 2
  Default sample rate: 44100.0
Device 2: snd_rpi_googlevoicehat_soundcar: Google voiceHAT SoundCard HiFi voicehat-hifi-0 (hw:1,0)
  Input channels: 0
  Output channels: 2
  Default sample rate: 48000.0
Device 3: sysdefault
  Input channels: 0
  Output channels: 128
  Default sample rate: 44100.0
Device 4: default
  Input channels: 0
  Output channels: 128
  Default sample rate: 44100.0
Device 5: dmix
  Input channels: 0
  Output channels: 2
  Default sample rate: 48000.0

