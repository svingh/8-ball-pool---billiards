CC=gcc
SWIG=swig
CFLAGS=-fPIC -Wall -std=c99
LDFLAGS=-shared
PYTHON_INCLUDE=$(shell python3-config --includes)
PYTHON_LIB=$(shell python3-config --libs)

all: _phylib.so

# Target for position independent object file
phylib.o: phylib.c
	$(CC) $(CFLAGS) -c phylib.c -o phylib.o

# Target for shared library
libphylib.so: phylib.o
	$(CC) $(LDFLAGS) phylib.o -o libphylib.so

# Generate Python interface files
phylib_wrap.c phylib.py: phylib.i
	$(SWIG) -python phylib.i

# Target for SWIG generated object file
phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) $(PYTHON_INCLUDE) -c phylib_wrap.c -o phylib_wrap.o

# Target for shared object library used by Python
_phylib.so: phylib_wrap.o phylib.o
	$(CC) $(LDFLAGS) phylib_wrap.o phylib.o $(PYTHON_LIB) -o _phylib.so

# Clean target
clean:
	rm -f *.o *.so phylib_wrap.c phylib.py
