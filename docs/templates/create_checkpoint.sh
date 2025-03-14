#!/bin/bash
# Checkpoint Creation Script
# Automatically creates a checkpoint file when state vectors are updated

# Check if required parameters are provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 <component_id> <step_id>"
  exit 1
fi

COMPONENT_ID=$1
STEP_ID=$2
TIMESTAMP=$(date +"%Y-%m-%d-%H-%M")
CHECKPOINT_ID="CHECKPOINT_P${COMPONENT_ID}_${STEP_ID}"
CHECKPOINT_FILE="docs/checkpoints/${CHECKPOINT_ID}.json"
TEMPLATE_FILE="docs/templates/checkpoint_template.json"

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "Error: Template file $TEMPLATE_FILE not found"
  exit 1
fi

# Create checkpoint directory if it doesn't exist
mkdir -p docs/checkpoints

echo "Creating checkpoint file: $CHECKPOINT_FILE"

# Extract current state from META_STATE.md - simplified approach
STATE_VECTOR=$(sed -n '/Project State Vector/,/```/p' docs/META_STATE.md | sed -n '/```json/,/```/p' | grep -v '```')
IMPLEMENTATION_STATE=$(sed -n '/implementation_state/,/}/p' docs/META_STATE.md)
VERIFICATION_STATUS=$(sed -n '/Verification Status/,/```/p' docs/META_STATE.md | sed -n '/```json/,/```/p' | grep -v '```')

# Generate a checksum (simplified version)
CHECKSUM=$(echo "$STATE_VECTOR$IMPLEMENTATION_STATE$VERIFICATION_STATUS$TIMESTAMP" | sha256sum | cut -d' ' -f1)

# Create checkpoint file
cp "$TEMPLATE_FILE" "$CHECKPOINT_FILE"

# Replace placeholders
sed -i "s|CHECKPOINT_{COMPONENT_ID}_{STEP_ID}|$CHECKPOINT_ID|g" "$CHECKPOINT_FILE"
sed -i "s|{TIMESTAMP}|$TIMESTAMP|g" "$CHECKPOINT_FILE"
sed -i "s|{CHECKSUM}|$CHECKSUM|g" "$CHECKPOINT_FILE"

# TODO: Replace other placeholders based on extracted state

echo "Checkpoint created successfully: $CHECKPOINT_FILE"
echo "Don't forget to update the clock_synchronization section in META_STATE.md"

# Update META_STATE.md clock_synchronization
sed -i "/clock_synchronization/,/}/s|\"participants\".*|\"participants\": [\"STATUS.md\", \"META_STATE.md\", \"checkpoints/$CHECKPOINT_ID.json\"],|" docs/META_STATE.md
sed -i "/clock_synchronization/,/}/s|\"last_sync\".*|\"last_sync\": \"$TIMESTAMP\",|" docs/META_STATE.md

echo "META_STATE.md updated with new checkpoint reference"

# Update Checkpoint History in META_STATE.md
CURRENT_DATE=$(date +"%Y-%m-%d")
COMPONENT_NAME=$(sed -n '/Session Continuation/,/Required Test/p' docs/META_STATE.md | grep "Component:" | head -1 | cut -d ':' -f 2 | sed 's/^ *//')
STATUS=$(sed -n '/Session Continuation/,/Required Test/p' docs/META_STATE.md | grep "State:" | head -1 | cut -d ':' -f 2 | sed 's/^ *//')

# Create new entry for Checkpoint History table
NEW_ENTRY="| $CURRENT_DATE | $CHECKPOINT_ID | ${COMPONENT_ID} | $COMPONENT_NAME | $STATUS |"

# Add entry to Checkpoint History table
sed -i "/^| Timestamp | Checkpoint ID | Phase | Component | Status |$/a $NEW_ENTRY" docs/META_STATE.md

echo "Checkpoint History updated in META_STATE.md"

# Update Recovery Data in META_STATE.md
sed -i "s|last known stable state was at.*|last known stable state was at $CHECKPOINT_ID ($CURRENT_DATE).|" docs/META_STATE.md
sed -i "s|Recovery instructions are stored in docs/checkpoints/.*|Recovery instructions are stored in docs/checkpoints/$CHECKPOINT_ID.json |" docs/META_STATE.md

echo "Recovery Data updated in META_STATE.md"

# Generate a new verification checksum
VERIFICATION_CHECKSUM="VERIFICATION_CHECKPOINT_$(date +"%Y%m%d_%H")"
SESSION_ID=$(grep "session_id" docs/META_STATE.md | head -1 | cut -d '"' -f 4)
COMPONENTS=$(grep "current_component" docs/META_STATE.md | head -1 | cut -d '"' -f 4)
STATE=$(echo "$STATUS" | tr ' ' '_')
VECTOR_CLOCK=$(grep "vector_clock" docs/META_STATE.md | head -1 | sed 's/.*{/\{/' | sed 's/}.*/\}/')

# Update verification checksum section
sed -i '/^VERIFICATION_CHECKPOINT/s/.*/'"$VERIFICATION_CHECKSUM"'/' docs/META_STATE.md
sed -i '/^Session:/s/.*/Session: '"$SESSION_ID"'/' docs/META_STATE.md
sed -i '/^Components:/s/.*/Components: '"$COMPONENTS"'/' docs/META_STATE.md
sed -i '/^State:/s/.*/State: '"$STATE"'/' docs/META_STATE.md
sed -i '/^Vector Clock:/s/.*/Vector Clock: '"$VECTOR_CLOCK"'/' docs/META_STATE.md
sed -i '/^SHA256:/s/.*/SHA256: '"$CHECKSUM"'/' docs/META_STATE.md

echo "Verification Checksum updated in META_STATE.md"
echo "Checkpoint creation complete!" 