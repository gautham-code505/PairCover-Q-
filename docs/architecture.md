# Q-Rescue Architecture

This document describes the intended flow for Q-Rescue — Quantum-Assisted Predictive Emergency Resource Allocation.

## Intended Flow

1. Load historical or clearly labelled synthetic ambulance data.
2. Estimate demand and prepare emergency/ambulance assignment costs.
3. Formulate a small ambulance assignment problem as QUBO.
4. Run QAOA with Qiskit on a simulator.
5. Compare against nearest-available dispatch and a classical exact optimization baseline.
6. Validate assignment feasibility and calculate response-time and future-coverage metrics.
7. Display the results through Streamlit.

## Experimental Setup

The first prototype will use a small scenario with three ambulances and four simultaneous emergency calls. It must preserve ambulance availability and capability constraints. Future coverage is an explicit objective to investigate, not a result we have already achieved.

## Data

Synthetic data will be used unless access to real operational data is confirmed. We do not claim live GPS, live traffic, quantum advantage, or real-world deployment.
