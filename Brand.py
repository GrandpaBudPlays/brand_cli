import os
import sys
from dotenv import load_dotenv

from config import CONFIG, CONTEXT
from ai.gemini import GeminiModel
from ai.model_runner import ModelRunner
from file_manager import (
    parse_cli_args,
    prepare_session_assets,
)
from workflows import get_workflow


DEFAULT_TIMEOUT = 300


if __name__ == "__main__":
    load_dotenv()

    # The parse_cli_args now handles the 'Context' operation directly and exits if so.
    args = parse_cli_args()
    operation = args.operation
    
    archive_root = CONFIG["archive"].get("content_root", "Unknown")
    
    print(f"--- Loading archive from: {archive_root} ---")
    
    print(f"Active Context -> IP: {CONTEXT.get('ip') or 'All'} | Series: {CONTEXT.get('series') or 'All'} | Season: {CONTEXT.get('season') or 'None'}")
    
    session = prepare_session_assets(args)

    print(f"--- Processing (Operation: {operation}) on {session.full_ep_id}  ---")
    gemini_model = GeminiModel(api_key=os.getenv('GEMINIAPIKEY'))
    model_runner = ModelRunner()

    print("Client initialized.")

    # Let the registry resolve and execute the workflow
    workflow = get_workflow(operation)
    workflow.execute(session, gemini_model)
