import pytest
from brand_cli.transcript import Transcript


def test_no_audio_detection():
    """Test that 'no audio' detection works case-insensitively"""
    with pytest.raises(ValueError):
        Transcript("NO AUDIO: This transcript has no audio content", "ep1").get_content()
    
    # Should not raise for normal content
    assert Transcript("Normal transcript", "ep2").get_content() == "Normal transcript"


def test_empty_transcript():
    """Test handling of empty transcripts"""
    with pytest.raises(ValueError):
        Transcript("", "ep3").get_content()


def test_long_transcript():
    """Test handling of very long transcripts"""
    long_content = "a" * 10000
    assert Transcript(long_content, "ep4").get_content() == long_content