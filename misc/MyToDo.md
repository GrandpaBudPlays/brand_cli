## New Items to prioritize and Organize


## 🛠️ Detailed Implementation Notes

- Ability for the system to self diagnose. (very low priority, long range goals)
- Cleanup the fragment implementation. Determine if the fragment class should load files or not.
- Add 000-Global to the end of the directory search code
- Move the creative pass output markdown into a yaml file.
- stop saving model name in the file name
- stop saving multiple versions of the same data (json and md etc)
- Cleanup pathing, move to a dictionary of paths that is resolved at the start of a workflow. remove all hard coded paths.
- Multi-pass Gold worrkflow. Post MVP (see notes below)
- Consider these architectural improvements:
   - Add proper error handling for missing prompt files
   - Make the prompts directory path configurable
   - Add validation for chapter data structure
- Improve arg handling to Zero pad Saga and Episode numbers
- Integrate with DaVinci Resolve
- remove  if not hasattr(result, '_mock_return_value'): from base.py workflow

# MyToDo.md

## 📊 Prioritized Task Dashboard

| Priority | Task Label | Status | Brief Description |
| :--- | :--- | :--- | :--- |
| P1 | Video Chapters | PENDING | Rethink/Improve Video Chapters approach: persona-driven titles and visual styling for timestamps. |
| P1 | SEO Optimization | PENDING | Maximize all 500 characters for SEO optimized YouTube tags, mapping custom lingo to searchable terms. |
| P1 | Core Refactor | PENDING | Move Transcript logic out of file_manager and remove hard-coded paths. |
| P1 | Fragment Integration | IN PROGRESS | Connect the existing Fragment classes to the PromptLoader and WorkflowContext. |
| P1 | Core Refactor | IN PROGRESS | Implement Asset Manifest & PathResolver; replace hard-coded paths with a validated PathDict; add 000-Global fallback. |
| P2 | Documentation | PENDING | Sync README.md and ARCHITECTURE.md with the new Fragment/YAML engine. |
| P2 | Core Refactor | PENDING | Implement path dictionary; remove hard-coded paths; add 000-Global to directory search. |
| P2 | Data Integrity | PENDING | Stop saving model names in filenames; stop saving redundant versions (JSON vs MD). |
| P2 | YAML Switchover | IN PROGRESS | Migrate all workflows to PromptLoader (including creative pass output) and delete legacy classes. |
| P3 | Metadata Split | PENDING | Deconstruct find_transcript_and_metadata into atomic, single-purpose functions. |
| P3 | Robustness | PENDING | Add error handling for missing prompt files and validation for chapter data structures. |
| P3 | UX: Arg Handling | PENDING | Improve CLI argument handling to automatically Zero-pad Saga and Episode numbers. |
| P3 | Video Chapters | PENDING | Rethink/Improve Video Chapters approach: persona-driven titles and visual styling. |
| P3 | Metadata Split | PENDING | Deconstruct find_transcript_and_metadata into atomic, single-purpose functions. |
| P4 | Security & Config | PENDING | Shift API key retrieval from hard-coded patterns to os.environ in BaseAIModel. |
| P3 | SEO Optimization | PENDING | Maximize all 500 characters for SEO optimized YouTube tags, mapping custom lingo to searchable terms. |
| P4 | Context & Config | PENDING | Add CLI commands for context visibility; make the prompts directory path configurable. |
| P5 | Context Visibility | PENDING | Add CLI commands to view current episode context and list available settings. |
| P5 | UX & Terminology | PENDING | Standardize internal MAM terms (IP, Series, Season, Episode) across the CLI. |
| P5 | Long-Range Goals | PENDING | Multi-pass Gold workflow (Post-MVP); implement system self-diagnosis logic. |

## 🛠️ Detailed Implementation Notes

### Refactoring the Draft Workflow (post MVP)
- **Fragment Engine:** Transition to the Polymorphic Fragment Engine to handle Static, Tagged, and Random fragments.
- **YAML Templates:** Complete migration of all workflows to use external YAML templates via the `PromptLoader`.
- **Metadata Atomicity:** Split metadata retrieval to ensure it is handled independently from the transcript data.
- **Security:** Ensure all API keys are managed through environmental variables rather than being stored in the codebase.

- **Multipass Gold Workflow:**
    - Why Multi-Pass is the "Pro" Move
        1. **The "Context Window" Advantage** 
        In a single pass, the AI has to hold the transcript, the YouTube rules, the "Brand voice" for the ledger, and the logic for three different clip types all at once.

            - **Multi-Pass:** You feed the AI only what it needs for that specific task. For Type A (Shorts), it only needs to look for high-energy hooks, not the overall narrative arc.

        2. **Specific "Personas" per Pass** 
        
        You can swap the system_instruction for each pass:  
        - **Pass 1 (The Editor):** Focuses strictly on timestamps and accuracy for the Timeline.
        - **Pass 2 (The Social Lead):** Focuses on "clickability" and hooks for Type A (Shorts).
        - **Pass 3 (The Writer):** Focuses on the "Brand voice" for the Ledger Entry.

        3. **Error Isolation (Anti-Fragility)**   
        If the AI hallucinates a timestamp in a single-pass prompt, the whole JSON object might fail to parse. In a multi-pass system, if the "Shorts" pass fails, your "Chapters" and "Ledger" are still perfectly intact.
        
        The "Post-MVP" Architecture  

        | Pass | Input | Goal | Output |
        | :--- | :--- | :--- | :--- |
        | Pass 1: Structuring | Raw Transcript | Cleaned Timeline & Chapters | chapters.json | 
        | Pass 2: Mining | Chapters + Transcript | Identifying Gold (A, B, C) | highlights.json |
        | Pass 3: Refining | Highlights | Writing Ledger & Social Copy | final_metadata.json |


## 📚 Reference Appendix

### Architectural Risks
- **Context Ambiguity:** Risks associated with improper state management in the `WorkflowContext`.
- **Migration Failures:** Potential issues when switching from Python-based prompts to YAML.

### Technical Guardrails
- **Recursion Safety:** Prevent circular logic during fragment resolution.
- **Standardized Error Handling:** Consistent error output across all CLI operations.

### YouTube Metadata Architect Guidelines
- **150-Character Hook:** Ensure descriptions begin with a high-impact narrative hook.
- **"Grandpa Anchor":** Maintain brand identity through the established persona in the description blocks.


