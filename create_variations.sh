#!/bin/bash
#Bash script to create variations for the given languages using the generate_variations_with_itn.py script

LANGUAGES=(
  "Assamese" "Bengali" "Bodo" "Dogri" "Gujarati" "Hindi" "Kannada" "Kashmiri" "Konkani"
  "Maithili" "Malayalam" "Manipuri" "Marathi" "Nepali" "Odia"
  "Punjabi" "Sanskrit" "Santali" "Sindhi" "Tamil" "Telugu" "Urdu"
)

BASE_INPUT_DIR="/path/to/input_files"
BASE_OUTPUT_DIR="/path/to/output_files"
LOG_DIR="./logs"

TEMPERATURE=0.1
MAX_WORKERS=6 #adjust this based on the number of CPUs available
BATCH_SIZE=100 #adjust this based on the memory available
BATCH_RETRY=2 #adjust this based on the number of retries needed

mkdir -p "$BASE_OUTPUT_DIR" "$LOG_DIR"

for LANGUAGE in "${LANGUAGES[@]}"; do
    LOWER_LANGUAGE=$(echo "$LANGUAGE" | tr '[:upper:]' '[:lower:]')

    INPUT_FILE="${BASE_INPUT_DIR}/${LOWER_LANGUAGE}.jsonl"
    OUTPUT_FILE="${BASE_OUTPUT_DIR}/${LOWER_LANGUAGE}_variations.jsonl"
    LOG_FILE="${LOG_DIR}/${LOWER_LANGUAGE}.log"

    echo "Processing $LANGUAGE..."

    python3 generate_variations_with_itn.py \
        "$INPUT_FILE" \
        "$OUTPUT_FILE" \
        "$LANGUAGE" \
        --max_workers "$MAX_WORKERS" \
        --batch_size "$BATCH_SIZE" \
        --batch_retry "$BATCH_RETRY" \
        --temperature "$TEMPERATURE" \
        > "$LOG_FILE" 2>&1

    echo "Finished $LANGUAGE → $OUTPUT_FILE"
done