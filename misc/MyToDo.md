### ⚠️ Brand-CLI Architectural Risks & Considerations

* **Context Ambiguity (Section 3):** * *Risk:* Full-archive crawls on context-less commands (e.g., `Audit E001`) may lead to performance lag or "False Positive" collisions across different IPs.
    * *Mitigation:* Implement a "Did you mean?" fuzzy search or a LRU (Least Recently Used) cache for the `.brand_context`.

* **Atomic Migration Failures (Section 5):**
    * *Risk:* Interruptions during "Inbox to Bundle" auto-migration could result in "Partial Bundles" (e.g., folder created, but files not moved), causing downstream AI analysis to fail or hallucinate.
    * *Mitigation:* Use transactional file operations or a "Verification Check" before triggering the Audit workflow.

* **Terminology Mapping Overhead (Section 4):**
    * *Risk:* The "Mental Translation Layer" between generic MAM code terms (`arc`) and brand-specific CLI output (`Biome`) increases debugging complexity and potential mapping nulls in prompt injection.
    * *Mitigation:* Centralize a `TermMapper` utility to ensure strict validation between `brand_config.json` and AI prompt variables.

---

### 🎯 Project Goal
Implement a polymorphic "Fragment" engine for Brand-CLI to handle text assembly for both AI Prompts (prefixes/system instructions) and Final Output (suffixes/boilerplate).

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