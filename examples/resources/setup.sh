#!/bin/bash

drasi init --local --version latest

kubectl apply -f ./postgres-db.yml
kubectl wait --for=condition=Ready service/postgres

drasi apply -f ./postgres-source.yml
drasi wait source hello-world -t 120

drasi apply -f ./queries.yml

