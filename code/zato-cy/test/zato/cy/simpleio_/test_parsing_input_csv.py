# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from decimal import Decimal as decimal_Decimal
from uuid import UUID as uuid_UUID

# Zato
from zato.common import DATA_FORMAT
from zato.server.service import Service
from zato.simpleio import backward_compat_default_value, AsIs, Bool, CSV, CySimpleIO, Date, DateTime, Decimal, \
     Float, Int, Opaque, Text, UUID

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase
from zato.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

class CSVInputParsing(BaseTestCase):

# ################################################################################################################################

    def test_parse_basic_request(self):

        class MyService(Service):

            class SimpleIO:

                input = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'

                '''
                csv_dialect = ''
                csv_delimiter = ''
                csv_double_quote = ''
                csv_escape_char = ''
                csv_line_terminator = ''
                csv_quote_char = ''
                csv_quoting = ''
                csv_skip_initial_space = ''
                csv_strict = False
                '''

                class CSV:
                    dialect = ''
                    delimiter = ''
                    double_quote = ''
                    escape_char = ''
                    line_terminator = ''
                    quote_char = ''
                    quoting = ''
                    skip_initial_space = ''
                    strict = False

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = '222'
        ccc = 'ccc-ccc-ccc'
        eee = 'eee-444'

        # Note that 'ddd' is optional and we are free to skip it
        data = '{},{},{},,{}'.format(aaa, bbb, ccc, eee)

        input = MyService._sio.parse_input(data, DATA_FORMAT.CSV)
        self.assertIsInstance(input, list)

        input = input[0]
        self.assertEquals(input.aaa, aaa)
        self.assertEquals(input.bbb, int(bbb))
        self.assertEquals(input.ccc, ccc)
        self.assertEquals(input.ddd, backward_compat_default_value)
        self.assertEquals(input.eee, eee)

# ################################################################################################################################

    def test_parse_multiline(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa1 = 'aaa-111-1'
        bbb1 = '2221'
        ccc1 = 'ccc-ccc-ccc-1'
        eee1 = 'eee-444-1'

        aaa2 = 'aaa-111-2'
        bbb2 = '2222'
        ccc2 = 'ccc-ccc-ccc-2'
        eee2 = 'eee-444-2'

        # Note that 'ddd' is optional and we are free to skip it
        data  = '{},{},{},,{}'.format(aaa1, bbb1, ccc1, eee1)
        data += '\n'
        data += '{},{},{},,{}'.format(aaa2, bbb2, ccc2, eee2)

        input = MyService._sio.parse_input(data, DATA_FORMAT.CSV)
        self.assertIsInstance(input, list)

        input1 = input[0]
        input2 = input[1]

        self.assertEquals(input1.aaa, aaa1)
        self.assertEquals(input1.bbb, int(bbb1))
        self.assertEquals(input1.ccc, ccc1)
        self.assertEquals(input1.ddd, backward_compat_default_value)
        self.assertEquals(input1.eee, eee1)

        self.assertEquals(input2.aaa, aaa2)
        self.assertEquals(input2.bbb, int(bbb2))
        self.assertEquals(input2.ccc, ccc2)
        self.assertEquals(input2.ddd, backward_compat_default_value)
        self.assertEquals(input2.eee, eee2)

# ################################################################################################################################

    def test_parse_all_elem_types(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', AsIs('bbb'), Bool('ccc'), 'ddd', Date('eee'), DateTime('fff'), Decimal('ggg'), \
                    Float('jjj'), Int('mmm'), Opaque('ooo'), Text('ppp'), UUID('qqq')

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = 'bbb-222-bbb'
        ccc = 'True'
        ddd = ''
        eee = '1999-12-31'
        fff = '1988-01-29T11:22:33.0000Z'
        ggg = '123.456'

        jjj = '111.222'
        mmm = '9090'

        ooo = 'ZZZ-ZZZ-ZZZ'
        ppp = 'mytext'
        qqq = 'd011d054-db4b-4320-9e24-7f4c217af673'

        # Note that 'ddd' is optional and we are free to skip it
        data = ','.join([
            aaa, bbb, ccc, ddd, eee, fff, ggg, jjj, mmm, ooo, ppp, qqq
        ])

        input = MyService._sio.parse_input(data, DATA_FORMAT.CSV)
        self.assertIsInstance(input, list)
        input = input[0]

        self.assertEquals(input.aaa, aaa)
        self.assertEquals(input.bbb, bbb)
        self.assertTrue(input.ccc)
        self.assertEquals(input.ddd, '')

        self.assertIsInstance(input.eee, datetime)
        self.assertEquals(input.eee.year, 1999)
        self.assertEquals(input.eee.month, 12)
        self.assertEquals(input.eee.day, 31)

        self.assertIsInstance(input.fff, datetime)
        self.assertEquals(input.fff.year, 1988)
        self.assertEquals(input.fff.month, 1)
        self.assertEquals(input.fff.day, 29)

        self.assertEquals(input.ggg, decimal_Decimal(ggg))
        self.assertEquals(input.jjj, float(jjj))
        self.assertEquals(input.mmm, int(mmm))
        self.assertEquals(input.ooo, ooo)
        self.assertEquals(input.ppp, ppp)
        self.assertEquals(input.qqq, uuid_UUID(qqq))

# ################################################################################################################################
# ################################################################################################################################
