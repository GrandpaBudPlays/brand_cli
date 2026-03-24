import pytest
from unittest.mock import patch, MagicMock, mock_open
import sys
from brand_cli.Brand import main


def test_main_env_and_config_initialization(mocker):
    """Test environment and config initialization in main()"""
    mock_load_dotenv = mocker.patch("brand_cli.Brand.load_dotenv")
    mock_parse_args = mocker.patch("brand_cli.Brand.parse_cli_args",
                                 return_value=MagicMock(
                                     operation="Audit",
                                     session_id="S01E05",
                                     season="01",
                                     episode="05"))
    mocker.patch.dict("brand_cli.Brand.CONFIG", {"archive": {"content_root": "/test/archive"}})
    
    # Capture all print calls
    print_calls = []
    mocker.patch("builtins.print", side_effect=lambda *args, **kwargs: print_calls.append(args[0]))
    
    # Mock session with proper duration value
    mock_session = MagicMock(full_ep_id="S01E05", transcript_path="/valid/path", duration=1800.0)
    mocker.patch("brand_cli.Brand.prepare_session_assets", return_value=mock_session)
    
    # Mock Gemini upload and workflow execution
    mock_gemini = MagicMock()
    mock_gemini.upload_file.return_value = MagicMock()
    mocker.patch("brand_cli.Brand.GeminiModel", return_value=mock_gemini)
    
    mock_workflow = MagicMock()
    mocker.patch("brand_cli.Brand.get_workflow", return_value=mock_workflow)
    
    main()
    
    mock_load_dotenv.assert_called_once()
    mock_parse_args.assert_called_once()
    assert "--- Loading archive from: /test/archive ---" in print_calls


def test_main_session_and_model_orchestration(mocker):
    """Test session and model orchestration in main()"""
    mocker.patch("brand_cli.Brand.load_dotenv")
    mocker.patch("brand_cli.Brand.parse_cli_args",
                return_value=MagicMock(
                    operation="Audit",
                    session_id="S01E05",
                    season="01",
                    episode="05"))
    
    # Mock session with proper values
    mock_session = MagicMock(
        full_ep_id="S01E05",
        transcript_path="/valid/path",
        duration=1800.0
    )
    mock_prepare = mocker.patch("brand_cli.Brand.prepare_session_assets", return_value=mock_session)
    
    # Mock file operations
    mocker.patch("os.path.isfile", return_value=True)
    
    mock_gemini = MagicMock()
    mock_gemini.upload_file.return_value = MagicMock()
    mocker.patch("brand_cli.Brand.GeminiModel", return_value=mock_gemini)
    
    # Ensure ModelRunner is called
    mock_runner = MagicMock()
    runner_patch = mocker.patch("brand_cli.Brand.ModelRunner", return_value=mock_runner)
    
    mock_workflow = MagicMock()
    mocker.patch("brand_cli.Brand.get_workflow", return_value=mock_workflow)
    
    main()
    
    mock_prepare.assert_called_once()
    mock_gemini.upload_file.assert_called_once()
    assert runner_patch.called


def test_main_workflow_execution(mocker):
    """Test workflow execution in main()"""
    mocker.patch("brand_cli.Brand.load_dotenv")
    mocker.patch("brand_cli.Brand.parse_cli_args",
                return_value=MagicMock(
                    operation="Audit",
                    session_id="S01E05",
                    season="01",
                    episode="05"))
    
    mock_session = MagicMock(duration=1800.0)
    mocker.patch("brand_cli.Brand.prepare_session_assets", return_value=mock_session)
    
    mock_gemini = MagicMock()
    mocker.patch("brand_cli.Brand.GeminiModel", return_value=mock_gemini)
    
    mock_workflow = MagicMock()
    mocker.patch("brand_cli.Brand.get_workflow", return_value=mock_workflow)
    
    main()
    
    mock_workflow.execute.assert_called_once_with(mock_session, mock_gemini)


def test_main_error_handling(mocker):
    """Test error handling in main()"""
    mocker.patch("brand_cli.Brand.load_dotenv")
    mocker.patch("brand_cli.Brand.parse_cli_args",
                return_value=MagicMock(
                    operation="Audit",
                    session_id="S01E05",
                    season="01",
                    episode="05"))
    
    mock_session = MagicMock(duration=1800.0)
    mocker.patch("brand_cli.Brand.prepare_session_assets", return_value=mock_session)
    
    # Mock GeminiModel to raise error during initialization
    mocker.patch("brand_cli.Brand.GeminiModel", side_effect=ValueError("Test error"))
    
    # Mock workflow to prevent execution after error
    mock_workflow = MagicMock()
    mocker.patch("brand_cli.Brand.get_workflow", return_value=mock_workflow)

    mock_stderr = mocker.patch("sys.stderr.write")
    mock_exit = mocker.patch("sys.exit")

    main()
    
    from unittest.mock import call
    
    # Verify error was handled
    mock_stderr.assert_has_calls([call("Error: Test error"), call("\n")])
    mock_exit.assert_called_once_with(1)
    mock_workflow.execute.assert_not_called()
    mock_exit.assert_called_with(1)


def test_draft_workflow_skip_upload_when_pass_not_1(mocker):
    """Test upload skipped when workflow is draft and DRAFT_PASS != 1"""
    mocker.patch("brand_cli.Brand.load_dotenv")
    mocker.patch.dict("os.environ", {"DRAFT_PASS": "2"})
    mocker.patch("brand_cli.Brand.parse_cli_args",
                return_value=MagicMock(
                    operation="draft",
                    session_id="S01E05",
                    season="01",
                    episode="05"))

    # Mock session without is_draft_continue
    mock_session = MagicMock(
        full_ep_id="S01E05",
        transcript_path="/valid/path",
        duration=1800.0
    )
    mocker.patch("brand_cli.Brand.prepare_session_assets", return_value=mock_session)
    
    # Correct os.getenv mock with default parameter
    mocker.patch("os.getenv", 
                side_effect=lambda k, default=None: "2" if k == "DRAFT_PASS" else default)
    
    mock_gemini = MagicMock()
    mocker.patch("brand_cli.Brand.GeminiModel", return_value=mock_gemini)
    
    mock_workflow = MagicMock()
    mocker.patch("brand_cli.Brand.get_workflow", return_value=mock_workflow)
    
    main()
    
    mock_gemini.upload_file.assert_not_called()
    mock_workflow.execute.assert_called_once()


def test_draft_workflow_upload_when_pass_1(mocker):
    """Test upload occurs when workflow is draft and DRAFT_PASS == 1"""
    mocker.patch("brand_cli.Brand.load_dotenv")
    mocker.patch.dict("os.environ", {"DRAFT_PASS": "1"})
    mocker.patch("brand_cli.Brand.parse_cli_args",
                return_value=MagicMock(
                    operation="draft",  # Uppercase D to match registry
                    session_id="S01E05",
                    season="01",
                    episode="05"))

    mock_session = MagicMock(
        full_ep_id="S01E05",
        transcript_path="/valid/path",
        duration=1800.0
    )
    mocker.patch("brand_cli.Brand.prepare_session_assets", return_value=mock_session)
    
    mock_gemini = MagicMock()
    mocker.patch("brand_cli.Brand.GeminiModel", return_value=mock_gemini)
    
    # Mock the workflow registry
    mock_workflow = MagicMock()
    mocker.patch("brand_cli.Brand.get_workflow", return_value=mock_workflow)
    
    main()
    
    mock_gemini.upload_file.assert_called_once_with(
        file_path="/valid/path",
        display_name="Transcript_S01E05"
    )
    mock_workflow.execute.assert_called_once()