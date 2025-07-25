# Copyright 2017 Hewlett-Packard Enterprise Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
SNMP hardware types.
"""

from ironic.drivers import generic
from ironic.drivers.modules import fake
from ironic.drivers.modules import noop_mgmt
from ironic.drivers.modules import snmp


class SNMPHardware(generic.GenericHardware):
    """SNMP Hardware type """

    # NOTE(JayF) The SNMP driver depends on an old, out of maintenance library
    #   pysnmp-lextudio; unless it is migrated to a modern library (pysnmp),
    #   it will be removed in a future Ironic release. See bug #2106674.
    # TODO(JayF) Remove this driver on or after OpenStack 2026.1 release.
    supported = False

    @property
    def supported_power_interfaces(self):
        """List of supported power interfaces."""
        return [snmp.SNMPPower]

    @property
    def supported_management_interfaces(self):
        """List of supported management interfaces."""
        return [noop_mgmt.NoopManagement, fake.FakeManagement]
