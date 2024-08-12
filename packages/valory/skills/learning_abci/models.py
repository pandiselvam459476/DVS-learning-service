# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the shared state for the abci skill of VotingAbciApp."""

from typing import Any

from packages.valory.skills.abstract_round_abci.models import BaseParams
from packages.valory.skills.abstract_round_abci.models import (
    BenchmarkTool as BaseBenchmarkTool,
)
from packages.valory.skills.abstract_round_abci.models import Requests as BaseRequests
from packages.valory.skills.abstract_round_abci.models import (
    SharedState as BaseSharedState,
)
from packages.valory.skills.learning_abci.rounds import VotingAbciApp


class SharedState(BaseSharedState):
    """Keep the current shared state of the skill."""

    abci_app_cls = VotingAbciApp


Requests = BaseRequests
BenchmarkTool = BaseBenchmarkTool


class Params(BaseParams):
    """Parameters."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the parameters object."""
        self.coingecko_price_template = self._ensure(
            "coingecko_price_template", kwargs, str
        )
        self.coingecko_api_key = kwargs.get("coingecko_api_key", None)
        self.transfer_target_address = self._ensure(
            "transfer_target_address", kwargs, str
        )

        # New parameters for IPFS storage
        self.ipfs_api_endpoint = self._ensure("ipfs_api_endpoint", kwargs, str)
        self.ipfs_timeout = self._ensure("ipfs_timeout", kwargs, int, default=60)

        # New parameters for Multisend transactions
        self.multisend_contract_address = self._ensure(
            "multisend_contract_address", kwargs, str
        )
        self.multisend_gas_limit = self._ensure(
            "multisend_gas_limit", kwargs, int, default=300000
        )

        # Custom contract parameters (if needed)
        self.custom_contract_address = kwargs.get("custom_contract_address", None)

        super().__init__(*args, **kwargs)
