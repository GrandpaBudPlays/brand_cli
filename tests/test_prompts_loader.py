import pytest
from pathlib import Path
from brand_cli.prompts.loader import PromptLoader

@pytest.fixture
def test_prompts_dir(tmp_path):
    """Create a temporary prompts directory structure for testing"""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    
    # Create test prompt file
    audit_prompt = prompts_dir / "audit.yaml"
    audit_prompt.write_text("""
name: "Audit"
system_prompt: |
  Test system {{ fragments.test_var }}
user_prompt: |
  Test user {{ session.test_data }}
""")
    
    # Create game prompt file
    games_dir = prompts_dir / "games"
    games_dir.mkdir()
    game_prompt = games_dir / "testgame.yaml"
    game_prompt.write_text("""
name: "TestGame"
system_prompt: |
  Game system {{ fragments.game_var }}
user_prompt: |
  Game user {{ session.game_data }}
""")
    
    return str(prompts_dir)


def test_load_regular_prompt(test_prompts_dir):
    """Test loading a regular prompt"""
    loader = PromptLoader(test_prompts_dir)
    result = loader.load_prompt(
        "audit",
        fragments={"test_var": "VALUE"},
        session_data={"test_data": "123"}
    )
    
    assert result["system_prompt"] == "Test system VALUE"
    assert result["user_prompt"] == "Test user 123"


def test_load_game_prompt(test_prompts_dir):
    """Test loading a game-specific prompt"""
    loader = PromptLoader(test_prompts_dir)
    result = loader.load_prompt(
        "audit",
        fragments={"game_var": "GAME_VALUE"},
        session_data={"game_data": "456", "game": "testgame"}
    )
    
    assert result["system_prompt"] == "Game system GAME_VALUE"
    assert result["user_prompt"] == "Game user 456"


def test_missing_prompt(test_prompts_dir):
    """Test handling of missing prompt file"""
    loader = PromptLoader(test_prompts_dir)
    with pytest.raises(ValueError, match="Prompt file not found for missing"):
        loader.load_prompt("missing")


def test_invalid_yaml(tmp_path):
    """Test handling of invalid YAML"""
    prompts_dir = tmp_path / "bad_prompts"
    prompts_dir.mkdir()
    bad_file = prompts_dir / "bad.yaml"
    bad_file.write_text("invalid: yaml: [")
    
    loader = PromptLoader(str(prompts_dir))
    with pytest.raises(ValueError, match="Invalid YAML"):
        loader.load_prompt("bad")