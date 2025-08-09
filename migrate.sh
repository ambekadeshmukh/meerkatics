#!/bin/bash
# Meerkatics Migration Script
# This script migrates enhanced components from sentinelops/ to main meerkatics/ structure

set -e  # Exit on any error

echo "🚀 Starting Meerkatics Migration..."
echo "Moving enhanced components from sentinelops/ to main meerkatics/ structure"

# Create backup first
echo "📦 Creating backup..."
cp -r meerkatics meerkatics_backup_$(date +%Y%m%d_%H%M%S)

# Navigate to project root
cd meerkatics

echo "🔄 Phase 1: Migrating Backend Components..."

# 1. Migrate Stream Processor
echo "  → Migrating Stream Processor..."
if [ -d "sentinelops/backend/stream-processor" ]; then
    # Create target directory if it doesn't exist
    mkdir -p backend/stream-processor
    
    # Copy enhanced stream processor files
    cp -r sentinelops/backend/stream-processor/* backend/stream-processor/
    
    # Ensure processors directory exists
    mkdir -p backend/stream-processor/processors
    
    echo "    ✅ Stream processor migrated"
else
    echo "    ⚠️  sentinelops/backend/stream-processor not found"
fi

# 2. Migrate API Server  
echo "  → Migrating API Server..."
if [ -d "sentinelops/backend/api-server" ]; then
    # Create target directory if it doesn't exist
    mkdir -p backend/api-server
    
    # Copy enhanced API server files
    cp -r sentinelops/backend/api-server/* backend/api-server/
    
    echo "    ✅ API server migrated"
else
    echo "    ⚠️  sentinelops/backend/api-server not found"
fi

# 3. Migrate Database Components
echo "  → Migrating Database Components..."
if [ -d "sentinelops/backend/database" ]; then
    mkdir -p backend/database
    cp -r sentinelops/backend/database/* backend/database/
    echo "    ✅ Database components migrated"
fi

echo "🎨 Phase 2: Migrating Frontend Components..."

# 4. Migrate Enhanced Frontend
echo "  → Migrating Frontend Components..."
if [ -d "sentinelops/frontend" ]; then
    # Create target directories
    mkdir -p frontend/src/components
    mkdir -p frontend/src/services
    mkdir -p frontend/src/utils
    mkdir -p frontend/public
    
    # Copy enhanced components (merge with existing)
    if [ -d "sentinelops/frontend/src/components" ]; then
        cp -r sentinelops/frontend/src/components/* frontend/src/components/
    fi
    
    # Copy services
    if [ -d "sentinelops/frontend/src/services" ]; then
        cp -r sentinelops/frontend/src/services/* frontend/src/services/
    fi
    
    # Copy utils
    if [ -d "sentinelops/frontend/src/utils" ]; then
        cp -r sentinelops/frontend/src/utils/* frontend/src/utils/
    fi
    
    # Copy package.json if it has additional dependencies
    if [ -f "sentinelops/frontend/package.json" ]; then
        echo "    📋 Note: Review sentinelops/frontend/package.json for additional dependencies"
        cp sentinelops/frontend/package.json frontend/package_sentinelops.json
    fi
    
    echo "    ✅ Frontend components migrated"
else
    echo "    ⚠️  sentinelops/frontend not found"
fi

echo "🧪 Phase 3: Migrating Tests..."

# 5. Migrate Tests
echo "  → Migrating Test Files..."
if [ -d "sentinelops/tests" ]; then
    mkdir -p tests
    cp -r sentinelops/tests/* tests/
    echo "    ✅ Tests migrated"
fi

echo "📚 Phase 4: Migrating Documentation..."

# 6. Migrate Documentation
echo "  → Migrating Documentation..."
if [ -d "sentinelops/docs" ]; then
    # Merge docs (don't overwrite existing)
    for file in sentinelops/docs/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            if [ ! -f "docs/$filename" ]; then
                cp "$file" "docs/$filename"
                echo "    📄 Copied $filename"
            else
                cp "$file" "docs/sentinelops_$filename"
                echo "    📄 Copied $filename as sentinelops_$filename (conflict resolved)"
            fi
        fi
    done
    echo "    ✅ Documentation merged"
fi

echo "⚙️  Phase 5: Migrating Configuration..."

# 7. Migrate Infrastructure and Scripts
echo "  → Migrating Infrastructure..."
if [ -d "sentinelops/infrastructure" ]; then
    mkdir -p infrastructure
    
    # Merge infrastructure files
    for item in sentinelops/infrastructure/*; do
        if [ -d "$item" ]; then
            dirname=$(basename "$item")
            mkdir -p "infrastructure/$dirname"
            cp -r "$item"/* "infrastructure/$dirname/"
        elif [ -f "$item" ]; then
            filename=$(basename "$item")
            if [ ! -f "infrastructure/$filename" ]; then
                cp "$item" "infrastructure/$filename"
            else
                cp "$item" "infrastructure/sentinelops_$filename"
                echo "    ⚙️  Copied $filename as sentinelops_$filename (conflict resolved)"
            fi
        fi
    done
    echo "    ✅ Infrastructure migrated"
fi

# 8. Migrate Scripts
echo "  → Migrating Scripts..."
if [ -d "sentinelops/scripts" ]; then
    mkdir -p scripts
    cp -r sentinelops/scripts/* scripts/
    echo "    ✅ Scripts migrated"
fi

echo "🔧 Phase 6: Updating Import Paths..."

# 9. Fix Import Paths in Stream Processor
echo "  → Fixing stream processor imports..."
if [ -d "backend/stream-processor" ]; then
    # Update Python imports
    find backend/stream-processor -name "*.py" -type f -exec sed -i.bak \
        -e 's/from processors\./from .processors./g' \
        -e 's/from services\./from ..services./g' \
        -e 's/from models\./from ..models./g' \
        {} \;
    
    # Remove backup files
    find backend/stream-processor -name "*.bak" -delete
    echo "    ✅ Stream processor imports updated"
fi

# 10. Fix Import Paths in API Server
echo "  → Fixing API server imports..."
if [ -d "backend/api-server" ]; then
    # Update Python imports
    find backend/api-server -name "*.py" -type f -exec sed -i.bak \
        -e 's/from \.\.services/from ..services/g' \
        -e 's/from \.\.models/from ..models/g' \
        -e 's/from \.\.middleware/from ..middleware/g' \
        -e 's/from routers\./from .routers./g' \
        {} \;
    
    # Remove backup files
    find backend/api-server -name "*.bak" -delete
    echo "    ✅ API server imports updated"
fi

# 11. Update Frontend API Endpoints
echo "  → Updating frontend API configurations..."
if [ -f "frontend/src/services/api.js" ]; then
    # Update API base URL if needed
    sed -i.bak 's/sentinelops/meerkatics/g' frontend/src/services/api.js
    rm -f frontend/src/services/api.js.bak
fi

echo "📋 Phase 7: Merging Configuration Files..."

# 12. Merge Docker Compose Files
echo "  → Merging Docker Compose configurations..."
if [ -f "sentinelops/docker-compose.yml" ]; then
    if [ -f "infrastructure/docker-compose.yml" ]; then
        # Create merged version
        echo "# Merged Docker Compose - Review and edit as needed" > infrastructure/docker-compose-merged.yml
        echo "# Original from infrastructure/" >> infrastructure/docker-compose-merged.yml
        cat infrastructure/docker-compose.yml >> infrastructure/docker-compose-merged.yml
        echo "" >> infrastructure/docker-compose-merged.yml
        echo "# Enhanced from sentinelops/" >> infrastructure/docker-compose-merged.yml
        cat sentinelops/docker-compose.yml >> infrastructure/docker-compose-merged.yml
        echo "    📄 Created docker-compose-merged.yml for review"
    else
        cp sentinelops/docker-compose.yml infrastructure/docker-compose.yml
        echo "    📄 Copied docker-compose.yml"
    fi
fi

# 13. Merge Environment Files
echo "  → Merging environment configurations..."
if [ -f "sentinelops/.env.example" ]; then
    if [ -f "infrastructure/.env.example" ]; then
        # Append additional env vars
        echo "" >> infrastructure/.env.example
        echo "# Additional variables from sentinelops" >> infrastructure/.env.example
        cat sentinelops/.env.example >> infrastructure/.env.example
        echo "    📄 Merged .env.example"
    else
        cp sentinelops/.env.example infrastructure/.env.example
        echo "    📄 Copied .env.example"
    fi
fi

echo "🧹 Phase 8: Cleanup and Verification..."

# 14. Create migration summary
echo "  → Creating migration summary..."
cat > MIGRATION_SUMMARY.md << EOF
# Meerkatics Migration Summary

Migration completed on: $(date)

## Files Migrated:

### Backend:
- Stream Processor: sentinelops/backend/stream-processor/ → backend/stream-processor/
- API Server: sentinelops/backend/api-server/ → backend/api-server/
- Database: sentinelops/backend/database/ → backend/database/

### Frontend:
- Components: sentinelops/frontend/src/components/ → frontend/src/components/
- Services: sentinelops/frontend/src/services/ → frontend/src/services/
- Utils: sentinelops/frontend/src/utils/ → frontend/src/utils/

### Infrastructure:
- Scripts: sentinelops/scripts/ → scripts/
- Infrastructure: sentinelops/infrastructure/ → infrastructure/
- Tests: sentinelops/tests/ → tests/
- Docs: sentinelops/docs/ → docs/ (merged)

## Next Steps:

1. Review merged configuration files:
   - infrastructure/docker-compose-merged.yml
   - infrastructure/.env.example

2. Test the integration:
   \`\`\`bash
   cd infrastructure
   docker-compose -f docker-compose-merged.yml up --build
   \`\`\`

3. Update any remaining import paths if needed

4. Remove the sentinelops/ folder after verification:
   \`\`\`bash
   rm -rf sentinelops/
   \`\`\`

## Backup:
Original meerkatics folder backed up as: meerkatics_backup_*

EOF

echo "✅ Migration Complete!"
echo ""
echo "📋 Summary:"
echo "  • Backend components migrated and imports updated"
echo "  • Frontend components merged"
echo "  • Configuration files merged" 
echo "  • Tests and documentation migrated"
echo "  • Import paths automatically updated"
echo ""
echo "📖 Next Steps:"
echo "  1. Review MIGRATION_SUMMARY.md"
echo "  2. Check infrastructure/docker-compose-merged.yml"
echo "  3. Test the integration:"
echo "     cd infrastructure && docker-compose up --build"
echo "  4. Remove sentinelops/ folder after verification"
echo ""
echo "🎉 Your Meerkatics platform is now ready with all enhanced components!"
