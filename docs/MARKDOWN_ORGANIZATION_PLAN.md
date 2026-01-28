# Markdown Files Organization Plan

## Current State

**Root Directory**: 24 markdown files  
**docs/ Folder**: 13 markdown files (already organized)  
**Total**: 37+ markdown files across the project

## Analysis: Should We Consolidate?

### ✅ **YES, but with strategy** - Not everything should move

## Recommended Organization Strategy

### Files to KEEP in Root (Standard Practice)
These are expected in the project root:
- ✅ `README.md` - Main project documentation (standard)
- ✅ `INSTALL.md` - Installation instructions (often in root)
- ✅ `LICENSE` - If you have one (standard)

### Files to MOVE to `docs/` (User Documentation)
These are user-facing guides:
- `CLOUD_DEPLOYMENT_GUIDE.md` → `docs/DEPLOYMENT.md`
- `STREAMLIT_CLOUD_DEPLOYMENT.md` → `docs/STREAMLIT_DEPLOYMENT.md`
- `STREAMLIT_ASYNC_GUIDE.md` → `docs/STREAMLIT_ASYNC_GUIDE.md`
- `UNIFIED_MCP_QUICKSTART.md` → `docs/UNIFIED_MCP_QUICKSTART.md` (or merge with existing)
- `UNIFIED_MCP_MIGRATION.md` → `docs/archive/` (historical)
- `UNIFIED_MCP_SUMMARY.md` → `docs/archive/` (historical)
- `environment_setup.md` → `docs/ENVIRONMENT_SETUP.md`

### Files to MOVE to `docs/status/` (New Folder)
Status and summary files (create new folder):
- `TEST_MIGRATION_COMPLETE.md`
- `TEST_MIGRATION_PLAN.md`
- `LANGFUSE_FIX_SUMMARY.md`
- `LANGFUSE_STREAMLIT_TESTING.md`
- `PRIVACY_INTEGRATION_COMPLETE.md`
- `PACKAGE_CLEANUP_SUMMARY.md`
- `MCP_INTEGRATION_STATUS.md`
- `WEATHER_INTEGRATION_STATUS.md`
- `KNOWLEDGE_SOURCES_UPGRADE.md`
- `DOCUMENTATION_CONSOLIDATION.md`

### Files to MOVE to `docs/archive/` (Historical)
Old or superseded documentation:
- `CLAUDE.md` → `docs/archive/`
- `LANGFUSE_DIAGNOSTICS.md` → `docs/archive/` (if superseded)
- `ASYNC_MCP_IMPLEMENTATION.md` → `docs/archive/`
- `TEST_SESSION_TRACKING.md` → `docs/archive/` (if superseded by tests/README.md)

### Files to MOVE to `docs/guides/` (New Folder)
Technical guides and how-tos:
- `MODEL_CONFIGURATION.md` → `docs/guides/MODEL_CONFIGURATION.md`

## Proposed Structure

```
omd/
├── README.md                    # ✅ Keep in root
├── INSTALL.md                   # ✅ Keep in root
├── docs/
│   ├── INDEX.md                 # Main docs index
│   ├── QUICK_START.md
│   ├── DEVELOPMENT.md
│   ├── INTEGRATION.md
│   ├── OBSERVABILITY.md
│   ├── PRIVACY.md
│   ├── USAGE_EXAMPLES.md
│   ├── DEPLOYMENT.md            # ← Moved from root
│   ├── STREAMLIT_DEPLOYMENT.md  # ← Moved from root
│   ├── STREAMLIT_ASYNC_GUIDE.md # ← Moved from root
│   ├── ENVIRONMENT_SETUP.md     # ← Moved from root
│   ├── guides/                  # ← New folder
│   │   └── MODEL_CONFIGURATION.md
│   ├── status/                  # ← New folder
│   │   ├── TEST_MIGRATION_COMPLETE.md
│   │   ├── TEST_MIGRATION_PLAN.md
│   │   ├── LANGFUSE_FIX_SUMMARY.md
│   │   ├── LANGFUSE_STREAMLIT_TESTING.md
│   │   ├── PRIVACY_INTEGRATION_COMPLETE.md
│   │   ├── PACKAGE_CLEANUP_SUMMARY.md
│   │   ├── MCP_INTEGRATION_STATUS.md
│   │   ├── WEATHER_INTEGRATION_STATUS.md
│   │   ├── KNOWLEDGE_SOURCES_UPGRADE.md
│   │   └── DOCUMENTATION_CONSOLIDATION.md
│   └── archive/               # ← Existing folder
│       ├── CLAUDE.md
│       ├── ASYNC_MCP_IMPLEMENTATION.md
│       ├── UNIFIED_MCP_MIGRATION.md
│       ├── UNIFIED_MCP_SUMMARY.md
│       └── ... (existing archive files)
```

## Benefits

✅ **Cleaner root** - Only essential files visible  
✅ **Better organization** - Related docs grouped together  
✅ **Easier navigation** - Clear structure for finding docs  
✅ **Maintainability** - Status files separate from guides  
✅ **Professional** - Follows standard project structure  

## Considerations

⚠️ **README.md must stay** - Standard practice, GitHub displays it  
⚠️ **Update links** - Any internal markdown links will need updating  
⚠️ **Update docs/INDEX.md** - Add references to moved files  
⚠️ **CI/CD references** - Check if any scripts reference these files  

## Migration Steps

1. Create new folders: `docs/status/` and `docs/guides/`
2. Move files according to categorization above
3. Update `docs/INDEX.md` with new structure
4. Search for internal links and update them
5. Update any CI/CD or scripts that reference these files
6. Test that all documentation is still accessible

## Alternative: Minimal Approach

If you prefer less reorganization:

**Keep in root:**
- README.md
- INSTALL.md

**Move everything else to `docs/`:**
- All other .md files → `docs/`

This is simpler but less organized.

---

**Recommendation**: Use the structured approach above for better long-term maintainability.

