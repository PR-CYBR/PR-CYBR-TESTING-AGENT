#!/bin/bash

# Function to test docker-compose files
test_docker_compose() {
    local dir=$1
    echo "Testing docker-compose in directory: $dir"

    # Navigate to the directory
    cd "$dir" || exit

    # Pull the images
    docker-compose pull

    # Start the containers in detached mode
    docker-compose up -d

    # Check the status of the containers
    if [ $(docker ps -q | wc -l) -gt 0 ]; then
        echo "Containers are running in $dir."
    else
        echo "No containers are running in $dir. Please check the docker-compose file."
        exit 1
    fi

    # Cleanup
    docker-compose down
    cd - || exit
}

# Loop through all directories containing docker-compose.yml
for dir in agents/*/; do
    if [ -f "${dir}docker-compose.yml" ]; then
        test_docker_compose "$dir"
    fi
done