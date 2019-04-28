P = greedy-superstring
SOURCES = overlap_matrix.c

default: clean $(P)

test: clean debug
	valgrind --leak-check=yes ./$(P) input.txt

debug:
	gcc -g -o $(P) $(SOURCES)

$(P):
	gcc -o $@ $(SOURCES)
	@echo "Usage: greedy-superstring <input_file>"

clean:
	rm -f *.o *.out $(P)

.PHONY: default clean test