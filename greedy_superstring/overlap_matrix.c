// Read from file many strings and find the shortest superstring using greedy algorithm
// USAGE: <executable> <input_file>
// OUTPUT: <shortest_superstring>

#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_READ_LENGTH 200

/** Compute max overlap between a suffix of read1 and a prefix of read2
 * @param read1: first string processed
 * @param read2: second string processed
 * @param length1: first string length (to avoid computing it every time)
 * @param length2: second string length (to avoid computing it every time)
 * @return max overlap. Returns strlen(read2) if and only if read2 is contained in its entirety in read1.
 */ 
size_t overlap(char* read1, char* read2, size_t length1, size_t length2) {
    size_t max_overlap = 0;
    
    // i must be declared as int because size_t vars can't go <0
    for (int i = length1-1; i >= 0; i = i-1) {
        size_t j = 0;  // current number of overlapping characters
        bool overlapping = true;
        while (j < length2 && i+j < length1 && overlapping) {
            if (read1[i+j] != read2[j]) {
                overlapping = false;
            } else {
                j = j+1;
            }
        }
        // We have 3 cases for the cycle to exit:
        // 1) j == length2 means that read2 is a substring of read1
        // this means that no other best solution can be found
        if (j == length2) {
            return length2;
        }
        // 2) i+j == length1 means a prefix of read2 is a suffix of read1
        // Candidate to be the best local overlap
        if (i+j == length1) {
            max_overlap = j;
        }
        // 3) overlapping == false means that we must go on
    }
    return max_overlap;
}

/** Compute overlap between 2 reads without knowing their lenghts
 * Helper of: overlap(char*, char*, size_t, size_t)
 * @param read1: first read
 * @param read2: second read
 * @return overlap between read1 and read2
 */
size_t overlap_unfixed(char* read1, char* read2) {
    size_t length1 = strlen(read1);
    size_t length2 = strlen(read2);
    return overlap(read1, read2, length1, length2);
}

/** Read a file line by line and count # of lines
 * @param filename: name of the file to be read
 * @param lines: pointer to number of lines
 * @return char** with allocated memory containing every line of the file
 * It saves the # of lines at (*lines)
 */
char** from_file(char* filename, size_t* lines) {
    FILE* input_file;
    input_file = fopen(filename, "r");
    assert(input_file != NULL && "Input file not found");

    char temp_read[MAX_READ_LENGTH];
    // Count lines and check that lines is a real pointer
    if (lines == NULL)
        lines = malloc(sizeof(size_t));
    size_t n = 0;
    while (fgets(temp_read, MAX_READ_LENGTH, input_file)) {
        n = n+1;
    }
    assert(n >= 1 && "File hasn't enough lines");

    rewind(input_file);     // Return to the beginning of file
    // Now read every single line
    char** reads = malloc(n * sizeof(char*));
    assert(reads != NULL && "Can't allocate enough memory");

    // '\n' is counted as a valid character in file strings so we have to strip it
    // This is done by inserting a terminator ('\0') at the last position
    // NB: We don't have to strip it from the last read
    for (size_t i = 0; i < n-1; i = i+1) {
        assert(fgets(temp_read, MAX_READ_LENGTH, input_file) && "Cannot read from file\n");
        temp_read[strlen(temp_read)-1] = '\0';
        reads[i] = strdup(temp_read);
    }
    assert(fgets(temp_read, MAX_READ_LENGTH, input_file) && "Cannot read from file\n");
    // Check if last line has '\n' or not
    if (temp_read[strlen(temp_read) - 1] == '\n')
        temp_read[strlen(temp_read)-1] = '\0';
    reads[n-1] = strdup(temp_read);

    fclose(input_file);
    
    // return reads and # of lines counted
    (*lines) = n;
    return reads;
}


/** Given an array of strings, and its length, returns and array of size_t
 * containing lengths line by line
 * @param reads: array of strings that has to be counted
 * @param n: # of strings
 * @return size_t* to allocated memory with computed lengths that has to be freed
 */
size_t* compute_lengths(char** reads, size_t n) {
    size_t* lengths = malloc(n * sizeof(size_t));
    for (size_t i = 0; i < n; i = i+1) {
        lengths[i] = strlen(reads[i]);
    }
    return lengths;
}

int main (int argc, char** argv) {
    // Must be: <executable> <input_file>
    assert(argc > 1 && "Need one additional argument (filename)");

    size_t *lines = malloc(sizeof(size_t));   // Number of reads (file lines)
    char** reads = from_file(argv[1], lines);
    size_t n = (*lines);

    // Save reads lengths to avoid recomputing them every time
    size_t* lengths = compute_lengths(reads, n);

    /** Compute overlaps between every pair of reads and save them into a matrix
     * overlap matrix is n*n and it's not symmetric: for every pair (i,j), overlap
     * is computed as the overlap of a suffix of i to a prefix of j
     */
    int** overlap_matrix = malloc(n * sizeof(int*));
    assert(overlap_matrix != NULL && "Cannot allocate more memory");
    for (size_t i = 0; i < n; i = i+1) {
        overlap_matrix[i] = malloc(n * sizeof(int));
        assert(overlap_matrix[i] != NULL && "Cannot allocate more memory");
    }

    for (size_t i = 0; i < n; i = i+1) {
        for (size_t j = 0; j < n; j = j+1) {
            if (i != j)
                overlap_matrix[i][j] = overlap(reads[i], reads[j], lengths[i], lengths[j]);
            else
                overlap_matrix[i][j] = -1; // Do not calculate overlap between same strings
        }
    }

    bool* used_strings = malloc(n * sizeof(bool));
    assert(used_strings != NULL && "Cannot allocate more memory");
    for (size_t i = 0; i < n; i = i+1) {
        used_strings[i] = false;
    }
    
    // For n-1 times I have to melt the two most overlapping strings
    // Compute n-1 times the max on a matrix (This has to be improved)
    for (size_t h = 0; h < n-1; h = h+1) {
        int max = -1;
        size_t ii, jj;    // temp indexes
        for (size_t i = 0; i < n; i = i+1) {
            if (used_strings[i] == true)    // Skip used strings
                continue;
            
            for (size_t j = 0; j < n; j = j+1) {
                if (i == j || used_strings[j] == true)  // do not count same strings and used ones
                    continue;

                if (overlap_matrix[i][j] > max) {
                    max = overlap_matrix[i][j];
                    ii = i;
                    jj = j;
                }
            }
        }
        used_strings[jj] = true;    // Mark jj as used
        if (max == lengths[jj])
            // reads[jj] is contained in its entirety in reads[ii] so:
            // * don't have to melt them
            // * don't have to compute again overlaps
            continue;

        reads[ii] = realloc(reads[ii], lengths[ii] + lengths[jj] - max + 1);
        assert(reads[ii] != NULL);
        // melt reads[ii] and reads[jj] so that the suffix of ii is prefix of jj by max characters
        strcat(reads[ii], reads[jj]+max);
        // Save updated length
        lengths[ii] = lengths[ii] + lengths[jj] - max;

        // Compute again new overlaps ONLY for new melt string
        for (size_t i = 0; i < n; i = i+1) {
            if (used_strings[i] == false && i != ii) {
                overlap_matrix[i][ii] = overlap(reads[i], reads[ii], lengths[i], lengths[ii]);
                overlap_matrix[ii][i] = overlap(reads[ii], reads[i], lengths[ii], lengths[i]);
            }
        }
    }
    // Resulting superstring is found in the unique "false" position
    for (size_t i = 0; i < n; i = i+1) {
        if (used_strings[i] == false)
            printf("%s\n", reads[i]);
    } 

    // Cleanup dynamic memory
    for (int i = 0; i < n; i = i+1) {
        free(reads[i]);
        free(overlap_matrix[i]);
    }
    free(reads);
    free(overlap_matrix);
    free(lengths);
    free(lines);
    free(used_strings);
    return 0;
}