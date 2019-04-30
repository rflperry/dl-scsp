'''
Adjacency Matrix
Author: Joanna Guo joannaguo@jhu.edu
'''

import numpy as np
import math
import pickle
# import node2vec.py

def find_overlap(first, second):
	'''
	Name: find_overlap

	Description: find the longest overlap between the suffix of the first string and the prefix of the second string

	Inputs:
	1. first: the first genome string to find overlap in suffix
	2. second: the second genome string to find overlap in prefix

	Output:
	longest overlapping string
	'''

	# save length of the shortest string input
	length = min(len(first), len(second))
	
	# reverse the first string
	rev = first[::-1]
	
	# set overlap index to 0
	i = 0

	# loop over strings to compare characters
	while i < length and rev[i] == second[i]:
		i += 1

	# return overlap sequence
	return second[0:i]

def adjacency_matrix(file, num, index, write=False):
	'''
	Name: adjacency_matrix

	Description: Generates adjacency matrix for each genome string in file
	 
	Inputs: 
	1. file: name of input text file of genome strings
	2. num: number of genome strings in text file
	3. index: write index
	4. write: default false, if true write edgelist to file
	
	Output:
	adjacency matrix of overlap sequence between each input string
	'''

	# open input file
	with open(file) as f:
		# strip newline and insert each sequence into genomes array
		genomes = [x.strip() for x in f.readlines()]


	# initialize adjacency matrix as empty array
	adj = np.empty([num, num], dtype=int)
	# adj = np.empty([num, num], dtype=object)

	# set file as unopened
	opened = False

	# loop through adjacency matrix to detemine overlaps
	for r in range(num):
		for c in range(num):
			# find length of overlap for each entry
			adj[r][c] = len(find_overlap(genomes[r], genomes[c]))

			if(write):
			# if there is overlap
				if adj[r][c] != "":
					if not opened:
						file = open("adj" + str(index) + ".edgelist", "a+")
						opened = True
					# append overlap to file
					file.write(str(r) + " " + str(c) + " " + str(adj[r][c]) + "\n")

	if opened:
		file.close()

	return adj


if __name__ == '__main__':

	for i in range(800):

		# define values
		adjacency = adjacency_matrix("fragments_" + str(i) + ".txt", 100, i, True)
		
		print(i)
