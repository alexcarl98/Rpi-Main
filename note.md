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

