#!/bin/bash

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 780690093991.dkr.ecr.us-east-1.amazonaws.com

docker build --platform linux/amd64 -t fenix-amd64 .

docker tag fenix-amd64 780690093991.dkr.ecr.us-east-1.amazonaws.com/fenix:latest

docker push 780690093991.dkr.ecr.us-east-1.amazonaws.com/fenix:latest