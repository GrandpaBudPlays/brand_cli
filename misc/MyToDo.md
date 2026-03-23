# TODO List
# Priority One Changes
- remove Transcript functions from file_manager, change all calls to Transcript.
- find and remove all hard coded paths from file_manager
## Audit: I recommend adding a final instruction to the agent to delete the misc/ folder leftovers once the src/ integration is verified.

# Priority 2 Changes
## 🎯 Project Goal
Implement a polymorphic "Fragment" engine for Brand-CLI to handle text assembly for both AI Prompts (prefixes/system instructions) and Final Output (suffixes/boilerplate).
- convert draft to use the Random Fragment
- Change Feedback, ask AI for the list of filler words. Count in python.

# Priority 3 Changes
## Can we change file_manager.load_transcript_asset to a more generic load_archive_asset
- Review README.md, ARCHITECTURE.md, ./docs/brand_cli.md
- Add ability to view the current context
- Add ability to list available context settings (read the directory structure)
- Modify AI class to use user defined API key env variable
- Split find_transcript_and_metadata into two separate functions, find_transcript and Find Metadata. Change this function to call the two supporting functions.

 
# Priority 4 Changes
- Modify Help to use defined terms for IP, Series, Season, Episode
- Does SessonData class belong in fileManager?


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

### Long Term Changes
#### Phase 4: Optimization (Back Burner)
* Research long-term persistent File IDs and custom TTL logic in `.brand_context`. Do we want to have the file live in google longer so we can run back tasks at another time?


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

The current implementation of AI prompts in the codebase relies on a Fragment pattern where prompt strings are defined as Python class attributes or return values within Python modules. While this approach provides programmatic flexibility, it tightly couples the natural language content of the prompt with the execution logic of the application. This makes the code difficult to parse visually and prevents non-developers—or even developers looking for a quick adjustment—from modifying the AI's behavior without editing and redeploying the source code.

To address these issues, the architecture should move toward a decoupled, template-based system.

### 1. Externalize Prompts to a Structured Format
Instead of embedding multi-line strings inside Python classes, all prompt content should be moved to external files, such as YAML or Markdown. YAML is particularly effective because it allows you to store metadata alongside the prompt text, such as the model version, temperature settings, or descriptions of required variables.

By creating a dedicated directory for these templates, the "what" (the prompt text) is physically separated from the "how" (the Python code that calls the API). This immediately improves readability because the Python files are reduced to pure logic, and the prompt files are focused entirely on the language being sent to the AI.

### 2. Implement a Template Engine
To bridge the gap between external files and Python logic, a template engine like Jinja2 should be used. This allows for dynamic variable injection using a standardized syntax that is common in professional web and CLI development.

In this model, the Python code simply identifies which template it needs and passes a dictionary of data to it. The template engine then handles the string formatting, loops, and conditional logic. This replaces complex string concatenation or the current fragment-composition logic with a clear, declarative structure that any user can read and understand.

### 3. Support for User-Level Overrides
To solve the issue of users being unable to modify prompts, the system should implement a hierarchical loading strategy. The application can look for prompt files in three locations in order of priority:

First, a user-specific directory (e.g., ~/.config/brand-cli/prompts/).
Second, a project-specific directory within the current working folder.
Third, the default system templates bundled with the package.

If a user wants to tweak the "Audit" prompt, they simply copy the default YAML file to their local config folder and edit the text. The CLI will detect the local version and use it instead of the hardcoded default. This provides full customizability without requiring the user to touch a single line of Python.

### 4. Transitioning the Fragment System
The current fragment-based composition—where different pieces of a prompt are assembled based on context—can be preserved but modernized. Instead of having "Fragment" classes in Python, these fragments should be defined as "Blocks" within a single template file or as small, reusable sub-templates.

The Python logic would then "include" these blocks as needed. This maintains the flexibility of the current system while ensuring that the entire prompt remains visible and editable as a single, cohesive document rather than a scattered collection of code snippets.

### 5. Documentation and Schema Validation
To ensure that users don't break the application when editing prompts, each prompt should have an associated schema. This can be as simple as a comment at the top of the YAML file listing the required variables. This turns the prompt files into a self-documenting interface, making it clear to the user exactly which data points are available for them to use in their custom instructions.


---

# Breakdown: Implementing an Automated Testing Suite and Framework

Implementing an automated testing suite is best approached by following the "Testing Pyramid" philosophy: a broad base of fast unit tests, a middle layer of integration tests, and a small top layer of end-to-end tests.



[Image of the testing pyramid]


### Chunk 5: Testing the Interface
Verify the user-facing entry points, such as a Command Line Interface (CLI).

1. **Simulation Runners:** Use specific testing tools (like a CLI runner) to simulate terminal interactions and capture output.
2. **Success and Failure Paths:** Write tests to confirm the application returns correct exit codes and helpful error messages for both valid and invalid user inputs.

### Chunk 6: Continuous Integration (CI) and Automation
Automate execution so tests run on every code change.



[Image of a CI/CD pipeline workflow]


1. **CI Pipelines:** Configure automated workflows to run the full test suite on every code push or pull request.
2. **Static Analysis:** Add steps to the pipeline for **linting** and **type checking** to catch structural issues automatically.
3. **Coverage Reports:** Use coverage tools to generate reports showing which parts of the codebase are exercised by tests, helping to identify gaps in the testing strategy.


