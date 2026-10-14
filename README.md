# ITC560 Assessment 4 Greenhouse IoT Analytics

This repository contains the starter code for the ITC560 Assessment 4 template-repository task.

Students are given read access to this private template repository through the subject GitHub team. Use the template to create your own private working repository, then complete the notebook, output evidence, and report evidence in your copy.

You will analyse data from a simulated smart greenhouse. The dataset represents IoT telemetry: environmental sensor readings, actuator states, device health indicators, and gateway/network health measurements across two greenhouse zones. Your task is to turn those readings into useful evidence for greenhouse operations, platform planning, and risk analysis.

## Repository Setup

1. Sign in to GitHub with the account you will use for ITC560.
2. Open this private template repository after your subject access has been enabled.
3. Select **Use this template** and create a new repository in your own GitHub account.
4. Make your new repository **private**.
5. Use a clear repository name, such as `202660-itc560-a4-yourname` or `202660-itc560-a4-studentid`.
6. Open your new repository in GitHub Codespaces.

If you cannot see the template repository, your GitHub account may not yet have access through the subject team. Ask for help early rather than waiting until the submission week.

## Student Workflow

1. Open your private Assessment 4 repository in GitHub Codespaces.
2. Wait for the Codespace setup to finish installing the Python requirements.
3. Run the variant selector from the terminal:

   ```bash
   python src/variant_selector.py
   ```

4. Open `notebooks/ITC560_A4_analysis.ipynb`.
5. Complete the notebook analysis using the selected dataset in `data/selected/`.
6. Save your selected charts, tables, or summary files into `outputs/`.
7. Write the report using `report/ITC560_A4_report_template.md` as a guide. Save a repository evidence copy as `report/ITC560_A4_report.md`.
8. Commit and push the selected dataset, manifest, notebook, outputs, and report evidence to your private repository.
9. Upload the final report to Brightspace in the source format required by the subject outline.
10. Submit the GitHub repository URL and final commit hash in the Brightspace submission notes if requested.

If the notebook editor asks you to choose a kernel, select the default Python 3 kernel in the Codespace. If imports are still underlined while the notebook runs correctly, wait for the Python extension to finish loading or reload the Codespace window.

Before submission, use **Run All** in the notebook and then run `python -m pytest` from the terminal. After your dataset variant exists, the checks include a notebook execution check. If the notebook has a Python error, fix it before submitting.

## Dataset Variant

A manifest is a small JSON file that records which dataset variant was selected for your repository. In this assignment, the selector creates `data/selected/variant_manifest.json` and a matching CSV file. Once created, the manifest is reused so your analysis remains reproducible.

Do not delete the manifest to choose a different dataset unless your lecturer asks you to reset it.

## What Makes This An IoT Analysis Task

Do not treat the CSV file as just numbers to plot. Each field represents part of an IoT ecosystem:

- sensor data, such as temperature, humidity, soil moisture, and light;
- actuator state, such as fan and irrigation activity;
- device and gateway health, such as battery level, signal strength, latency, and packet loss;
- operational labels that help you reason about abnormal greenhouse behaviour.

Your notebook should show how you selected useful signals, created derived indicators, identified operational risk windows, and connected your findings to IoT design decisions. Your report should explain what the results imply for data management, service platforms, hardware choices, and security or privacy risk.

## Coding Challenge

The coding task is more than creating two charts. You should use code to:

- inspect and clean the selected dataset;
- choose data fields that matter for greenhouse monitoring and justify why they matter;
- create derived indicators, such as environmental risk, water stress, network degradation, or edge-action priority;
- identify time windows and greenhouse zones where attention is required;
- account for missing or unreliable sensor readings;
- produce at least four charts or tables that support clear operational and platform recommendations, including at least one output you create or materially adapt beyond the starter examples.

The assessment task and marking criteria will provide the formal requirements, but the notebook is where you build the technical evidence for the report.

The starter is designed for foundational Python skills. You are not expected to use advanced machine learning or advanced data-science libraries. Focus on adapting the examples, explaining your thresholds, creating meaningful indicators, and connecting your outputs to IoT decisions.

Limited use of Generative AI is permitted for the coding component only. You may use it to help understand Python errors, explain starter-code patterns, suggest coding approaches, or debug notebook code. You must still check the code, run the notebook, understand the results, and make sure your submitted work is accurate and reproducible.

Do not use Generative AI to write the report, interpret the data for you, create recommendations, complete the security and privacy reflection, or replace your own professional judgement. Your report must include a GenAI declaration. If you used Generative AI for coding support, include the tool, purpose, prompts used, and how you checked and revised the output. If you did not use Generative AI, state "No Generative AI used".

## Template Checks

The tests are intended for structural feedback only. Passing tests does not mean the assessment is complete or correct.

```bash
python -m pytest
```

The GitHub workflow in `.github/workflows/starter-checks.yml` runs the same structural checks when changes are pushed. Some checks are skipped until a dataset variant has been selected. After the manifest exists, the checks expect committed output evidence, a report evidence draft, and a notebook that runs from top to bottom without errors.
