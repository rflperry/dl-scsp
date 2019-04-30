'''
Adjacency Matrix
Author: Joanna Guo joannaguo@jhu.edu
'''

import numpy as np
import math
import pickle

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

def adjacency_matrix(file, num):
	'''
	Name: adjacency_matrix

	Description: Generates adjacency matrix for each genome string in file
	 
	Inputs: 
	1. file: name of input text file of genome strings
	2. num: number of genome strings in text file
	
	Output:
	adjacency matrix of overlap sequence between each input string
	'''

	# open input file
	with open(file) as f:
		# strip newline and insert each sequence into genomes array
		genomes = [x.strip() for x in f.readlines()]


	# initialize adjacency matrix as empty array
	adj = np.empty([num, num], dtype=str)

	# loop through adjacency matrix to detemine overlaps
	for r in range(num):
		for c in range(num):
			# find overlap for each entry
			adj[r][c] = find_overlap(genomes[r], genomes[c])

	return adj


if __name__ == '__main__':

	print(find_overlap("ABC", "CBD"))

	for i in range(800):
		adj_mat = adjacency_matrix("fragments_" + str(i) + ".txt", 100)
		print(adj_mat)
		file_object = open("pickle_" + str(i), 'wb')
		pickle.dump(adj_mat, file_object)
		file_object.close()
