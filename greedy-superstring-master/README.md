# Greedy approximation algorithm to find shortest common superstring

## Computational complexity

Given `n` reads of `k` max characters (`k` is hardcoded):

* `overlap` = `O(k^2)` -> overlap between 2 reads
* `from_file` = `O(n*k)` -> read input
* `compute_lengths` = `O(n*k)` -> count and save reads lenghts

Build the Dynamic Programming matrix `[n, n]` for overlaps costs `overlap` for every cell. So `O(n^2*k^2)`.

Computing max `n-1` times on the overlaps matrix costs `O(n^3)`.

So total computational time is: `O(n^2*k^2 + n^3)`.

## Usage

Make it and run it passing as first argument the file containing input:

        make
        ./greedy-superstring <input_file>

As a working example, we include `input.txt`. Try running this:

        ./greedy-superstring input.txt

Output will be the shortest superstring found.

## Input format

The file containing reads must be made of a # of lines without blank lines at the end.

Every line is read as a single string. Check `input.txt` as an example file