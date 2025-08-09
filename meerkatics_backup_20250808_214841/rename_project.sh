#!/bin/bash

# Rename Project Script - Meerkatics to Meerkatics
# This script performs a comprehensive rename of the project by searching and replacing
# all instances of "meerkatics", "Meerkatics", "MEERKATICS" with "meerkatics", "Meerkatics", "MEERKATICS"

set -e  # Exit on any error

echo "Starting project-wide rename from Meerkatics to Meerkatics"

# Define the project directory
PROJECT_DIR="$(pwd)"

# Color for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Working in directory: ${PROJECT_DIR}${NC}"

# Confirm with user
read -p "This will replace all instances of 'meerkatics' with 'meerkatics' in all files. Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 0
fi

# Function to replace text in files with various case forms
replace_in_files() {
    local old_text=$1
    local new_text=$2
    local old_upper=$(echo $old_text | tr '[:lower:]' '[:upper:]')
    local new_upper=$(echo $new_text | tr '[:lower:]' '[:upper:]')
    local old_title=$(echo $old_text | sed 's/\<./\u&/g')
    local new_title=$(echo $new_text | sed 's/\<./\u&/g')
    local old_camel=$(echo $old_text | sed -r 's/(^|_)([a-z])/\U\2/g')
    local new_camel=$(echo $new_text | sed -r 's/(^|_)([a-z])/\U\2/g')
    
    echo -e "${YELLOW}Searching for files containing '$old_text', '$old_upper', '$old_title', or '$old_camel'...${NC}"
    
    # Find files containing the text (excluding .git directory and binary files)
    FILES=$(grep -l -r -i "$old_text" --include="*.*" --exclude-dir=".git" --exclude="*.pyc" --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.pdf" "$PROJECT_DIR" 2>/dev/null || echo "")
    
    if [ -z "$FILES" ]; then
        echo "No files found containing $old_text"
    else
        echo -e "${GREEN}Found $(echo "$FILES" | wc -l | tr -d ' ') files containing the pattern.${NC}"
        
        for file in $FILES; do
            if [ -f "$file" ]; then
                echo "Processing file: $file"
                
                # Check if file is binary
                if [[ "$(file -b --mime "$file" | grep -c 'binary')" -gt 0 ]]; then
                    echo -e "${YELLOW}Skipping binary file: $file${NC}"
                    continue
                fi
                
                # Make replacements for different case forms
                sed -i '' "s/$old_text/$new_text/g" "$file"
                sed -i '' "s/$old_upper/$new_upper/g" "$file"
                sed -i '' "s/$old_title/$new_title/g" "$file"
                sed -i '' "s/$old_camel/$new_camel/g" "$file"
                
                # Handle specific mixed case forms that may appear in code
                # Meerkatics
                sed -i '' "s/Meerkatics/Meerkatics/g" "$file"
                # meerkaticsOps (camelCase)
                sed -i '' "s/meerkaticsOps/meerkaticsOps/g" "$file"
            fi
        done
    fi
}

# Function to rename files and directories
rename_files_and_dirs() {
    local old_text=$1
    local new_text=$2
    
    echo -e "${YELLOW}Searching for files and directories with names containing '$old_text'...${NC}"
    
    # Find files/directories with names containing the text
    FILES_DIRS=$(find "$PROJECT_DIR" -name "*$old_text*" -not -path "*/\.*" | sort -r)
    
    if [ -z "$FILES_DIRS" ]; then
        echo "No files or directories found with names containing $old_text"
    else
        echo -e "${GREEN}Found $(echo "$FILES_DIRS" | wc -l | tr -d ' ') files/directories with matching names.${NC}"
        
        for item in $FILES_DIRS; do
            if [ -e "$item" ]; then
                new_name=$(echo "$item" | sed "s/$old_text/$new_text/g")
                if [ "$item" != "$new_name" ]; then
                    echo "Renaming: $item -> $new_name"
                    # Create directory if needed
                    mkdir -p "$(dirname "$new_name")"
                    mv "$item" "$new_name"
                fi
            fi
        done
    fi
}

# Execute replacements
echo -e "${GREEN}Step 1: Replacing text in file contents...${NC}"
replace_in_files "meerkatics" "meerkatics"

echo -e "${GREEN}Step 2: Renaming files and directories...${NC}"
rename_files_and_dirs "meerkatics" "meerkatics"

echo -e "${GREEN}Step 3: Checking for remaining references...${NC}"
REMAINING=$(grep -r -i "meerkatics\|Meerkatics" --include="*.*" --exclude-dir=".git" --exclude="*.pyc" --exclude="*.png" --exclude="*.jpg" --exclude="*.jpeg" --exclude="*.gif" --exclude="*.pdf" "$PROJECT_DIR" 2>/dev/null || echo "")

if [ -n "$REMAINING" ]; then
    echo -e "${YELLOW}There may still be some references to check manually:${NC}"
    echo "$REMAINING" | head -n 10
    if [ $(echo "$REMAINING" | wc -l) -gt 10 ]; then
        echo -e "${YELLOW}... and $(expr $(echo "$REMAINING" | wc -l) - 10) more matches.${NC}"
    fi
else
    echo -e "${GREEN}No remaining references found.${NC}"
fi

echo -e "${GREEN}=============================================================${NC}"
echo -e "${GREEN}Project rename from Meerkatics to Meerkatics completed!${NC}"
echo -e "${GREEN}=============================================================${NC}"
echo -e "Please check your project to ensure all references are updated correctly."
echo -e "You may need to manually update some complex references or special cases."
echo -e "Don't forget to update any external references like CI/CD configurations."
