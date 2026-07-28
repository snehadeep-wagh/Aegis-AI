import json

from agents.classifier_agents.classifier_agent import ClassifierAgent
from agents.extractor_agents.extractor_agents import ExtractorAgent
from agents.risk_agents.risk_agent import RiskAgent
from agents.loan_agents.loan_agent import LoanAgent


class MasterAgent:

    def __init__(self):
        self.classifier = ClassifierAgent()
        self.extractor = ExtractorAgent()
        self.risk = RiskAgent()
        self.loan = LoanAgent()

    def process(self, documents):
        """
        Orchestrates all agents.

        Args:
            documents:
                {
                    "aadhaar": Part(...),
                    "pan": Part(...),
                    "passport": Part(...),
                    ...
                }

        Returns:
            {
                "documents": {...},
                "loan_decision": LoanDecisionResponse(...)
            }
        """

        # Step 1: Classify all documents
        print("Classification in progress.....")
        document_types = self.classifier.classify(documents)

        # Step 2: Extract structured data
        print("Extraction in progress.....")
        extracted_data = self.extractor.extract(documents)

        # Step 3: Verify document authenticity
        print("Risk verification in progress.....")
        risk_results = self.risk.evaluate(documents)

        # Step 4: Combine results from all agents
        combined_results = {}

        for document_name in documents.keys():
            combined_results[document_name] = {
                "document_type": document_types.get(document_name),
                "data": extracted_data.get(document_name),
                "risk": risk_results.get(document_name),
            }

        # Step 5: Convert Pydantic models to JSON
        print("Overall verification in progress.....")
        combined_json = json.dumps(
            combined_results,
            default=lambda obj: obj.model_dump() if hasattr(obj, "model_dump") else str(obj),
            indent=2,
        )

        # Step 6: Get overall loan decision
        loan_decision = self.loan.evaluate(combined_json)

        # Step 7: Return complete response
        final_res = {
            "documents": combined_results,
            "loan_decision": loan_decision,
        }

        print("Result:\n" + str(final_res))

        return final_res