all: ttf2eot ttf2eotdll

ttf2eot: OpenTypeUtilities.o ttf2eot.o
	g++ -o $@ $^

ttf2eotdll: OpenTypeUtilities.o ttf2eot_dll.o
	g++ -shared -o ttf2eot.dll $^ -Wl,--out-implib,ttf2eot_dll.a

clean:
	rm -f *.o *.core *.obj *.exe core ttf2eot *.dll
