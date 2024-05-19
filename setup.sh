#!/bin/bash

docker build -t plush .
docker run -ti plush:latest nix-shell -p python311 python311Packages.ply llvm gcc
