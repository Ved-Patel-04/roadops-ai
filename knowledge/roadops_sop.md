# RoadOps POC Incident Assessment Policy

## Purpose

This document defines a simplified roadway incident assessment policy
for the RoadOps AI proof of concept.

It is intended for experimentation and evaluation only and does not
represent an official transportation-agency operational procedure.

---

## SOP-01: Verify Incident Information

RoadOps should avoid making assumptions when critical information is
missing.

Important incident information may include:

- roadway
- direction
- location
- incident type
- active-lane impact
- traffic conditions
- queue conditions
- expected incident duration

If sufficient information is unavailable, RoadOps may classify the
incident as INSUFFICIENT_INFORMATION.

---

## SOP-02: Active-Lane Impact

An incident affecting an active travel lane generally creates greater
operational impact than an incident located entirely on the shoulder.

Increasing numbers of blocked active lanes may increase incident
priority.

---

## SOP-03: Queue Monitoring

Traffic queues should be monitored when an incident produces
significant congestion.

Growing queues may increase operational concern because sudden upstream
slowing can contribute to secondary incidents.

---

## SOP-04: Changing Conditions

Incident assessments should be reevaluated when conditions change.

Relevant changes include:

- increasing or decreasing congestion
- growing or clearing traffic queues
- lane closures or reopenings
- worsening weather
- changing visibility
- changes in expected clearance duration

---

## SOP-05: Weather Context

Weather is a contextual risk factor.

Reduced visibility, heavy rain, or other adverse conditions may increase
operational concern when combined with lane blockage or congestion.

Weather alone does not automatically make an incident high priority.

---

## SOP-06: Duration

For this proof of concept:

- Minor-duration incident: less than 30 minutes
- Intermediate-duration incident: 30 minutes to 2 hours
- Major-duration incident: more than 2 hours

Duration contributes to operational impact but should not be considered
in isolation.

---

## SOP-07: Unsupported Assumptions

RoadOps must not assume facts that are not present in the incident
report or retrieved context.

Examples include:

- injuries
- hazardous materials
- incident cause
- additional blocked lanes
- emergency responders already on scene
- exact location when none was provided

Unknown information should remain explicitly marked as unknown.

---

## SOP-08: Human Decision Authority

RoadOps is a decision-support system.

It may provide:

- incident assessment
- priority recommendation
- supporting evidence
- uncertainty
- relevant operational guidance

RoadOps does not autonomously dispatch emergency resources, control
roadway infrastructure, or make final operational decisions.

---

# RoadOps POC Priority Framework

## LOW

Typical characteristics:

- no active travel lane blocked
- minimal traffic disruption
- shoulder-only incident
- little or no queue development
- no significant compounding contextual factors

---

## MEDIUM

Typical characteristics:

- one active lane affected
- moderate traffic disruption
- localized congestion
- limited compounding risk factors

---

## HIGH

Typical characteristics:

- multiple active lanes affected
- active-lane blockage combined with heavy congestion
- growing queue
- adverse weather combined with roadway impact
- multiple compounding operational factors
- potentially extended duration

---

## CRITICAL

Reserved for exceptional synthetic benchmark scenarios such as:

- complete roadway blockage
- extreme network disruption
- prolonged major incident combined with significant safety or traffic impact

---

## INSUFFICIENT_INFORMATION

Used when the available evidence does not support a reliable incident
assessment.

RoadOps should identify the missing information instead of inventing it.