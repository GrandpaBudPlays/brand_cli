### **Part 1: The Prioritized Task Dashboard**

| Priority | Task Label | Status | Brief Description |
| :--- | :--- | :--- | :--- |
| **P1** | **Fragment Integration** | **IN PROGRESS** | Connect the existing `Fragment` classes to the `PromptLoader` and `WorkflowContext`. |
| **P1** | **YAML Switchover** | **IN PROGRESS** | Point all workflows to the `PromptLoader` and delete legacy Python prompt classes. |
| **P2** | **Metadata Split** | **PENDING** | Deconstruct `find_transcript_and_metadata` into atomic, single-purpose functions. |
| **P2** | **Security & Config** | **PENDING** | Shift API key retrieval from hard-coded patterns to `os.environ` in `BaseAIModel`. |
| **P3** | **Context Visibility** | **PENDING** | Add CLI commands to view current episode context and list available settings. |
| **P4** | **UX & Terminology** | **PENDING** | Standardize internal MAM terms (IP, Series, Season, Episode) across the CLI. |
| **P4** | **Documentation** | **PENDING** | Sync `README.md` and `ARCHITECTURE.md` with the new Fragment/YAML engine. |

---

### **Part 2: Detailed Implementation Notes**

#### **P1: Fragment Integration & YAML Switchover**
* **Fragment Chaining:** The `CompositeFragment` is built but needs a factory or registry to resolve paths automatically based on the directory hierarchy (Episode > Season > IP).
* **The "Clean Break":** Now that `PromptLoader` exists, refactor `WorkflowContext` to accept rendered templates rather than raw strings.
* **Path Decoupling:** Complete the removal of `content_root` defaults like `/home/bud/dev/Stream-Archive` from `file_manager.py` and move them strictly to `config.py`.

#### **P2: Metadata Atomicity & Security**
* **Split Strategy:** Create `Youtube_for_path()` and `locate_transcript_file()` as separate utilities. This prevents metadata lookups from failing when a transcript hasn't been staged yet.
* **Env Security:** Update `GeminiModel` to throw a clear error if `GOOGLE_API_KEY` is missing from the environment, rather than attempting to load a local config file.

#### **P3: Context Visibility**
* **Active Context:** Expand `handle_context_command` to not just set values, but to list available Arcs and Seasons found in the file system.

#### **P4: UX, Terminology, and Cleanup**
* **Terminology Mapping:** Standardize the "Mental Translation Layer" to ensure strict validation between generic code terms and brand-specific CLI output.
* **Legacy Cleanup:** Once the YAML engine is verified, remove legacy classes in `src/brand_cli/prompts/` and the base class in `src/brand_cli/prompts/base.py`.

---

### **Part 3: Reference Appendix**

#### **Architectural Risks & Mitigations**
* **Context Ambiguity:** Full-archive crawls (e.g., `Audit E001`) may cause lag. **Mitigation:** Implement fuzzy search or an LRU cache for `.series_metadata`.
* **Atomic Migration Failures:** Interruptions during "Inbox to Bundle" moves could cause partial folders. **Mitigation:** Use transactional file operations or a verification check.
* **Mapping Overhead:** The translation between MAM code terms and brand terms (e.g., "Biome") adds complexity. **Mitigation:** Centralize a `TermMapper` utility.

#### **Technical Guardrails**
* **Recursion Safety:** `CompositeFragment` currently has a `MAX_RECURSION` of 10 and circular reference detection—ensure this is tested in `conftest.py`.
* **Standardized Errors:** Use the format: `[FRAGMENT_ERROR] {fragment_type}@{path}: {reason}`.
* **Transcript Validation:** The `_has_no_audio` check is now the primary gatekeeper for session assets.

#### **YouTube Metadata Architect Role (Grandpa Bud Plays)**
* **The 150-Character Hook:** First sentence must contain Game Title (Valheim) and Primary Biome/Entity.
* **The Grandpa Anchor:** Always start the `[Grandpa's Legend]` section with: "I'm Grandpa and we're playing Valheim".
* **Natural Flow:** Avoid metadata blocks at the top; keywords must feel like natural storytelling.