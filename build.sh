#!/bin/sh
# Script to manually compile PREDICT
#
cc -g -Wall -fomit-frame-pointer predict.c -lm -lncurses -pthread -o predict
