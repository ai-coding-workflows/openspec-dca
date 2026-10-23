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

    def test_d2_is_optional_and_preserves_custom_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'book.toml'
            config.write_text('[book]\ntitle="Book"\n')
            self.assertFalse(feature_policy(config).d2)
            self.assertTrue(feature_policy(config, d2=True).d2)
            config.write_text('[preprocessor.d2]\nlayout="elk"\n')
            self.assertTrue(feature_policy(config).d2)
            self.assertFalse(feature_policy(config, d2=False).d2)
            config.write_text('[preprocessor.d2]\ncommand="custom-d2"\n')
            self.assertFalse(feature_policy(config, d2=True).d2)
