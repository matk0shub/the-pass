from __future__ import annotations

import copy
import unittest
from pathlib import Path

from the_pass.roadmap import RoadmapValidationError, load_roadmap, validate_roadmap_document


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "implementation" / "roadmap-status.yaml"


class RoadmapMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = load_roadmap(STATUS)

    def milestone(self, document: dict, milestone_id: str) -> dict:
        return next(item for item in document["milestones"] if item["id"] == milestone_id)

    def test_tracked_roadmap_is_valid(self) -> None:
        validate_roadmap_document(self.document, root=ROOT)

    def test_p4_capability_cannot_omit_candidate_state(self) -> None:
        document = copy.deepcopy(self.document)
        self.milestone(document, "P4").pop("candidate_gate_state")
        with self.assertRaisesRegex(RoadmapValidationError, "candidate gate must remain blocked"):
            validate_roadmap_document(document, root=ROOT)

    def test_p4_capability_cannot_claim_candidate_pass(self) -> None:
        document = copy.deepcopy(self.document)
        self.milestone(document, "P4")["candidate_gate_state"] = "pass"
        with self.assertRaisesRegex(RoadmapValidationError, "records disagree|must remain blocked"):
            validate_roadmap_document(document, root=ROOT)

    def test_locked_boundary_cannot_claim_live_candidate_pass(self) -> None:
        document = copy.deepcopy(self.document)
        self.milestone(document, "L5_L6")["candidate_gate_state"] = "pass"
        with self.assertRaisesRegex(RoadmapValidationError, "records disagree|must remain blocked"):
            validate_roadmap_document(document, root=ROOT)


if __name__ == "__main__":
    unittest.main()
