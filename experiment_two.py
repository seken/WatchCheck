#!/usr/bin/env python
import wave
import numpy as np
import sys

if len(sys.argv) != 3:
	print('./experiment_two.py filename ampitude_threshold')
	print('e.g. ./experiment_two.py sample-wavs/t2.wav 0.5')
	exit(-1)

# What bph are we expecting?
near = [10660, 18000, 21600, 28800, 36000, 16200, 14400]
# What is the bph +/- tolerance?
tolerance = 1000
# What is the ampitude threshold for discovering a tick/tock
amp_thresh = float(sys.argv[2])
# Plot the detected peaks?
render = False

#Cleanup window size
window = tolerance * 5

if render:
	import matplotlib.pyplot as plt

def time_lost(design, actual):
	""" returns the seconds gained per day as opposed to the design bph """
	seconds_per_hour = 60 * 60
	per_day = 24

	return ((float(actual)/(float(design)/seconds_per_hour)) - seconds_per_hour)*per_day

# open up a wave
wf = wave.open(sys.argv[1], 'rb')

# Wave properties
swidth = wf.getsampwidth()
rate = wf.getframerate()
# Chunk size is 10s
chunk = rate*10

values = dict([(n, []) for n in near])
nt = dict([(n, 0) for n in near])

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
		else:
			indata[i] = 1

	reset = 0
	for i in range(len(indata)):
		if reset > 0:
			indata[i] = 0
			reset -= 1
		elif indata[i] >  0:
			reset = window

	last = 0
	for i in range(len(indata)):
		if indata[i] == 1:
			val = (60*60)/(float(i-last)/rate)
			for n in near:
				if val > n - tolerance and val < n + tolerance:
					values[n].append(val)
					nt[n] += 1
				last = i

	if render:
		plt.plot(indata)
		plt.show()
	
	data = wf.readframes(chunk)

for bph, c in nt.iteritems():
	if len(values[bph]) > 0:
		actual = np.mean(values[bph])
		print ('%dbph matched %d times, mean %.2fbph, seconds gained per day %0.3f'%(bph, c, actual, time_lost(bph, actual)))
