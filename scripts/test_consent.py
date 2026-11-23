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
                        # GTM loader must live inside __loadGTM and only run after consent.
                        self.assertEqual(html.count('googletagmanager.com/gtm.js'), 1)
                        self.assertLess(html.index('window.__loadGTM = function'),
                                        html.index('googletagmanager.com/gtm.js'))
                        self.assertLess(html.index('cerez_onayi=kabul'),
                                        html.index('window.__loadGTM();'))
                    else:
                        self.assertNotIn('googletagmanager.com', html)
                        self.assertNotIn('id="cookie-banner"', html)
                        self.assertNotIn('data-cookie-preferences', html)


class ConsentScriptTest(unittest.TestCase):
    def test_loader_runs_only_on_accept(self):
        script = (ROOT/'assets/consent.js').read_text()
        self.assertIn('window.__loadGTM?.()', script)
        accept_block = script.split("value === 'kabul'", 1)[1].split("value === 'red'", 1)[0]
        self.assertIn('__loadGTM', accept_block)
        self.assertNotIn('__loadGTM', script.split("value === 'kabul'", 1)[0])


if __name__ == '__main__':
    unittest.main()
