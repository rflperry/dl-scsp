#!/bin/bash
for f in {0..799}
do
	echo "Processing $f file"
	python main.py --input adj$f.edgelist --output adj$f.emb --weighted --directed
done