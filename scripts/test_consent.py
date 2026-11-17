"""Check production and tracking-disabled output without touching published pages."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ConsentBuildTest(unittest.TestCase):
    def test_consent_order_and_disabled_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            for directory in ('scripts', 'content'):
                shutil.copytree(ROOT/directory, site/directory)
            for container in ('GTM-MW95NM39', ''):
                subprocess.run([sys.executable, site/'scripts/build.py'], check=True,
                               env={**os.environ, 'GTM_ID': container})
                for page in site.rglob('index.html'):
                    html = page.read_text()
                    if container:
                        self.assertLess(html.index("analytics_storage: 'denied'"),
                                        html.index('googletagmanager.com/gtm.js'))
                        self.assertIn('id="cookie-banner"', html)
                    else:
                        self.assertNotIn('googletagmanager.com', html)
                        self.assertNotIn('id="cookie-banner"', html)
                        self.assertNotIn('data-cookie-preferences', html)


if __name__ == '__main__':
    unittest.main()
