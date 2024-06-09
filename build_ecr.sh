#!/bin/bash

REPO=780690093991.dkr.ecr.us-east-1.amazonaws.com

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $REPO

docker build --platform linux/amd64 -t fenix-amd64 .

docker tag fenix-amd64 $REPO/fenix:latest

docker push $REPO/fenix:latest