#  -------------------------------------------------------------------------
#  Copyright (C) 2019 Daniel Werner Lima Souza de Almeida
#                     dwlsalmeida@gmail.com
#  -------------------------------------------------------------------------
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
#  -------------------------------------------------------------------------


import sys
import os
# TODO: Improve this, how is this not in there already?
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import unittest

import test_intermediary_representation
import test_RamsesBlenderExporter

def run():
    suite_1 = unittest.defaultTestLoader.\
            loadTestsFromTestCase(test_intermediary_representation.TestVectorUnpack)
    suite_2 = unittest.defaultTestLoader.\
            loadTestsFromTestCase(test_intermediary_representation.TestFind)

    suite_3 = unittest.defaultTestLoader.\
            loadTestsFromTestCase(test_RamsesBlenderExporter.TestRamsesBlenderExporter)

    all_tests = unittest.TestSuite([suite_1,
                                    suite_2,
                                    suite_3])

    success = unittest.TextTestRunner().run(all_tests).wasSuccessful()
    if not success:
        raise Exception('Unit tests failed')

run()
