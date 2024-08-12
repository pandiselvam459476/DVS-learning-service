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

"""This module contains the transaction payloads of the VotingAbciApp."""

from dataclasses import dataclass
from typing import Optional

from packages.valory.skills.abstract_round_abci.base import BaseTxPayload


@dataclass(frozen=True)
class APICheckPayload(BaseTxPayload):
    """Represent a transaction payload for the APICheckRound."""

    price: Optional[float]


@dataclass(frozen=True)
class DecisionMakingPayload(BaseTxPayload):
    """Represent a transaction payload for the DecisionMakingRound."""

    event: str


@dataclass(frozen=True)
class TxPreparationPayload(BaseTxPayload):
    """Represent a transaction payload for the TxPreparationRound."""

    tx_submitter: Optional[str] = None
    tx_hash: Optional[str] = None


@dataclass(frozen=True)
class IPFSPayload(BaseTxPayload):
    """Represent a transaction payload for storing/retrieving data from IPFS."""

    ipfs_hash: Optional[str] = None
    data: Optional[str] = None


@dataclass(frozen=True)
class MultisendTxPayload(BaseTxPayload):
    """Represent a transaction payload for preparing a multisend transaction."""

    tx_submitter: Optional[str] = None
    multisend_tx_hash: Optional[str] = None
    transactions: Optional[str] = None  # JSON string or similar representation of the transactions


@dataclass(frozen=True)
class CustomContractPayload(BaseTxPayload):
    """Represent a transaction payload for interacting with a custom contract."""

    contract_address: str
    function_name: str
    function_args: str  # Arguments can be serialized to a string or use a more appropriate data structure
