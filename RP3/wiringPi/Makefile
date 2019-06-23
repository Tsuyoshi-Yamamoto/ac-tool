.SUFFIX: .cpp .o
TARGET = wpitest
CC = g++
CFLAGS = -std=c++0x -O2

OBJS = wpitest.o

SOURCES = wpitest.cpp
HEADERS = wpitest.h

$(TARGET): $(OBJS)
	$(CC) -o $(TARGET) -lwiringPi $^

.cpp.o:
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f $(OBJS)

