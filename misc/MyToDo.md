# TODO List
 ## convert draft to use the Random Fragment
 ## Add ability to view the current context
 ## Add ability to list available context settings (read the directory structure)
 ## Modify Help to use defined terms for IP, Series, Season, Episode
 ## Modify AI class to use user defined API key env variable
 ## Review README.md, ARCHITECTURE.md, ./docs/brand_cli.md




### 🎯 Project Goal
Implement a polymorphic "Fragment" engine for Brand-CLI to handle text assembly for both AI Prompts (prefixes/system instructions) and Final Output (suffixes/boilerplate).



# Brand-CLI: Transcript Refactor Roadmap

## Phase 1: The Transcript Foundation
* Create `src/brand_cli/transcript.py`.
* Move transcript-specific logic from `file_manager.py` to the new `Transcript` class:
    * `load_transcript_asset` (Loading/Cleaning)
    * `_has_no_audio_transcript` (Validation)
    * `get_video_duration` & `get_last_timestamp` (Metadata Extraction)
* Implement `ensure_uploaded(model)` method in `Transcript` for Just-In-Time (JIT) 
  uploads to the Gemini File API.

## Phase 1.5: Data Bridge
* Update `SessionData` dataclass in `file_manager.py` to replace the `transcript` string 
  and `path` string with a single `transcript_obj: Transcript` field.

## Phase 2: Injection & Logic Flow
* Modify `AuditWorkflow` to initialize the `Transcript` object once.
* Implement cleanup logic (using a `try/finally` block or a Context Manager) 
  to ensure `model.delete_file()` is called only after all sub-workflows 
  (Feedback, Gold) are finished.

## Phase 3: Global Integration
* Update all workflows (`Feedback`, `Gold`, `Describe`, `Draft`) to source 
  data/IDs from `session.transcript_obj` instead of raw strings.
* Update `Brand.py` and `prepare_session_assets` to initialize the `Transcript` 
  object during the initial session setup.

## Phase 4: Optimization (Back Burner)
* Research long-term persistent File IDs and custom TTL logic in `.brand_context`.




### 🏛️ Architectural Decisions
1. **Hierarchy-First Resolution:** Files are resolved via a "bottom-up" search: 
   Episode -> Season -> Series -> IP -> Global.
   
2. **Class Hierarchy (The Fragment Strategy):**
   - **StaticFragment:** One-to-one file content retrieval.
   - **RandomFragment:** Multi-section files; returns one random block (delimiter-based).
   - **FlaggedFragment:** Key-value retrieval within a single file using `[TAGS]`.
   - **CompositeFragment:** The "Chainer." Holds a list of other fragments to build complex strings (Recursive/Composite Pattern).

3. **Workflow Integration:**
   - Fragments are "Dumb" (they don't know about the AI).
   - The Workflow class is the "Orchestrator" that bundles these fragments.
   - Fail-forward logic: Missing files append an error string rather than crashing the CLI.

4. **Philosophy:**
   - Agnostic & Decoupled: The engine doesn't care if the content is Valheim or Tech Tutorials.
   - Zero Fatigue: Automatic path resolution based on `.brand_context`.

### Implementation Notes

## Recursion Safety
- Implement max recursion depth (10 levels) for CompositeFragment
- Add cycle detection in fragment references

## Performance Optimizations
- Add LRU cache for resolved fragment paths
- Implement bulk fragment pre-loading for workflows

## Error Handling Standardization
- Use format: "[FRAGMENT_ERROR] {fragment_type}@{path}: {reason}"
- Document all error cases in FragmentError.md

## Flagged Fragment Tags
- Standardize tag format: "[TAG:NAME]"
- Add reserved tags list (TBD)

## Metadata Headers
- Implement YAML front matter for:
  - Fragment version
  - Last modified
  - Author
  - Dependencies


  ### ⚠️ Brand-CLI Architectural Risks & Considerations

* **Context Ambiguity (Section 3):** * *Risk:* Full-archive crawls on context-less commands (e.g., `Audit E001`) may lead to performance lag or "False Positive" collisions across different IPs.
    * *Mitigation:* Implement a "Did you mean?" fuzzy search or a LRU (Least Recently Used) cache for the `.brand_context`.

* **Atomic Migration Failures (Section 5):**
    * *Risk:* Interruptions during "Inbox to Bundle" auto-migration could result in "Partial Bundles" (e.g., folder created, but files not moved), causing downstream AI analysis to fail or hallucinate.
    * *Mitigation:* Use transactional file operations or a "Verification Check" before triggering the Audit workflow.

* **Terminology Mapping Overhead (Section 4):**
    * *Risk:* The "Mental Translation Layer" between generic MAM code terms (`arc`) and brand-specific CLI output (`Biome`) increases debugging complexity and potential mapping nulls in prompt injection.
    * *Mitigation:* Centralize a `TermMapper` utility to ensure strict validation between `brand_config.json` and AI prompt variables.
