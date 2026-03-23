import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from brand_cli.workflows.draft import DraftWorkflow

class TestDraftWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflow = DraftWorkflow()
        self.mock_context = MagicMock()
        self.mock_model = MagicMock()
        
    @patch('brand_cli.workflows.draft.read_file')
    def test_load_brand_assets_all_found(self, mock_read_file):
        """Test when all brand asset files are found"""
        mock_read_file.side_effect = [
            "Ulf content",  # ulf
            "Protocol content",  # protocol
            "Brand content"  # brand
        ]
        
        base_dir = Path("/test/path")
        result = self.workflow._load_brand_assets(base_dir)
        
        self.assertEqual(result["ulf"], "Ulf content")
        self.assertEqual(result["protocol"], "Protocol content")
        self.assertEqual(result["brand"], "Brand content")
        
    @patch('brand_cli.workflows.draft.read_file')
    def test_load_brand_assets_none_found(self, mock_read_file):
        """Test when no brand asset files are found"""
        mock_read_file.side_effect = ["", "", ""]
        
        base_dir = Path("/test/path")
        result = self.workflow._load_brand_assets(base_dir)
        
        self.assertEqual(result["ulf"], "")
        self.assertEqual(result["protocol"], "")
        self.assertEqual(result["brand"], "")
        
    @patch('brand_cli.workflows.draft.read_file')
    def test_load_brand_assets_mixed_found(self, mock_read_file):
        """Test when some brand asset files are found"""
        mock_read_file.side_effect = [
            "Ulf content",  # ulf found
            "",  # protocol not found
            "Brand content"  # brand found
        ]
        
        base_dir = Path("/test/path")
        result = self.workflow._load_brand_assets(base_dir)
        
        self.assertEqual(result["ulf"], "Ulf content")
        self.assertEqual(result["protocol"], "")
        self.assertEqual(result["brand"], "Brand content")

if __name__ == '__main__':
    unittest.main()