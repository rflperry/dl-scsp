import numpy as np
import sys

def main(path):
    data = np.genfromtxt(path,skip_header=1)
    print('The mean approx ratio is: %.3f' % np.mean(data[:,4]))
    print('With variance: %.3f' % np.std(data[:,4]))
    print('With max: %.3f' % np.max(data[:,4]))
    print('With min: %.3f' % np.min(data[:,4]))


if __name__ == "__main__":
    main(sys.argv[1])