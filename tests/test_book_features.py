import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/md-book-builder'))
from book_features import feature_policy


class FeatureTests(unittest.TestCase):
    def test_flags_and_author_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'book.toml'
            config.write_text('[preprocessor.mermaid]\ncommand = "custom --flag"\n[preprocessor.svgbob]\n')
            self.assertFalse(feature_policy(config, mermaid=True).mermaid)
            self.assertTrue(feature_policy(config).svgbob)
            self.assertFalse(feature_policy(config, svgbob=False).svgbob)
            config.write_text('[book]\ntitle="Book"\n')
            self.assertFalse(feature_policy(config).mermaid)
            self.assertTrue(feature_policy(config, mermaid=True).mermaid)
