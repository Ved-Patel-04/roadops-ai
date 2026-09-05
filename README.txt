# RoadOps AI

### Agentic Roadway Incident Decision-Support System

RoadOps AI is a proof-of-concept agentic AI system designed to assist roadway operations personnel in assessing incidents by combining an initial incident report with relevant operational context, policy guidance, and structured AI reasoning.

Rather than sending an incident description directly to a language model, RoadOps uses an agentic workflow that determines which information sources are relevant, retrieves contextual evidence through tools, applies a simplified roadway operations policy framework, and produces a structured assessment for human review.

> **RoadOps is a decision-support proof of concept. It does not autonomously dispatch responders, control roadway infrastructure, or replace human operational authority.**

---

## The Problem

Roadway incident assessment can require operators to consider information from several different sources.

An initial incident report may contain only a portion of the information needed to understand the operational impact of an event. Relevant context may include:

- Active-lane blockage
- Traffic conditions
- Queue development
- Weather
- Visibility
- Incident duration
- Incident-management information
- Standard operating procedures

A language model operating only on the initial report may therefore have insufficient context or may rely too heavily on assumptions.

RoadOps explores whether an AI agent can improve this process by actively gathering relevant context before producing an assessment.

---

## Design Goal

The goal of RoadOps was not simply to build an LLM-powered dashboard.

The project was designed around the following hypothesis:

> **Providing an LLM with autonomous contextual retrieval, structured reasoning, operating-procedure grounding, and validation will improve incident-assessment quality compared with an LLM operating only on the initial incident description.**

To test this, RoadOps was compared against an initial-report-only baseline using the **same underlying language model**.

This helps isolate the value of the agent architecture rather than comparing different models.

---

# System Architecture

RoadOps separates incident intake, planning, contextual retrieval, policy grounding, assessment, and human review.

```text
                         INCIDENT REPORT
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v
       REPORTED CONTEXT                AGENT PLANNER
          EXTRACTION                         |
                 |             +-------------+-------------+
                 |             |             |             |
                 |             v             v             v
                 |          TRAFFIC       WEATHER       INCIDENT
                 |           TOOL           TOOL       DETAILS TOOL
                 |                                         
                 |                          +--------------+
                 |                          |
                 |                          v
                 |                       SOP / POLICY
                 |                          TOOL
                 |                           |
                 +-------------+-------------+
                               |
                               v
                       GATHERED CONTEXT
                               |
                               v
                       ASSESSMENT AGENT
                               |
                               v
                    STRUCTURED ASSESSMENT
                               |
                               v
                         HUMAN REVIEW
```

The original incident report is also provided directly to the assessment agent so that explicitly reported information is not lost during context gathering.

---

## Agent Workflow

### 1. Incident Report

The workflow begins with a roadway incident description entered by an operator or selected from the included benchmark scenarios.

Example:

```text
Sedan crash on I-75. Right lane blocked and heavy rain.
```

---

### 2. Reported Context Extraction

RoadOps extracts structured information that is **explicitly stated** in the initial report.

Possible fields include:

- Roadway
- Direction
- Incident type
- Lane impact
- Number of blocked active lanes
- Traffic level
- Queue status
- Weather
- Visibility
- Duration

The extraction layer is intentionally conservative.

For example:

```text
"heavy rain"
```

may support:

```text
weather = "heavy rain"
```

but RoadOps will **not automatically infer reduced visibility** unless reduced visibility is explicitly reported or provided by another evidence source.

This component was added as a post-evaluation product enhancement after custom-input testing revealed that operator-reported facts were correctly understood by the assessment model but were not always represented in the UI's contextual evidence cards.

The frozen holdout results reported below were produced **before this enhancement and were not rerun or retroactively modified**.

---

### 3. Agent Planner

The planner examines the incident and determines which contextual information sources would be useful.

Available tools include:

- Traffic Data Tool
- Weather Tool
- Incident Details Tool
- SOP / Policy Tool

The planner returns a structured tool plan containing the selected tools and its reason for selecting each source.

Planning is separated from final assessment so the decision about **what information to retrieve** is not conflated with the decision about **how the incident should be classified**.

---

### 4. Traffic Data Tool

The Traffic Data Tool provides synthetic operational traffic context such as:

- Traffic level
- Queue status
- Average speed
- Normal/reference speed

The current proof of concept uses deterministic local JSON data.

This was an intentional design decision to make demonstrations and evaluations reproducible.

The tool interface is isolated from the rest of the agent so that a future implementation could replace the synthetic source with an authorized real-time traffic data service without redesigning the complete workflow.

---

### 5. Weather Tool

The Weather Tool retrieves contextual weather information associated with an incident.

Example information includes:

- Weather conditions
- Visibility

Weather is treated as a contextual factor rather than an automatic reason to classify an incident as high priority.

For example, adverse weather combined with significant roadway impact may increase operational concern, while adverse weather alone does not necessarily make a shoulder-only incident high priority.

---

### 6. Incident Details Tool

During early development testing, RoadOps could retrieve traffic, weather, and policy information but had no source for structured operational facts such as:

- Number of blocked lanes
- Lane-impact information
- Incident duration

One development scenario exposed this limitation: the benchmark contained important incident details that the agent could not actually observe.

Instead of exposing hidden benchmark answers directly to the model, RoadOps was expanded with a separate **Incident Details Tool** representing a synthetic incident-management/CAD-style source.

This preserves separation between:

1. The initial operator report
2. External operational context
3. The benchmark answer key

---

### 7. SOP / Policy Retrieval

RoadOps retrieves relevant guidance from a simplified proof-of-concept roadway operations policy.

The policy includes guidance related to:

- Information verification
- Lane impact
- Queue monitoring
- Changing traffic conditions
- Weather
- Incident duration
- Unsupported assumptions
- Human authority
- Priority classification

The policy framework is informed by publicly available roadway incident-management guidance, including material from the U.S. Federal Highway Administration (FHWA).

**The RoadOps priority framework itself is a simplified POC policy and should not be interpreted as an official FHWA classification standard.**

---

### 8. Assessment Agent

The assessment agent receives:

- Original incident report
- Structured reported context
- Retrieved traffic context
- Retrieved weather context
- Retrieved incident details
- Relevant policy guidance

It produces a validated structured assessment containing:

```text
Priority
Confidence
Identified Factors
Recommended Actions
Missing Information
Reasoning Summary
```

Supported priorities are:

```text
LOW
MEDIUM
HIGH
CRITICAL
INSUFFICIENT_INFORMATION
```

Missing information is surfaced explicitly.

Missing information can reduce confidence, but RoadOps does not automatically classify every incomplete incident as `INSUFFICIENT_INFORMATION` when the available evidence still strongly supports an operational classification.

---

### 9. Human Review

RoadOps deliberately ends with a human decision point.

The system provides decision support rather than autonomous operational authority.

A human operator remains responsible for reviewing the evidence and determining the appropriate real-world response.

---

# Evaluation

RoadOps was evaluated against an initial-report-only LLM baseline.

Both systems used the **same underlying model**.

The primary difference was the information and architecture available to each system.

### Baseline

```text
Initial Report
      |
      v
     LLM
      |
      v
Assessment
```

The baseline had:

- No traffic tool
- No weather tool
- No incident-details tool
- No SOP retrieval
- No agentic contextual retrieval

### RoadOps

```text
Initial Report
      |
      v
Agent Planning
      |
      v
Contextual Tools + Policy
      |
      v
Evidence Gathering
      |
      v
Assessment
```

This comparison was designed to test the value of the **system architecture**, rather than simply testing one language model against another.

---

## Frozen Holdout Benchmark

Four initial scenarios (`A1-A4`) were used during development to identify architectural and evaluation problems.

After the architecture and tool interfaces were established, a separate **20-case holdout benchmark (`A5-A24`)** was created.

The holdout scenarios included combinations of:

- Active-lane impacts
- Shoulder incidents
- Light, moderate, and heavy congestion
- Queue development
- Adverse weather
- Extended incident duration
- Missing or ambiguous information
- Severe roadway disruption
- Exceptional full-closure scenarios

The holdout benchmark was frozen before final RoadOps evaluation.

The baseline was executed and preserved, followed by a single frozen RoadOps evaluation run.

The benchmark labels were not changed based on final RoadOps predictions.

---

## Holdout Results

| Metric | Baseline | RoadOps |
|---|---:|---:|
| **Priority Accuracy** | 5.0% | **95.0%** |
| **Critical-Factor Recall** | 23.2% | **92.2%** |
| **Guidance Coverage** | 28.3% | **81.7%** |
| **Prohibited Affirmative Matches*** | 0 | **0** |

**Priority accuracy improved by 90.0 percentage points.**

**Critical-factor recall improved by 69.0 percentage points.**

**Guidance coverage improved by 53.4 percentage points.**

\*The prohibited-assumption metric is a deterministic benchmark evaluator and should not be interpreted as proof that the system can never hallucinate. Under the final benchmark rules, the evaluator detected zero prohibited affirmative claims in the frozen outputs.

---

## Holdout Performance

RoadOps correctly classified:

```text
19 / 20 holdout incidents
```

for a final holdout priority accuracy of:

```text
95.0%
```

The initial-report-only baseline correctly classified:

```text
1 / 20 holdout incidents
```

for:

```text
5.0%
```

The baseline's poor performance should be interpreted specifically within this synthetic benchmark: many scenarios intentionally placed decision-relevant operational information outside the initial report.

---

## Failure Analysis

RoadOps was not perfect.

The sole RoadOps priority miss occurred on case `A15`.

The scenario represented a prolonged shoulder incident with:

- No active-lane blockage
- No queue
- Otherwise limited roadway impact
- Extended duration

The frozen benchmark expected `MEDIUM`, while RoadOps predicted `LOW`.

This exposed an ambiguity in the simplified policy: how strongly should extended duration increase priority when the incident otherwise remains a low-impact shoulder event?

The benchmark label and original RoadOps prediction were retained rather than modifying the case after evaluation.

This case represents a useful area for future policy refinement.

---

# Evaluation Methodology

Several controls were used to make the comparison more meaningful.

## Same Model

The baseline and RoadOps use the same underlying LLM.

This reduces the likelihood that improvements are simply caused by using a stronger model.

---

## Frozen Evaluation Data

Development cases were separated from the final holdout benchmark.

The final holdout set was frozen before RoadOps evaluation to reduce post-hoc benchmark modification.

---

## Preserved Outputs

Baseline and RoadOps holdout outputs were preserved so evaluation results could be inspected after execution rather than selectively replacing individual predictions.

---

## Independent Evaluation

Early in development, the assessment schema asked the model to report its own unsupported assumptions.

Testing showed that this was not a reliable evaluation strategy: the model could describe assumptions that **would be unsupported** rather than identifying assumptions it had actually made.

Unsupported-assumption detection was therefore moved into a separate deterministic evaluation layer.

---

## Assertion-Aware Evaluation

Initial versions of the evaluator used lexical matching.

This exposed another problem.

Statements such as:

```text
"queue status is unavailable"
```

could incorrectly trigger the prohibited term:

```text
queue
```

even though the model was explicitly stating that the information was unknown.

The evaluator was therefore refined to distinguish affirmative factual assertions from:

- Missing-information statements
- Explicitly unavailable information
- Negated statements
- Expressions of uncertainty

The generated RoadOps outputs themselves were not modified while making these evaluator corrections.

---

# Development Process

RoadOps was developed iteratively rather than implementing the final architecture immediately.

Several development observations directly changed the system design.

### Initial Workflow

The first version established:

```text
Incident
→ Planner
→ Tools
→ Evidence
→ Assessment
```

A simple deterministic keyword-based SOP retrieval system was initially used.

The purpose was to validate the complete orchestration pipeline before introducing more sophisticated retrieval behavior.

---

### Development Benchmark Findings

The first four-case end-to-end benchmark exposed multiple different failure modes:

- Priority calibration
- Incomplete tool selection
- Policy retrieval limitations
- Missing access to operational incident details

The initial RoadOps implementation improved development-set priority accuracy from 25% to 75%, but the small four-case development set was used for system iteration and is **not presented as final model performance**.

---

### SOP Retrieval Improvement

One development case showed that dynamic keyword retrieval could retrieve relevant incident procedures while failing to include the complete priority framework.

Because priority definitions are globally relevant to every classification, the SOP tool was changed to:

1. Always provide the complete priority framework
2. Dynamically retrieve incident-specific policy sections

This improved priority calibration stability during development testing.

---

### Missing-Information Policy

An early revision became overly conservative when information was missing.

The system could treat one unavailable field as disqualifying even when strong operational evidence was already available.

The assessment policy was refined so that missing information:

- Is explicitly surfaced
- Can reduce confidence
- Does not automatically override strong observed operational evidence

---

### Incident Details Tool

Development testing revealed that some operational facts could not be retrieved through the original traffic, weather, or SOP tools.

Rather than exposing benchmark answer data directly, a separate Incident Details Tool was introduced.

This created a cleaner boundary between operational evidence and evaluation labels.

---

### Baseline Variability

Repeated development runs demonstrated that the baseline LLM could produce different classifications for the same incident.

To prevent the control group from drifting while the RoadOps architecture was being modified, the initial baseline outputs were frozen for subsequent development comparisons.

---

### Reported-Context Enhancement

After the frozen holdout evaluation was complete, custom-input testing exposed a product-level issue.

The assessment model correctly understood information explicitly stated in a custom operator report, but some UI context cards showed the information as unavailable because the synthetic external feeds were keyed to benchmark incident IDs.

A structured reported-context extraction layer was added.

The UI now distinguishes between evidence originating from:

```text
Initial Incident Report
```

and evidence originating from external/synthetic sources such as:

```text
Traffic Data Source
Weather Data Source
Incident Details Source
```

This prevents the interface from presenting operator-reported information as though it came from an external API.

This enhancement was added **after the frozen evaluation**, so the reported holdout metrics were not rerun or attributed to this feature.

---

# Agent Behavior

RoadOps uses structured model outputs throughout the workflow.

Pydantic schemas define contracts for:

- Incident input
- Tool planning
- Reported context
- Incident assessment

Structured outputs reduce downstream parsing ambiguity and make agent state easier to validate and display.

---

## Tool Selection Behavior

The planner dynamically generates tool-selection decisions and reasons.

However, during the final 20-case holdout evaluation, it selected:

```text
Traffic Tool:          20 / 20
Weather Tool:          20 / 20
Incident Details Tool: 20 / 20
SOP Tool:              20 / 20
```

This indicates that the current planner favors **context completeness over tool-call efficiency**.

That is a known limitation rather than evidence of optimized tool selection.

A future version could evaluate whether individual tool calls provide enough expected information gain to justify their latency and cost.

---

# User Interface

RoadOps includes two primary modes.

## Operator Mode

Operator Mode intentionally hides most implementation complexity.

It focuses on information useful to an operational user:

- Priority
- Confidence
- Traffic context
- Weather context
- Roadway impact
- Duration
- Recommended actions
- Missing information
- Reasoning summary
- Human-review status

The goal is to avoid exposing unnecessary agent internals to an end user.

---

## Developer Mode

Developer Mode exposes the technical workflow.

It includes:

- Agent execution
- Planner decisions
- Tool usage
- Retrieved tool data
- Policy context
- Evaluation results

Before entering the developer console, the interface presents an architecture briefing showing how the incident report moves through reported-context extraction, agent planning, evidence retrieval, assessment, and human review.

This separation allows the same proof of concept to demonstrate both:

1. The end-user experience
2. The underlying engineering architecture

---

# Project Structure

```text
roadops-ai/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── agent/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── assessor.py
│   ├── orchestrator.py
│   ├── report_parser.py
│   └── reporter.py
│
├── tools/
│   ├── __init__.py
│   ├── traffic_tool.py
│   ├── weather_tool.py
│   ├── incident_details_tool.py
│   └── sop_tool.py
│
├── schemas/
│   ├── __init__.py
│   └── models.py
│
├── data/
│   ├── benchmark.json
│   ├── benchmark_frozen_v1.json
│   ├── traffic_context.json
│   ├── weather_context.json
│   └── incident_details.json
│
├── knowledge/
│   └── roadops_sop.md
│
├── evaluation/
│   ├── baseline.py
│   ├── roadops_eval.py
│   ├── metrics.py
│   ├── holdout_baseline.py
│   ├── holdout_roadops.py
│   └── holdout_metrics.py
│
└── outputs/
    ├── holdout_baseline_v1.json
    └── holdout_roadops_v1.json
```

---

# Running RoadOps Locally

## 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd roadops-ai
```

---

## 2. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

---

## 4. Configure the OpenAI API Key

Create a local `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

The `.env` file is excluded from version control.

**Never commit API credentials to the repository.**

---

## 5. Start the Application

```bash
python -m streamlit run app.py
```

Streamlit will provide a local application URL.

---

# Core Technologies

RoadOps uses:

- Python
- Streamlit
- OpenAI API
- Pydantic
- Structured Outputs
- JSON-based deterministic context sources
- Custom agent orchestration
- Deterministic evaluation logic

The project intentionally focuses on understanding and implementing the agent workflow rather than relying on a large external agent framework.

---

# Current Limitations

RoadOps is a proof of concept and has several important limitations.

### Synthetic Operational Data

Traffic, weather, and incident-management context currently comes from deterministic local data rather than production transportation systems.

This enables reproducible evaluation but does not represent live operational deployment.

### Simplified Policy

The RoadOps priority framework is a simplified POC policy.

It is not an official transportation-agency incident classification standard.

### Small Benchmark

The final holdout contains 20 synthetic incidents.

The results demonstrate behavior within this controlled benchmark and should not be interpreted as production-level validation.

### Planner Efficiency

The planner selected all four tools for every holdout case.

Future work should evaluate selective retrieval based on expected information value, latency, and cost.

### LLM Variability

Language-model outputs can vary between executions.

RoadOps reduces some uncertainty through structured outputs and grounding, but model behavior is not perfectly deterministic.

### External System Integration

The current implementation does not connect to production CAD, traffic-management, weather, dispatch, or roadway-control systems.

### Human Review Required

RoadOps is not designed to make autonomous safety-critical decisions.

Human review remains required.

---

# References

The proof-of-concept policy design was informed by publicly available Federal Highway Administration Traffic Incident Management resources.

- FHWA Traffic Incident Management Program  
  https://ops.fhwa.dot.gov/tim/

- FHWA Responder and Motorist Safety  
  https://ops.fhwa.dot.gov/tim/about/rms.htm

- FHWA Traffic Management Center Incident Information  
  https://ops.fhwa.dot.gov/publications/fhwahop14022/chapter4.htm

- FHWA Incident Duration Guidance  
  https://ops.fhwa.dot.gov/publications/fhwahop10014/s5.htm

These references informed the project context. The **RoadOps priority framework is independently simplified for this proof of concept and is not an official FHWA policy or classification system.**

---

# Project Status

**Proof of Concept**

RoadOps AI was built to demonstrate how an agentic AI architecture can combine contextual retrieval, policy grounding, structured reasoning, evaluation, and human review for a transportation operations use case.

The project emphasizes not only the final application, but also measurable comparison against a baseline, preservation of evaluation results, analysis of failure cases, and transparent documentation of system limitations.
