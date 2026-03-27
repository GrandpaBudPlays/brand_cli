## New Items to prioritize and Organize
Ability for the system to self diagnose. (very low priority, long range goals)
Cleanup the fragment implementation. Determine if the fragment class should load files or not.
Add 000-Global to the end of the directory search code
Move the creative pass output markdown into a yaml file.
stop saving model name in the file name
stop saving multiple versions of the same data (json and md etc)


# MyToDo.md

## 📊 Prioritized Task Dashboard

| Priority | Task Label | Status | Brief Description |
| :--- | :--- | :--- | :--- |
| P1 | Fragment Integration | IN PROGRESS | Connect the existing Fragment classes to the PromptLoader and WorkflowContext. |
| P1 | YAML Switchover | IN PROGRESS | Point all workflows to the PromptLoader and delete legacy Python prompt classes. |
| P1 | Core Refactor | PENDING | Move Transcript logic out of file_manager and remove hard-coded paths. |
| P1 | Video Chapters | PENDING | Rethink/Improve Video Chapters approach: persona-driven titles and visual styling for timestamps. |
| P2 | Metadata Split | PENDING | Deconstruct find_transcript_and_metadata into atomic, single-purpose functions. |
| P2 | Security & Config | PENDING | Shift API key retrieval from hard-coded patterns to os.environ in BaseAIModel. |
| P2 | SEO Optimization | PENDING | Maximize all 500 characters for SEO optimized YouTube tags, mapping custom lingo to searchable terms. |
| P3 | Context Visibility | PENDING | Add CLI commands to view current episode context and list available settings. |
| P4 | UX & Terminology | PENDING | Standardize internal MAM terms (IP, Series, Season, Episode) across the CLI. |
| P4 | Documentation | PENDING | Sync README.md and ARCHITECTURE.md with the new Fragment/YAML engine. |

## 🛠️ Detailed Implementation Notes

### Refactoring the Draft Workflow
- **Fragment Engine:** Transition to the Polymorphic Fragment Engine to handle Static, Tagged, and Random fragments.
- **YAML Templates:** Complete migration of all workflows to use external YAML templates via the `PromptLoader`.
- **Metadata Atomicity:** Split metadata retrieval to ensure it is handled independently from the transcript data.
- **Security:** Ensure all API keys are managed through environmental variables rather than being stored in the codebase.

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


