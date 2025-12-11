#!/bin/bash

echo "✅ TALENTSHIRE INTEGRATION VERIFICATION"
echo ""

# Check infrastructure files
echo "📦 Infrastructure Files:"
test -f docker-compose.yml && echo "  ✅ docker-compose.yml" || echo "  ❌ docker-compose.yml"
test -f Dockerfile.backend && echo "  ✅ Dockerfile.backend" || echo "  ❌ Dockerfile.backend"
test -f frontend/Dockerfile && echo "  ✅ frontend/Dockerfile" || echo "  ❌ frontend/Dockerfile"
test -f deploy.sh && echo "  ✅ deploy.sh" || echo "  ❌ deploy.sh"

echo ""
echo "🎬 Demo Files:"
test -f demo.py && echo "  ✅ demo.py" || echo "  ❌ demo.py"
test -f DEMO_GUIDE.md && echo "  ✅ DEMO_GUIDE.md" || echo "  ❌ DEMO_GUIDE.md"
test -f QUICK_START.md && echo "  ✅ QUICK_START.md" || echo "  ❌ QUICK_START.md"

echo ""
echo "🔧 Backend Model Files:"
test -f shared/models.py && echo "  ✅ shared/models.py" || echo "  ❌ shared/models.py"
test -f shared/database_models.py && echo "  ✅ shared/database_models.py" || echo "  ❌ shared/database_models.py"
test -f shared/model_converters.py && echo "  ✅ shared/model_converters.py" || echo "  ❌ shared/model_converters.py"
test -f shared/schema.sql && echo "  ✅ shared/schema.sql" || echo "  ❌ shared/schema.sql"

echo ""
echo "🎨 Frontend Files:"
test -f frontend/src/types/api.ts && echo "  ✅ frontend/src/types/api.ts" || echo "  ❌ frontend/src/types/api.ts"
test -f frontend/src/services/api.ts && echo "  ✅ frontend/src/services/api.ts" || echo "  ❌ frontend/src/services/api.ts"

echo ""
echo "📚 Documentation:"
test -f START_HERE.md && echo "  ✅ START_HERE.md" || echo "  ❌ START_HERE.md"
test -f DELIVERY_SUMMARY.md && echo "  ✅ DELIVERY_SUMMARY.md" || echo "  ❌ DELIVERY_SUMMARY.md"
test -f COMPLETE_PLATFORM_INTEGRATION.md && echo "  ✅ COMPLETE_PLATFORM_INTEGRATION.md" || echo "  ❌ COMPLETE_PLATFORM_INTEGRATION.md"

echo ""
echo "🚀 Ready to deploy with: ./deploy.sh --demo"
