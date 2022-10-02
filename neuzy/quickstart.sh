#!/bin/bash

echo -e "Neuzy - Population-based Neuron Modelling, Copyright (C) 2022  Adrian Röth \nThis program comes with ABSOLUTELY NO WARRANTY.\nThis is free software, and you are welcome to redistribute it under certain conditions.\n"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
NCORE=$(grep -c ^processor /proc/cpuinfo)
echo "Your system supports up to $NCORE CPU cores"
read -p "How many CPU cores do you want to use in parallelization? " cores

if [[ $cores -gt 1 && $cores -le $NCORE ]];
then
    echo "Starting Neuzy with $cores cores."
    mpirun -n $cores python3 $SCRIPT_DIR/paropt/models/run_default.py
elif [[ $cores -eq 1 ]];
then
    echo "Starting Neuzy with $cores core."
    mpirun -n $cores python3 $SCRIPT_DIR/paropt/models/run_default.py
elif [[ $cores -gt $NCORE || $cores -lt 1 ]];
then
    echo "CPU cores are not within the range of the system's available CPU cores."
    echo "Available cores: $NCORE."
    echo "Chosen number of cores: $cores." 
    read -p "Please select a correct number of cores within the range: " cores
    if [[ $cores -gt 1 && $cores -le $NCORE ]];
    then
        echo "Starting Neuzy with $cores cores."
        mpirun -n $cores python3 $SCRIPT_DIR/paropt/models/run_default.py
    elif [[ $cores -eq 1 ]];
    then
        echo "Starting Neuzy with $cores core."
        mpirun -n $cores python3 $SCRIPT_DIR/paropt/models/run_default.py
    elif [[ $cores -gt $NCORE || $cores -lt 1 ]];
    then
        echo "CPU cores are not within the range of the system's available CPU cores."
        echo "Available cores: $NCORE."
        echo "Chosen number of cores: $cores." 
        echo "CPU cores are still not within a valid range. Restart the application and try again."
    fi
fi


