#!/usr/bin/env python
import wave
import numpy as np
import sys

if len(sys.argv) != 4:
	print('./experiment_one.py filename expected_bph ampitude_threshold')
	print('e.g. ./experiment_one.py sample-wavs/t2.wav 14400 0.5')
	exit(-1)

# What bph are we expecting?
near = int(sys.argv[2])
# What is the bph +/- tolerance?
tolerance = 1000
# What is the ampitude threshold for discovering a tick/tock
amp_thresh = float(sys.argv[3])
# Plot the detected peaks?
render = True

#Cleanup window size
window = tolerance * 5

if render:
	import matplotlib.pyplot as plt

# open up a wave
wf = wave.open(sys.argv[1], 'rb')

# Wave properties
swidth = wf.getsampwidth()
rate = wf.getframerate()
# Chunk size is 10s
chunk = rate*10

values = []

# read some data
data = wf.readframes(chunk)
# play stream and find the frequency of each chunk
while len(data) > 0:
	# unpack the data and times by the hamming window
	indata = np.array(wave.struct.unpack("%dh"%(len(data)/swidth), data))
	indata = np.abs(indata)
	maximum = indata.max()
	thresh = amp_thresh * maximum

	for i in range(len(indata)):
		if indata[i] < thresh:
			indata[i] = 0

	reset = False
	for i in range(len(indata)):
		if indata[i] != 0:
			reset = True
		elif reset:
			if indata[i] == 0:
				reset = False
			indata[i] = 0

	for i in range(0, len(indata), window):
		win=indata[i:i+window]
		if win.max() > 0:
			win /= win.max()

	for i in range(window):
		if indata[-i] > 1:
			indata[-i] = 0

	last = 0
	for i in range(len(indata)):
		if indata[i] > 0:
			val = (60*60)/(float(i-last)/rate)
			if val > near - tolerance and val < near + tolerance:
				values.append(val)
			last = i

	if render:
		plt.plot(indata)
		plt.show()
	
	print('Rolling Mean: %.2fbph' %(np.mean(values)))

	data = wf.readframes(chunk)

print('Total Mean: %.2fbph' % (np.mean(values)))
