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

import ddt
import mock

from rally.plugins.openstack.scenarios.neutron import bgpvpn
from tests.unit import test


@ddt.ddt
class NeutronBgpvpnTestCase(test.TestCase):

    def _get_context(self):
        context = test.get_test_context()
        return context

    def _get_bgpvpn_create_data(self):
        return {
            "route_targets": None,
            "import_targets": None,
            "export_targets": None,
            "route_distinguishers": None}

    def _get_bgpvpn_update_data(self):
        return {
            "route_targets": None,
            "import_targets": None,
            "export_targets": None,
            "route_distinguishers": None}

    @ddt.data(
        {},
        {"bgpvpn_create_args": None},
        {"bgpvpn_create_args": {}},
    )
    @ddt.unpack
    def test_create_and_delete_bgpvpns(self, bgpvpn_create_args=None):
        scenario = bgpvpn.CreateAndDeleteBgpvpns(self._get_context())
        bgpvpn_create_data = bgpvpn_create_args or {}
        create_data = self._get_bgpvpn_create_data()
        create_data.update(bgpvpn_create_data)
        scenario._create_bgpvpn = mock.Mock()
        scenario._delete_bgpvpn = mock.Mock()
        scenario.run(**create_data)
        scenario._create_bgpvpn.assert_called_once_with(
            type="l3", **create_data)
        scenario._delete_bgpvpn.assert_called_once_with(
            scenario._create_bgpvpn.return_value)

    @ddt.data(
        {},
        {"bgpvpn_create_args": None},
        {"bgpvpn_create_args": {}},
    )
    @ddt.unpack
    def test_create_and_list_bgpvpns(self, bgpvpn_create_args=None):
        scenario = bgpvpn.CreateAndListBgpvpns(self._get_context())
        bgpvpn_create_data = bgpvpn_create_args or {}
        create_data = self._get_bgpvpn_create_data()
        create_data.update(bgpvpn_create_data)
        bgpvpn_created = {"bgpvpn": {"id": 1, "name": "b1"}}
        bgpvpn_listed = [{"id": 1}]
        scenario._create_bgpvpn = mock.Mock(return_value=bgpvpn_created)
        scenario._list_bgpvpns = mock.Mock(return_value=bgpvpn_listed)
        scenario.run(**create_data)
        scenario._create_bgpvpn.assert_called_once_with(
            type="l3", **create_data)
        scenario._list_bgpvpns.assert_called_once_with()

    @ddt.data(
        {},
        {"bgpvpn_create_args": {}},
        {"bgpvpn_update_args": {}},
        {"bgpvpn_update_args": {"update_name": True}},
        {"bgpvpn_update_args": {"update_name": False}},
    )
    @ddt.unpack
    def test_create_and_update_bgpvpns(self, bgpvpn_create_args=None,
                                       bgpvpn_update_args=None):
        scenario = bgpvpn.CreateAndUpdateBgpvpns(self._get_context())
        bgpvpn_create_data = bgpvpn_create_args or {}
        bgpvpn_update_data = bgpvpn_update_args or {}
        create_data = self._get_bgpvpn_create_data()
        create_data.update(bgpvpn_create_data)
        update_data = self._get_bgpvpn_update_data()
        update_data.update(bgpvpn_update_data)
        if "update_name" not in update_data:
            update_data["update_name"] = False
        bgpvpn_data = {}
        bgpvpn_data.update(bgpvpn_create_data)
        bgpvpn_data.update(bgpvpn_update_data)
        scenario._create_bgpvpn = mock.Mock()
        scenario._update_bgpvpn = mock.Mock()
        scenario.run(**bgpvpn_data)
        scenario._create_bgpvpn.assert_called_once_with(
            type="l3", **create_data)
        scenario._update_bgpvpn.assert_called_once_with(
            scenario._create_bgpvpn.return_value, **update_data)

    @ddt.data(
        {"list_networks": []},
        {"list_networks": [{"tenant_id": "tenant_id", "id": "network_id"}]},
    )
    @ddt.unpack
    def test_create_and_associate_disassociate_networks(self,
                                                        list_networks=None):
        scenario = bgpvpn.CreateAndAssociateDissassociateNetworks(
            self._get_context())
        create_data = self._get_bgpvpn_create_data()
        create_data["tenant_id"] = "tenant_id"
        network = {"network": {"tenant_id": "tenant_id",
                               "id": "network_id"}}
        scenario.context = {"user": {"tenant_id": "tenant_id"}}
        scenario._list_networks = mock.Mock(return_value=list_networks)
        if not list_networks:
            scenario._create_network = mock.Mock(return_value=network)
        scenario._create_bgpvpn = mock.Mock()
        scenario._create_bgpvpn_network_assoc = mock.Mock()
        scenario._delete_bgpvpn_network_assoc = mock.Mock()
        scenario.run()
        scenario._create_bgpvpn.assert_called_once_with(
            type="l3", **create_data)
        if list_networks:
            given_network = {"network": {"tenant_id": "tenant_id",
                                         "id": "network_id"}}
        else:
            scenario._create_network.assert_called_once_with({})
            given_network = scenario._create_network.return_value

        scenario._create_bgpvpn_network_assoc.assert_called_once_with(
            scenario._create_bgpvpn.return_value, given_network)
        scenario._delete_bgpvpn_network_assoc.assert_called_once_with(
            scenario._create_bgpvpn.return_value,
            scenario._create_bgpvpn_network_assoc.return_value)

    @ddt.data(
        {"list_routers": []},
        {"list_routers": [{"tenant_id": "tenant_id", "id": "router_id"}]},
    )
    @ddt.unpack
    def test_create_and_associate_disassociate_routers(self,
                                                       list_routers=None):
        scenario = bgpvpn.CreateAndAssociateDissassociateRouters(
            self._get_context())
        create_data = self._get_bgpvpn_create_data()
        create_data["tenant_id"] = "tenant_id"
        router = {"router": {"tenant_id": "tenant_id",
                             "id": "router_id"}}
        scenario._list_routers = mock.Mock(return_value=list_routers)
        if not list_routers:
            scenario._create_router = mock.Mock(return_value=router)
        scenario._create_bgpvpn = mock.Mock()
        scenario._create_bgpvpn_router_assoc = mock.Mock()
        scenario._delete_bgpvpn_router_assoc = mock.Mock()
        scenario.run()
        scenario._create_bgpvpn.assert_called_once_with(
            type="l3", **create_data)
        if list_routers:
            given_router = {"router": {"tenant_id": "tenant_id",
                                       "id": "router_id"}}
        else:
            scenario._create_router.assert_called_once_with({})
            given_router = scenario._create_router.return_value

        scenario._create_bgpvpn_router_assoc.assert_called_once_with(
            scenario._create_bgpvpn.return_value, given_router)
        scenario._delete_bgpvpn_router_assoc.assert_called_once_with(
            scenario._create_bgpvpn.return_value,
            scenario._create_bgpvpn_router_assoc.return_value)
