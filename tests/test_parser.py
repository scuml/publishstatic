import context

import unittest
from publishstatic,management.commands.publishstatic import handle


class StorageSuite(unittest.TestCase):



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StorageSuite))
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
