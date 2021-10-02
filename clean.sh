#!/bin/bash
#recursively goes through all directories and removes all *.stl and *.scad files
find . -name "*.stl" -delete
find . -name "*.scad" -delete