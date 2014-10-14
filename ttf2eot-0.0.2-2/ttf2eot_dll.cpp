/* Trivial utility to create EOT files on Linux */

#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <limits.h>
#include <string.h>

#include <vector>

#ifndef _MSC_VER
# include <stdint.h>
#else
typedef unsigned char uint8_t;
#endif

#if defined(_MSC_VER) || defined(__MINGW32__)
# include <io.h>
# include <fcntl.h> 
# ifndef _O_BINARY
#  define _O_BINARY 0x8000
# endif
# ifndef _O_TEXT
#  define _O_TEXT 0x4000
# endif
#endif

#include "OpenTypeUtilities.h"

#ifndef SIZE_MAX
# define SIZE_MAX UINT_MAX
#endif

using std::vector;

extern "C" { int __declspec(dllexport) __cdecl make_eot(char *infile, char *outfile); }

void cleanup(FILE *input, FILE *output){
    if (input){
        fflush(input);
        fclose(input);
    }
    if (output){
        fflush(output);
        fclose(output);
    }
}

int __declspec(dllexport) __cdecl make_eot(char *infile, char *outfile)
{
    const size_t kFontInitSize = 8192;
    vector<uint8_t> eotHeader(512);
    size_t overlayDst = 0;
    size_t overlaySrc = 0;
    size_t overlayLength = 0;
    size_t fontSize = 0;
    size_t fontOff = 0;
    FILE *input;
    FILE *output;
    unsigned char *fontData;


    if (infile == NULL) {
        return 0;
    } else {
        input = fopen(infile, "rb");
        if (input == NULL) {
            fprintf(stderr, "could not open input file %s, %m\n", infile);
            cleanup(input, output);
            return 1;
        }
    }

    if (outfile == NULL){
        return 0;
    } else {
        output = fopen(outfile, "wb");
        if (output == NULL) {
            fprintf(stderr, "could not open output file %s, %m\n", outfile);
            cleanup(input, output);
            return 1;
        }
    }

    if ((fontData = (unsigned char *) malloc(fontSize = kFontInitSize)) == NULL) {
        fprintf(stderr, "Allocation failure, %m\n");
        cleanup(input, output);
        return 0;
    }

    do {
        size_t ret = fread(fontData + fontOff, 1, fontSize - fontOff, input);
        if (ret && fontSize <= SIZE_MAX / 2) {
            fontOff += ret;
            if ((fontData = (unsigned char *) realloc(fontData, fontSize *= 2)) == NULL) {
                fprintf(stderr, "Allocation failure, %m\n");
                cleanup(input, output);
                return 0;
            }
        } else if (ret) {
            fprintf(stderr, "Too much data, %m\n");
            cleanup(input, output);
            return 0;
        } else {
            fontData = (unsigned char *) realloc(fontData, fontSize = fontOff);
            break;
        }
    } while (true);

    if (getEOTHeader(fontData, fontSize, eotHeader, overlayDst, overlaySrc, overlayLength)) {
        fwrite(&eotHeader[0], eotHeader.size(), 1, output);
        fwrite(fontData, fontSize, 1, output);
        cleanup(input, output);
        return 1;
    } else {
        fprintf(stderr, "unknown error parsing input font, %m\n");
        cleanup(input, output);
        return 0;
    }
}
