import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from fetch_github_stats import summarize_languages


class LanguageTests(unittest.TestCase):
    def test_aggregate_bytes_not_repository_counts(self):
        result=summarize_languages([{'Python':900,'JavaScript':100},{'JavaScript':200}])
        self.assertEqual(list(result.items()),[('Python',900),('JavaScript',300)])

    def test_empty_repos_and_invalid_counts(self):
        self.assertEqual(summarize_languages([{},{}]),{})
        with self.assertRaises(ValueError):
            summarize_languages([{'Python':-1}])


if __name__=='__main__':
    unittest.main()
