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

"""This package contains the rounds of VotingAbciApp."""

from enum import Enum
from typing import Dict, FrozenSet, Optional, Set, Tuple

from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AppState,
    BaseSynchronizedData,
    CollectSameUntilThresholdRound,
    CollectionRound,
    DegenerateRound,
    DeserializedCollection,
    EventToTimeout,
    get_name,
)
from packages.valory.skills.learning_abci.payloads import (
    APICheckPayload,
    DecisionMakingPayload,
    TxPreparationPayload,
    IPFSPayload,
    MultisendTxPayload,
    CustomContractPayload,
)


class Event(Enum):
    """VotingAbciApp Events"""

    DONE = "done"
    ERROR = "error"
    TRANSACT = "transact"
    NO_MAJORITY = "no_majority"
    ROUND_TIMEOUT = "round_timeout"
    IPFS_STORED = "ipfs_stored"
    IPFS_RETRIEVED = "ipfs_retrieved"
    MULTISEND_DONE = "multisend_done"
    CONTRACT_INTERACTED = "contract_interacted"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """

    def _get_deserialized(self, key: str) -> DeserializedCollection:
        """Strictly get a collection and return it deserialized."""
        serialized = self.db.get_strict(key)
        return CollectionRound.deserialize_collection(serialized)

    @property
    def price(self) -> Optional[float]:
        """Get the token price."""
        return self.db.get("price", None)

    @property
    def participant_to_price_round(self) -> DeserializedCollection:
        """Get the participants to the price round."""
        return self._get_deserialized("participant_to_price_round")

    @property
    def most_voted_tx_hash(self) -> Optional[str]:
        """Get the token most_voted_tx_hash."""
        return self.db.get("most_voted_tx_hash", None)

    @property
    def participant_to_tx_round(self) -> DeserializedCollection:
        """Get the participants to the tx round."""
        return self._get_deserialized("participant_to_tx_round")

    @property
    def tx_submitter(self) -> str:
        """Get the round that submitted a tx to transaction_settlement_abci."""
        return str(self.db.get_strict("tx_submitter"))

    @property
    def ipfs_hash(self) -> Optional[str]:
        """Get the IPFS hash."""
        return self.db.get("ipfs_hash", None)

    @property
    def multisend_tx_hash(self) -> Optional[str]:
        """Get the multisend transaction hash."""
        return self.db.get("multisend_tx_hash", None)

    @property
    def contract_interaction_result(self) -> Optional[str]:
        """Get the contract interaction result."""
        return self.db.get("contract_interaction_result", None)


class APICheckRound(CollectSameUntilThresholdRound):
    """APICheckRound"""

    payload_class = APICheckPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.DONE
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.participant_to_price_round)
    selection_key = get_name(SynchronizedData.price)

    # Event.ROUND_TIMEOUT  # this needs to be referenced for static checkers


class DecisionMakingRound(CollectSameUntilThresholdRound):
    """DecisionMakingRound"""

    payload_class = DecisionMakingPayload
    synchronized_data_class = SynchronizedData

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""

        if self.threshold_reached:
            event = Event(self.most_voted_payload)
            return self.synchronized_data, event

        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY

        return None

    # Event.DONE, Event.ERROR, Event.TRANSACT, Event.ROUND_TIMEOUT  # this needs to be referenced for static checkers


class TxPreparationRound(CollectSameUntilThresholdRound):
    """TxPreparationRound"""

    payload_class = TxPreparationPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.DONE
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.participant_to_tx_round)
    selection_key = (
        get_name(SynchronizedData.tx_submitter),
        get_name(SynchronizedData.most_voted_tx_hash),
    )

    # Event.ROUND_TIMEOUT  # this needs to be referenced for static checkers


class IPFSStoreRound(CollectSameUntilThresholdRound):
    """Round to store data in IPFS"""

    payload_class = IPFSPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.IPFS_STORED
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.ipfs_hash)

    # Event.ROUND_TIMEOUT  # this needs to be referenced for static checkers


class IPFSRetrieveRound(CollectSameUntilThresholdRound):
    """Round to retrieve data from IPFS"""

    payload_class = IPFSPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.IPFS_RETRIEVED
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.ipfs_hash)

    # Event.ROUND_TIMEOUT  # this needs to be referenced for static checkers


class MultisendTxRound(CollectSameUntilThresholdRound):
    """Round for preparing and executing multisend transactions"""

    payload_class = MultisendTxPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.MULTISEND_DONE
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.multisend_tx_hash)

    # Event.ROUND_TIMEOUT  # this needs to be referenced for static checkers


class CustomContractRound(CollectSameUntilThresholdRound):
    """Round for interacting with a custom contract"""

    payload_class = CustomContractPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.CONTRACT_INTERACTED
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.contract_interaction_result)

    # Event.ROUND_TIMEOUT  # this needs to be referenced for static checkers


class FinishedDecisionMakingRound(DegenerateRound):
    """FinishedDecisionMakingRound"""


class FinishedTxPreparationRound(DegenerateRound):
    """FinishedTxPreparationRound"""


class FinishedIPFSRound(DegenerateRound):
    """FinishedIPFSRound"""


class FinishedMultisendRound(DegenerateRound):
    """FinishedMultisendRound"""


class FinishedContractInteractionRound(DegenerateRound):
    """FinishedContractInteractionRound"""


class VotingAbciApp(AbciApp[Event]):
    """VotingAbciApp"""

    initial_round_cls: AppState = APICheckRound
    initial_states: Set[AppState] = {
        APICheckRound,
    }
    transition_function: AbciAppTransitionFunction = {
        APICheckRound: {
            Event.NO_MAJORITY: APICheckRound,
            Event.ROUND_TIMEOUT: APICheckRound,
            Event.DONE: DecisionMakingRound,
        },
        DecisionMakingRound: {
            Event.NO_MAJORITY: DecisionMakingRound,
            Event.ROUND_TIMEOUT: DecisionMakingRound,
            Event.DONE: FinishedDecisionMakingRound,
            Event.ERROR: FinishedDecisionMakingRound,
            Event.TRANSACT: TxPreparationRound,
            Event.IPFS_STORED: IPFSRetrieveRound,
            Event.MULTISEND_DONE: MultisendTxRound,
            Event.CONTRACT_INTERACTED: CustomContractRound,
        },
        TxPreparationRound: {
            Event.NO_MAJORITY: TxPreparationRound,
            Event.ROUND_TIMEOUT: TxPreparationRound,
            Event.DONE: FinishedTxPreparationRound,
        },
        IPFSStoreRound: {
            Event.NO_MAJORITY: IPFSStoreRound,
            Event.ROUND_TIMEOUT: IPFSStoreRound,
            Event.IPFS_STORED: FinishedIPFSRound,
        },
        IPFSRetrieveRound: {
            Event.NO_MAJORITY: IPFSRetrieveRound,
            Event.ROUND_TIMEOUT: IPFSRetrieveRound,
            Event.IPFS_RETRIEVED: FinishedIPFSRound,
        },
        MultisendTxRound: {
            Event.NO_MAJORITY: MultisendTxRound,
            Event.ROUND_TIMEOUT: MultisendTxRound,
            Event.MULTISEND_DONE: FinishedMultisendRound,
        },
        CustomContractRound: {
            Event.NO_MAJORITY: CustomContractRound,
            Event.ROUND_TIMEOUT: CustomContractRound,
            Event.CONTRACT_INTERACTED: FinishedContractInteractionRound,
        },
        FinishedDecisionMakingRound: {},
        FinishedTxPreparationRound: {},
        FinishedIPFSRound: {},
        FinishedMultisendRound: {},
        FinishedContractInteractionRound: {},
    }
    final_states: Set[AppState] = {
        FinishedDecisionMakingRound,
        FinishedTxPreparationRound,
        FinishedIPFSRound,
        FinishedMultisendRound,
        FinishedContractInteractionRound,
    }
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: FrozenSet[str] = frozenset()
    db_pre_conditions: Dict[AppState, Set[str]] = {
        APICheckRound: set(),
    }
    db_post_conditions: Dict[AppState, Set[str]] = {
        FinishedDecisionMakingRound: set(),
        FinishedTxPreparationRound: {get_name(SynchronizedData.most_voted_tx_hash)},
        FinishedIPFSRound: {get_name(SynchronizedData.ipfs_hash)},
        FinishedMultisendRound: {get_name(SynchronizedData.multisend_tx_hash)},
        FinishedContractInteractionRound: {get_name(SynchronizedData.contract_interaction_result)},
    }
