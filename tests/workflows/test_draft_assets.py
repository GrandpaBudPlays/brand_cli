import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from brand_cli.workflows.draft import DraftWorkflow

class TestDraftAssets(unittest.TestCase):
    def setUp(self):
        self.workflow = DraftWorkflow()
        self.mock_context = MagicMock()
        self.mock_model = MagicMock()
        
    @patch('brand_cli.workflows.draft.read_file')
    def test_load_brand_assets_all_found(self, mock_read_file):
        """Test when all brand asset files are found"""
        mock_read_file.side_effect = [
            "Brand Voice content",    # First file loaded (grandpa)
            "Protocol content",       # Second file (protocol)
            "Lexicon content",        # Third file (lexicon)
            "Ulf content",            # Fourth file (ulf)
            "Series content"          # Fifth file (series)
        ]
    
        base_dir = Path("/test/path")
        result = self.workflow._load_brand_assets(base_dir)
    
        self.assertEqual(result["grandpa"], "Brand Voice content")
        self.assertEqual(result["protocol"], "Protocol content")
        self.assertEqual(result["lexicon"], "Lexicon content")
        self.assertEqual(result["ulf"], "Ulf content")
        self.assertEqual(result["series"], "Series content")

    @patch('brand_cli.workflows.draft.read_file')
    def test_load_brand_assets_none_found(self, mock_read_file):
        """Test when no brand asset files are found"""
        mock_read_file.return_value = ""
        
        base_dir = Path("/test/path")
        result = self.workflow._load_brand_assets(base_dir)
        
        # Check all expected keys exist with empty values
        self.assertEqual(result.get("protocol", ""), "")
        self.assertEqual(result.get("ulf", ""), "")
        self.assertEqual(result.get("brand", ""), "")

    @patch('brand_cli.workflows.draft.read_file')
    def test_load_brand_assets_mixed_found(self, mock_read_file):
        """Test when some brand asset files are found"""
        mock_read_file.side_effect = [
            "",                       # First file not found (grandpa)
            "Protocol content",       # Second file found (protocol)
            "",                       # Third file not found (lexicon)
            "Ulf content",            # Fourth file found (ulf)
            ""                        # Fifth file not found (series)
        ]
    
        base_dir = Path("/test/path")
        result = self.workflow._load_brand_assets(base_dir)
    
        self.assertEqual(result["protocol"], "Protocol content")
        self.assertEqual(result["ulf"], "Ulf content")
        self.assertEqual(result.get("grandpa", ""), "")
        self.assertEqual(result.get("lexicon", ""), "")
        self.assertEqual(result.get("series", ""), "")

if __name__ == '__main__':
    unittest.main()