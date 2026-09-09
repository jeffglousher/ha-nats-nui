import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('provision','/provision.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.marker=Path(self.tmp.name)/'done'
        self.mock=patch.object(p,'MARKER',self.marker);self.mock.start();self.addCleanup(self.mock.stop)
    def test_existing_connections_are_never_modified(self):
        with patch.object(p,'request',return_value=[{'name':'user edited'}]) as req:
            self.assertTrue(p.attempt());self.assertTrue(self.marker.exists());self.assertEqual(req.call_count,1)
    def test_import_once_and_deletion_is_respected(self):
        host=p.BROKER.replace('_','-');value={'hosts':['nats://'+host+':4222']}
        with patch.object(p,'request',side_effect=[[],{'result':'ok','data':{'state':'started','hostname':host}},value,[],{'id':'new'}]) as req:
            self.assertTrue(p.attempt());self.assertEqual(req.call_args.args[1],value)
        with patch.object(p,'request') as req:
            self.assertTrue(p.attempt());req.assert_not_called()
    def test_absent_broker_can_be_installed_later(self):
        with patch.object(p,'request',side_effect=[[],{'result':'ok','data':{'state':'stopped'}}]):
            self.assertFalse(p.attempt());self.assertFalse(self.marker.exists())
    def test_ambiguous_import_is_not_retried(self):
        host=p.BROKER.replace('_','-');value={'hosts':['nats://'+host+':4222']}
        with patch.object(p,'request',side_effect=[[],{'result':'ok','data':{'state':'started','hostname':host}},value,[],OSError('interrupted')]):
            with self.assertRaises(OSError):p.attempt()
        with patch.object(p,'request') as req:
            self.assertTrue(p.attempt());req.assert_not_called()

unittest.main()
