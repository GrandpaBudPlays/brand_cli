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
        file_map = {
            ".series_metadata": "Series content",
            "Descriptions.md": "Protocol content",
            "Saga-Lexicon-Valheim.md": "Lexicon content",
            "Ulf Persona.md": "Ulf content",
            "Conrad Persona.md": "Conrad content",
            "Brand-Voice.md": "Brand Voice content"
        }
        # Use a function to return content based on the filename in the path, ignoring call order
        mock_read_file.side_effect = lambda path: next((v for k, v in file_map.items() if k in str(path)), "")
    
        base_dir = Path("/test/path")
        result = self.workflow._load_brand_assets(base_dir)
    
        self.assertEqual(result["grandpa"], "Brand Voice content")
        self.assertEqual(result["protocol"], "Protocol content")
        self.assertEqual(result["lexicon"], "Lexicon content")
        self.assertEqual(result["ulf"], "Ulf content")
        self.assertEqual(result["conrad"], "Conrad content")
        self.assertEqual(result["series"], "Series content")

    @patch('brand_cli.workflows.draft.read_file')
    def test_load_brand_assets_none_found(self, mock_read_file):
        """Test when no brand asset files are found"""
        mock_read_file.return_value = ""
        
        base_dir = Path("/test/path")
        result = self.workflow._load_brand_assets(base_dir)
        
        # Check all expected keys exist with empty values
        self.assertEqual(result.get("series", ""), "")
        self.assertEqual(result.get("protocol", ""), "")
        self.assertEqual(result.get("lexicon", ""), "")
        self.assertEqual(result.get("ulf", ""), "")
        self.assertEqual(result.get("conrad", ""), "")
        self.assertEqual(result.get("grandpa", ""), "")

    @patch('brand_cli.workflows.draft.read_file')
    def test_load_brand_assets_mixed_found(self, mock_read_file):
        """Test when some brand asset files are found"""
        file_map = {
            "Descriptions.md": "Protocol content",
            "Ulf Persona.md": "Ulf content",
        }
        # Return content if filename exists in map, else empty string
        mock_read_file.side_effect = lambda path: next((v for k, v in file_map.items() if k in str(path)), "")
    
        base_dir = Path("/test/path")
        result = self.workflow._load_brand_assets(base_dir)
    
        self.assertEqual(result["protocol"], "Protocol content")
        self.assertEqual(result["ulf"], "Ulf content")
        self.assertEqual(result.get("lexicon", ""), "")
        self.assertEqual(result.get("series", ""), "")
        self.assertEqual(result.get("conrad", ""), "")
        self.assertEqual(result.get("grandpa", ""), "")

if __name__ == '__main__':
    unittest.main()