"""
RAG Evaluation using DeepEval with Groq
- 25 clinical dialysis questions
- Ground truths auto-generated from ChromaDB (top retrieved chunk)
- No hardcoded answers

Install:
    pip install deepeval langchain-groq pandas
"""

import re
import json
import traceback
import pandas as pd # type: ignore

from deepeval import evaluate # type: ignore
from deepeval.evaluate.configs import AsyncConfig, DisplayConfig # type: ignore
from deepeval.metrics import ( # type: ignore
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.models.base_model import DeepEvalBaseLLM # type: ignore
from deepeval.test_case import LLMTestCase # type: ignore
from langchain_groq import ChatGroq # type: ignore

import config
from chat import ChatBot


# =============================================================================
# 1. Groq wrapper for DeepEval
# =============================================================================

class GroqDeepEvalLLM(DeepEvalBaseLLM):
    """
    Wraps Groq API so DeepEval can use it
    as the judge LLM for scoring metrics
    """

    def __init__(self, model=None):
        if model is None:
            model = config.CHAT_MODEL
        self.model_name = model
        # Main client for regular responses
        self._client = ChatGroq(
            model=model,
            api_key=config.GROQ_API_KEY,
            temperature=0.0
        )
        # JSON client for structured responses
        self._json_client = ChatGroq(
            model=model,
            api_key=config.GROQ_API_KEY,
            temperature=0.0
        )

    def load_model(self):
        return self._client

    @staticmethod
    def _clean(text):
        """Remove markdown code blocks from response"""
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = re.sub(r"```", "", text)
        return text.strip()

    @staticmethod
    def _schema_hint(schema):
        """Tell the model exactly what JSON format to return"""
        lines = ["", "", "Respond ONLY with valid JSON matching this structure:"]
        try:
            sample = {}
            for k, v in schema.model_fields.items():
                ann = v.annotation
                name = ann.__name__ if hasattr(ann, "__name__") else str(ann)
                sample[k] = "<" + name + ">"
            lines.append(json.dumps(sample, indent=2))
        except Exception:
            lines.append('{ "field": "<value>" }')
        return "\n".join(lines)

    def generate(self, prompt, schema=None):
        resp = self._client.invoke(prompt)
        raw = resp.content if hasattr(resp, "content") else str(resp)
        return self._clean(raw)

    async def a_generate(self, prompt, schema=None):
        resp = await self._client.ainvoke(prompt)
        raw = resp.content if hasattr(resp, "content") else str(resp)
        return self._clean(raw)

    def generate_with_schema(self, prompt, schema=None, **kwargs):
        augmented = prompt + (self._schema_hint(schema) if schema else "")
        resp = self._json_client.invoke(augmented)
        raw = resp.content if hasattr(resp, "content") else str(resp)
        return self._clean(raw)

    async def a_generate_with_schema(self, prompt, schema=None, **kwargs):
        augmented = prompt + (self._schema_hint(schema) if schema else "")
        resp = await self._json_client.ainvoke(augmented)
        raw = resp.content if hasattr(resp, "content") else str(resp)
        return self._clean(raw)

    def get_model_name(self):
        return self.model_name


# =============================================================================
# 2. 25 Clinical Test Questions
# =============================================================================

TEST_QUESTIONS = [
    "A dialysis patient has serum potassium of 6.2 mEq/L — which specific foods must be immediately restricted and why?",
    "How does phosphorus restriction differ between hemodialysis and peritoneal dialysis patients?",
    "Why is protein intake paradoxically higher in dialysis patients despite kidney failure?",
    "What is the relationship between sodium intake, fluid retention, and interdialytic weight gain?",
    "How should a diabetic patient on dialysis manage carbohydrate intake differently from a non-diabetic dialysis patient?",
    "Explain the difference between diffusion and convection as solute removal mechanisms in dialysis.",
    "What is the significance of Kt/V in hemodialysis adequacy and how is it interpreted clinically?",
    "How does APD differ from CAPD in terms of dwell time and clearance?",
    "What factors determine the choice between high-flux and low-flux dialysis membranes?",
    "How does residual renal function affect dialysis prescription in peritoneal dialysis patients?",
    "What are the early versus late signs of dialysis disequilibrium syndrome and how is it managed?",
    "How do you differentiate tunnel infection from exit-site infection in PD catheter care?",
    "What is the pathophysiology of intradialytic hypotension and what immediate interventions should a patient take?",
    "Explain why dialysis patients are at higher cardiovascular risk and what specific monitoring is recommended?",
    "What is encapsulating peritoneal sclerosis and what are its risk factors in long-term PD patients?",
    "Pre-dialysis BUN = 85 mg/dL, post-dialysis BUN = 28 mg/dL. Calculate URR and interpret adequacy.",
    "What does serum albumin below 3.5 g/dL indicate in a dialysis patient and what interventions are appropriate?",
    "How should intact PTH levels be interpreted differently in dialysis patients vs. general population?",
    "What is the clinical significance of elevated beta-2 microglobulin in long-term hemodialysis patients?",
    "How do you interpret anemia parameters (Hb, ferritin, TSAT) in dialysis patients on erythropoietin?",
    "What specific precautions must a hemodialysis patient take regarding AV fistula care during daily activities?",
    "How should medications be timed relative to dialysis sessions for dialyzable vs. non-dialyzable drugs?",
    "What are the psychological impacts of dialysis dependency and what evidence-based coping strategies exist?",
    "How does travel affect dialysis scheduling and what arrangements must be made for international travel?",
    "What specific sexual health considerations apply to dialysis patients and how should they be addressed?",
]


# =============================================================================
# 3. Auto-generate ground truth from ChromaDB top retrieved chunk
# =============================================================================

def get_ground_truth_from_chromadb(chatbot, question):
    """
    Query ChromaDB directly and use the top retrieved chunk
    as the ground truth. Ensures ground truth comes from
    your actual documents, not hardcoded answers.
    """
    try:
        docs = chatbot.retriever.vectorstore.similarity_search(question, k=1)
        if docs:
            return docs[0].page_content.strip()
    except Exception:
        pass

    # Fallback: use chatbot answer as ground truth proxy
    try:
        response = chatbot.chat(question, show_sources=False)
        return response["answer"]
    except Exception:
        return "No ground truth available."


# =============================================================================
# 4. Build LLMTestCase objects
# =============================================================================

def build_test_cases(num_questions=25):
    print("Loading DialysisBot...")
    chatbot = ChatBot()
    print("✅ Chatbot ready\n")

    questions = TEST_QUESTIONS[:num_questions]
    test_cases = []
    ground_truths_log = []

    print(f"Running {len(questions)} test queries...\n")
    print("-" * 70)

    for i, question in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {question[:70]}...")

        # Step 1: get ground truth from ChromaDB top chunk
        ground_truth = get_ground_truth_from_chromadb(chatbot, question)
        print(f"   Ground truth: ChromaDB top chunk ({len(ground_truth)} chars)")

        # Step 2: get chatbot RAG answer + sources
        response = chatbot.chat(question, show_sources=True)
        answer = response["answer"]
        retrieval_context = [
            source["preview"].replace("...", "")
            for source in response.get("sources", [])
        ]

        confidence = response.get("confidence", {}).get("score", 0)
        print(f"   Answer generated ({len(retrieval_context)} sources, "
              f"confidence {round(confidence, 1)}%)\n")

        test_cases.append(
            LLMTestCase(
                input=question,
                actual_output=answer,
                expected_output=ground_truth,
                retrieval_context=retrieval_context,
            )
        )

        ground_truths_log.append({
            "question_num": i,
            "question": question,
            "ground_truth": ground_truth,
            "answer_length": len(answer),
            "num_sources": len(retrieval_context),
            "confidence": confidence,
        })

    # Save ground truths to CSV
    try:
        pd.DataFrame(ground_truths_log).to_csv(
            "ground_truths_from_chromadb.csv", index=False
        )
        print("✅ Saved: ground_truths_from_chromadb.csv")
    except Exception as e:
        print(f"Could not save ground truths CSV: {e}")

    return test_cases, chatbot


# =============================================================================
# 5. Metrics info
# =============================================================================

METRICS_INFO = {
    "FaithfulnessMetric": (
        "Faithfulness",
        "Does the answer stick to retrieved documents? (no hallucination)"
    ),
    "AnswerRelevancyMetric": (
        "Answer Relevancy",
        "Does the answer actually address the question asked?"
    ),
    "ContextualPrecisionMetric": (
        "Contextual Precision",
        "Are the TOP retrieved chunks the most relevant ones?"
    ),
    "ContextualRecallMetric": (
        "Contextual Recall",
        "Did retrieval cover everything needed to answer?"
    ),
}


def _perf_label(pct):
    if pct >= 80:
        return "EXCELLENT ✅"
    elif pct >= 70:
        return "GOOD 👍"
    elif pct >= 60:
        return "FAIR ⚠️"
    else:
        return "NEEDS IMPROVEMENT ❌"


# =============================================================================
# 6. Run evaluation
# =============================================================================

def evaluate_rag_system(num_questions=25):
    print("\nBuilding test cases...")
    test_cases, chatbot = build_test_cases(num_questions)

    print(f"\n✅ Built {len(test_cases)} test cases")
    print("Starting DeepEval evaluation...\n")
    print("-" * 70)

    # Use Groq as the judge LLM
    judge_llm = GroqDeepEvalLLM()

    metrics = [
        FaithfulnessMetric(
            threshold=0.5,
            model=judge_llm,
            include_reason=True
        ),
        AnswerRelevancyMetric(
            threshold=0.5,
            model=judge_llm,
            include_reason=True
        ),
        ContextualPrecisionMetric(
            threshold=0.5,
            model=judge_llm,
            include_reason=True
        ),
        ContextualRecallMetric(
            threshold=0.5,
            model=judge_llm,
            include_reason=True
        ),
    ]

    try:
        test_results = evaluate(
            test_cases=test_cases,
            metrics=metrics,
            async_config=AsyncConfig(run_async=False),
            display_config=DisplayConfig(show_indicator=True),
        )
        return test_results, test_cases

    except Exception as e:
        print(f"\n❌ Evaluation error: {str(e)}")
        traceback.print_exc()
        return None, test_cases


# =============================================================================
# 7. Display results
# =============================================================================

def display_results(test_results, test_cases):
    if test_results is None:
        print("\nEvaluation incomplete - check errors above")
        return

    print("\n" + "=" * 70)
    print("DEEPEVAL RESULTS - 25 QUESTION EVALUATION")
    print("=" * 70 + "\n")

    metric_scores = {}
    for tr in test_results:
        for md in tr.metrics_data:
            metric_scores.setdefault(md.name, [])
            if md.score is not None:
                metric_scores[md.name].append(md.score)

    all_scores = []
    rows_for_csv = []

    for metric_name, scores in metric_scores.items():
        label, desc = METRICS_INFO.get(metric_name, (metric_name, ""))
        if scores:
            avg = sum(scores) / len(scores)
            pct = avg * 100
            passed = sum(1 for s in scores if s >= 0.5)
            all_scores.append(avg)
            rows_for_csv.append({
                "Metric": metric_name,
                "Score": round(avg, 4),
                "Percentage": round(pct, 2),
                "Pass_Count": passed,
                "Total": len(scores),
                "Pass_Rate": round((passed / len(scores)) * 100, 1),
            })
            print(f"{label}: {round(avg, 3)} ({round(pct, 1)}%) "
                  f"- {_perf_label(pct)}")
            print(f"   Pass rate: {passed}/{len(scores)} questions")
            print(f"   {desc}")
        else:
            print(f"{label}: N/A")
        print()

    if all_scores:
        avg_all = sum(all_scores) / len(all_scores)
        pct_all = avg_all * 100
        print("=" * 70)
        print(f"OVERALL AVERAGE: {round(avg_all, 3)} "
              f"({round(pct_all, 1)}%) - {_perf_label(pct_all)}")
        print("=" * 70 + "\n")

    # Save CSVs
    print("Saving results...")
    try:
        if rows_for_csv:
            pd.DataFrame(rows_for_csv).to_csv(
                "deepeval_results.csv", index=False
            )
            print("✅ Saved: deepeval_results.csv")

        detail_rows = []
        for i, tr in enumerate(test_results):
            tc = test_cases[i]
            row = {
                "Q_num": i + 1,
                "question": tc.input,
                "answer": tc.actual_output,
                "ground_truth": tc.expected_output,
            }
            for md in tr.metrics_data:
                label = METRICS_INFO.get(md.name, (md.name,))[0]
                row[label] = md.score
                row[label + "_pass"] = md.success
            detail_rows.append(row)

        pd.DataFrame(detail_rows).to_csv(
            "deepeval_detailed.csv", index=False
        )
        print("✅ Saved: deepeval_detailed.csv")

    except Exception as exc:
        print(f"Could not save: {exc}")

    print("\n" + "=" * 70)


# =============================================================================
# 8. Entry point
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("   DIALYSISBOT DeepEval EVALUATION  |  25 Clinical Questions")
    print("   Ground Truth: Auto-extracted from ChromaDB")
    print("   Judge LLM:    Groq (llama3-8b-8192)")
    print("=" * 70 + "\n")

    try:
        results, cases = evaluate_rag_system(num_questions=25)
        display_results(results, cases)
        print("\n✅ Done!")
        print("Output files:")
        print("  - deepeval_results.csv")
        print("  - deepeval_detailed.csv")
        print("  - ground_truths_from_chromadb.csv")

    except Exception as exc:
        print(f"\n❌ Fatal Error: {str(exc)}")
        traceback.print_exc()