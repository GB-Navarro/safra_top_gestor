"""Integração com o sincronizador documental: pacotes versionados são imutáveis (somente leitura do script)."""
import sys
import unittest

from analysis.common import REPO

sys.path.insert(0, str(REPO / "scripts"))
import sync_project_docs  # noqa: E402

BUNDLES = REPO / "outputs/draft/analysis_bundle"


class SyncDoesNotTouchBundles(unittest.TestCase):
    def test_bundle_markdown_not_managed(self):
        managed = sync_project_docs.managed_docs()
        self.assertFalse([p for p in managed if BUNDLES in p.parents], "sincronizador não pode inserir banner em pacote publicado")

    def test_bundle_files_not_in_draft_manifest(self):
        listed = sync_project_docs.manifest_files(REPO / "outputs/draft")
        self.assertFalse([f for f in listed if f["path"].startswith("outputs/draft/analysis_bundle/")])


if __name__ == "__main__":
    unittest.main()
