# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Tests for manipulating Ports via the DB API"""

from oslo_utils import uuidutils

from ironic.common import exception
from ironic.tests.unit.db import base
from ironic.tests.unit.db import utils as db_utils


def _create_test_port_with_shard(shard, address):
    node = db_utils.create_test_node(
        uuid=uuidutils.generate_uuid(),
        owner='12345', lessee='54321', shard=shard)
    pg = db_utils.create_test_portgroup(
        name='pg-%s' % shard,
        uuid=uuidutils.generate_uuid(),
        node_id=node.id,
        address=address)
    return db_utils.create_test_port(
        name='port-%s' % shard,
        uuid=uuidutils.generate_uuid(),
        node_id=node.id,
        address=address,
        portgroup_id=pg.id)


class DbPortTestCase(base.DbTestCase):

    def setUp(self):
        # This method creates a port for every test and
        # replaces a test for creating a port.
        super(DbPortTestCase, self).setUp()
        self.node = db_utils.create_test_node(owner='12345',
                                              lessee='54321')
        self.portgroup = db_utils.create_test_portgroup(node_id=self.node.id)
        self.port = db_utils.create_test_port(node_id=self.node.id,
                                              portgroup_id=self.portgroup.id,
                                              name='port-name')

    def test_get_port_by_id(self):
        res = self.dbapi.get_port_by_id(self.port.id)
        self.assertEqual(self.port.address, res.address)

    def test_get_port_by_uuid(self):
        res = self.dbapi.get_port_by_uuid(self.port.uuid)
        self.assertEqual(self.port.id, res.id)

    def test_get_port_by_address(self):
        res = self.dbapi.get_port_by_address(self.port.address)
        self.assertEqual(self.port.id, res.id)

    def test_get_port_by_address_filter_by_owner(self):
        res = self.dbapi.get_port_by_address(self.port.address,
                                             owner=self.node.owner)
        self.assertEqual(self.port.id, res.id)

    def test_get_port_by_address_filter_by_owner_no_match(self):
        self.assertRaises(exception.PortNotFound,
                          self.dbapi.get_port_by_address,
                          self.port.address,
                          owner='54321')

    def test_get_port_by_address_filter_by_project(self):
        res = self.dbapi.get_port_by_address(self.port.address,
                                             project=self.node.lessee)
        self.assertEqual(self.port.id, res.id)

    def test_get_port_by_address_filter_by_project_no_match(self):
        self.assertRaises(exception.PortNotFound,
                          self.dbapi.get_port_by_address,
                          self.port.address,
                          project='55555')

    def test_get_port_by_name(self):
        res = self.dbapi.get_port_by_name(self.port.name)
        self.assertEqual(self.port.id, res.id)

    def test_get_port_list(self):
        uuids = []
        for i in range(1, 6):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=self.node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
            uuids.append(str(port.uuid))
        # Also add the uuid for the port created in setUp()
        uuids.append(str(self.port.uuid))
        res = self.dbapi.get_port_list()
        res_uuids = [r.uuid for r in res]
        self.assertCountEqual(uuids, res_uuids)

    def test_get_port_list_sorted(self):
        uuids = []
        for i in range(1, 6):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=self.node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
            uuids.append(str(port.uuid))
        # Also add the uuid for the port created in setUp()
        uuids.append(str(self.port.uuid))
        res = self.dbapi.get_port_list(sort_key='uuid')
        res_uuids = [r.uuid for r in res]
        self.assertEqual(sorted(uuids), res_uuids)

        self.assertRaises(exception.InvalidParameterValue,
                          self.dbapi.get_port_list, sort_key='foo')

    def test_get_port_list_filter_by_node_owner(self):
        another_node = db_utils.create_test_node(
            uuid=uuidutils.generate_uuid())
        uuids = []
        for i in range(1, 3):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=another_node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
        for i in range(4, 6):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=self.node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
            uuids.append(str(port.uuid))
        # Also add the uuid for the port created in setUp()
        uuids.append(str(self.port.uuid))
        res = self.dbapi.get_port_list(owner=self.node.owner)
        res_uuids = [r.uuid for r in res]
        self.assertCountEqual(uuids, res_uuids)

    def test_get_port_list_filter_by_node_project(self):
        another_node = db_utils.create_test_node(
            uuid=uuidutils.generate_uuid())
        lessee_node = db_utils.create_test_node(uuid=uuidutils.generate_uuid(),
                                                lessee=self.node.owner)

        uuids = []
        for i in range(1, 3):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=lessee_node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
            uuids.append(str(port.uuid))
        for i in range(4, 6):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=another_node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
        for i in range(7, 9):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=self.node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
            uuids.append(str(port.uuid))
        # Also add the uuid for the port created in setUp()
        uuids.append(str(self.port.uuid))
        res = self.dbapi.get_port_list(project=self.node.owner)
        res_uuids = [r.uuid for r in res]
        self.assertCountEqual(uuids, res_uuids)

    def test_get_port_list_filter_by_conductor_groups(self):
        group_a_node = db_utils.create_test_node(
            uuid=uuidutils.generate_uuid(), conductor_group='group_a')
        group_b_node = db_utils.create_test_node(
            uuid=uuidutils.generate_uuid(), conductor_group='group_b')

        group_a_uuids = []
        group_b_uuids = []
        for i in range(1, 3):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=group_a_node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
            group_a_uuids.append(str(port.uuid))
        for i in range(7, 9):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=group_b_node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
            group_b_uuids.append(str(port.uuid))
        for i in range(4, 6):
            port = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                             node_id=self.node.id,
                                             address='52:54:00:cf:2d:4%s' % i)
        res = self.dbapi.get_port_list(conductor_groups=['group_a'])
        res_uuids = [r.uuid for r in res]
        self.assertJsonEqual(group_a_uuids, res_uuids)
        res = self.dbapi.get_port_list(conductor_groups=['group_b'])
        res_uuids = [r.uuid for r in res]
        self.assertJsonEqual(group_b_uuids, res_uuids)
        res = self.dbapi.get_port_list(
            conductor_groups=['group_a', 'group_b'])
        res_uuids = [r.uuid for r in res]
        self.assertJsonEqual(group_a_uuids + group_b_uuids, res_uuids)

    def test_get_ports_by_node_id(self):
        res = self.dbapi.get_ports_by_node_id(self.node.id)
        self.assertEqual(self.port.address, res[0].address)

    def test_get_ports_by_node_id_filter_by_node_owner(self):
        res = self.dbapi.get_ports_by_node_id(self.node.id,
                                              owner=self.node.owner)
        self.assertEqual(self.port.address, res[0].address)

    def test_get_ports_by_node_id_filter_by_node_owner_no_match(self):
        res = self.dbapi.get_ports_by_node_id(self.node.id,
                                              owner='54321')
        self.assertEqual([], res)

    def test_get_ports_by_node_id_filter_by_node_project(self):
        res = self.dbapi.get_ports_by_node_id(self.node.id,
                                              project=self.node.lessee)
        self.assertEqual(self.port.address, res[0].address)

    def test_get_ports_by_node_id_filter_by_node_project_no_match(self):
        res = self.dbapi.get_ports_by_node_id(self.node.id,
                                              owner='11111')
        self.assertEqual([], res)

    def test_get_ports_by_node_id_that_does_not_exist(self):
        self.assertEqual([], self.dbapi.get_ports_by_node_id(99))

    def test_get_ports_by_portgroup_id(self):
        res = self.dbapi.get_ports_by_portgroup_id(self.portgroup.id)
        self.assertEqual(self.port.address, res[0].address)

    def test_get_ports_by_portgroup_id_filter_by_node_owner(self):
        res = self.dbapi.get_ports_by_portgroup_id(self.portgroup.id,
                                                   owner=self.node.owner)
        self.assertEqual(self.port.address, res[0].address)

    def test_get_ports_by_portgroup_id_filter_by_node_owner_no_match(self):
        res = self.dbapi.get_ports_by_portgroup_id(self.portgroup.id,
                                                   owner='54321')
        self.assertEqual([], res)

    def test_get_ports_by_portgroup_id_filter_by_node_project(self):
        res = self.dbapi.get_ports_by_portgroup_id(self.portgroup.id,
                                                   project=self.node.lessee)
        self.assertEqual(self.port.address, res[0].address)

    def test_get_ports_by_portgroup_id_filter_by_node_project_no_match(self):
        res = self.dbapi.get_ports_by_portgroup_id(self.portgroup.id,
                                                   project='11111')
        self.assertEqual([], res)

    def test_get_ports_by_portgroup_id_that_does_not_exist(self):
        self.assertEqual([], self.dbapi.get_ports_by_portgroup_id(99))

    def test_get_ports_by_shard_no_match(self):
        res = self.dbapi.get_ports_by_shards(['shard1', 'shard2'])
        self.assertEqual([], res)

    def test_get_ports_by_shard_with_match_single(self):
        _create_test_port_with_shard('shard1', 'aa:bb:cc:dd:ee:ff')

        res = self.dbapi.get_ports_by_shards(['shard1'])
        self.assertEqual(1, len(res))
        self.assertEqual('port-shard1', res[0].name)

    def test_get_ports_by_shard_with_match_multi(self):
        _create_test_port_with_shard('shard1', 'aa:bb:cc:dd:ee:ff')
        _create_test_port_with_shard('shard2', 'ab:bb:cc:dd:ee:ff')
        _create_test_port_with_shard('shard3', 'ac:bb:cc:dd:ee:ff')

        res = self.dbapi.get_ports_by_shards(['shard1', 'shard2'])
        self.assertEqual(2, len(res))
        # note(JayF): We do not query for shard3; ensure we don't get it.
        self.assertNotEqual('port-shard3', res[0].name)
        self.assertNotEqual('port-shard3', res[1].name)

    def test_destroy_port(self):
        self.dbapi.destroy_port(self.port.id)
        self.assertRaises(exception.PortNotFound,
                          self.dbapi.destroy_port, self.port.id)

    def test_update_port(self):
        old_address = self.port.address
        new_address = 'ff.ee.dd.cc.bb.aa'

        self.assertNotEqual(old_address, new_address)

        res = self.dbapi.update_port(self.port.id, {'address': new_address})
        self.assertEqual(new_address, res.address)

    def test_update_port_uuid(self):
        self.assertRaises(exception.InvalidParameterValue,
                          self.dbapi.update_port, self.port.id,
                          {'uuid': ''})

    def test_update_port_duplicated_address(self):
        address1 = self.port.address
        address2 = 'aa-bb-cc-11-22-33'
        port2 = db_utils.create_test_port(uuid=uuidutils.generate_uuid(),
                                          node_id=self.node.id,
                                          address=address2)
        self.assertRaises(exception.MACAlreadyExists,
                          self.dbapi.update_port, port2.id,
                          {'address': address1})

    def test_create_port_duplicated_address(self):
        self.assertRaises(exception.MACAlreadyExists,
                          db_utils.create_test_port,
                          uuid=uuidutils.generate_uuid(),
                          node_id=self.node.id,
                          address=self.port.address)

    def test_create_port_duplicated_uuid(self):
        self.assertRaises(exception.PortAlreadyExists,
                          db_utils.create_test_port,
                          uuid=self.port.uuid,
                          node_id=self.node.id,
                          address='aa-bb-cc-33-11-22')

    def test_create_port_with_description(self):
        description = 'Management Port'
        port1 = db_utils.create_test_port(
            uuid=uuidutils.generate_uuid(),
            node_id=self.node.id,
            address='52:54:00:cf:2d:42',
            description=description)

        port2 = db_utils.create_test_port(
            uuid=uuidutils.generate_uuid(),
            node_id=self.node.id,
            address='52:54:00:cf:2d:45',
            description=description)

        self.assertEqual(description, port1.description)
        self.assertEqual(description, port2.description)

        new_description = 'Updated Description'
        updated_port = self.dbapi.update_port(
            port1.id, {'description': new_description})

        self.assertEqual(new_description, updated_port.description)

        retrieved_port1 = self.dbapi.get_port_by_uuid(port1.uuid)
        self.assertEqual(new_description, retrieved_port1.description)
