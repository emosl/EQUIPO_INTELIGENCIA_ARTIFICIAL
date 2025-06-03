#!/bin/bash

# Source and destination directories (edit these paths)
SOURCE_DIR="/mnt/c/Users/Pboli/Escritorio/github/EQUIPO_INTELIGENCIA_ARTIFICIAL/Results"
for DIR in "$SOURCE_DIR"/PROCESSED_KALMAN_*; do
    if [[ -d "$DIR" ]]; then
        echo "Processing folder: $DIR"

        # Loop through s1 to s20
        for i in {10..20}; do
            # Construct subfolder destination path
            DEST_DIR="$DIR/S$i"

            # Move all matching files
            for file in "$DIR"/S${i}*.csv; do
                [[ -e "$file" ]] || continue  # Skip if no match
                mv "$file" "$DEST_DIR/"
            done
        done
    fi
done