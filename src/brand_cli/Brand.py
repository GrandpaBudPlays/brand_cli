import os
import sys
from dotenv import load_dotenv

# Updated to use package-absolute imports for the CLI entry point
from brand_cli.config import CONFIG, CONTEXT
from brand_cli.ai.gemini import GeminiModel
from brand_cli.ai.model_runner import ModelRunner
from brand_cli.file_manager import (
    parse_cli_args,
    prepare_session_assets,
)
from brand_cli.workflows import get_workflow

DEFAULT_TIMEOUT = 300

def main():
    """
    The main entry point for the 'brand' CLI command.
    Mapped in pyproject.toml as brand_cli.Brand:main
    """
    load_dotenv()

    # The parse_cli_args handles the 'Context' operation directly and exits if so.
    args = parse_cli_args()
    operation = args.operation
    
    archive_root = CONFIG["archive"].get("content_root", "Unknown")
    
    print(f"--- Loading archive from: {archive_root} ---")
    
    print(f"Active Context -> IP: {CONTEXT.get('ip') or 'All'} | Series: {CONTEXT.get('series') or 'All'} | Season: {CONTEXT.get('season') or 'None'}")
    
    session = prepare_session_assets(args)

    print(f"--- Processing (Operation: {operation}) on {session.full_ep_id}  ---")
    
    try:
        gemini_model = GeminiModel()
        model_runner = ModelRunner()
        print("Client initialized.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Let the registry resolve and execute the workflow
    workflow = get_workflow(operation)
    workflow.execute(session, gemini_model)

if __name__ == "__main__":
    main()