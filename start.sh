#!/bin/bash

ncore=$(grep -c ^processor /proc/cpuinfo)
echo "Your system supports up to $ncore CPU cores"
read -p "How many CPU cores do you want to use in parallelization? " cores

if [[ $cores -gt 1 && $cores -le $ncore ]];
then
    echo "Starting Neuzy with $cores cores."
    mpirun -n $cores python3 ./paropt/models/run_mpi.py
elif [[ $cores -eq 1 ]];
then
    echo "Starting Neuzy with $cores core."
    mpirun -n $cores python3 ./paropt/models/run_mpi.py
elif [[ $cores -gt $ncore || $cores -lt 1 ]];
then
    echo "CPU cores are not within the range of the system's available CPU cores."
    echo "Available cores: $ncore."
    echo "Chosen number of cores: $cores." 
    read -p "Please select a correct number of cores within the range: " cores
    if [[ $cores -gt 1 && $cores -le $ncore ]];
    then
        echo "Starting Neuzy with $cores cores."
        mpirun -n $cores python3 ./paropt/models/run_mpi.py
    elif [[ $cores -eq 1 ]];
    then
        echo "Starting Neuzy with $cores core."
        mpirun -n $cores python3 ./paropt/models/run_mpi.py
    elif [[ $cores -gt $ncore || $cores -lt 1 ]];
    then
        echo "CPU cores are not within the range of the system's available CPU cores."
        echo "Available cores: $ncore."
        echo "Chosen number of cores: $cores." 
        echo "CPU cores are still not within a valid range. Restart the application and try again."
    fi
fi


