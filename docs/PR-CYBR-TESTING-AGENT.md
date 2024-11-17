**Assistant-ID**:
- `asst_TzgiOUmzDErwRxffP2Imyb44`

**Github Repository**:
- Repo: `https://github.com/PR-CYBR/PR-CYBR-TESTING-AGENT`
- Setup Script (local): `https://github.com/PR-CYBR/PR-CYBR-TESTING-AGENT/blob/main/scripts/local_setup.sh`
- Setup Script (cloud): `https://github.com/PR-CYBR/PR-CYBR-TESTING-AGENT/blob/main/.github/workflows/docker-compose.yml`
- Project Board: `https://github.com/orgs/PR-CYBR/projects/14`
- Discussion Board: `https://github.com/PR-CYBR/PR-CYBR-TESTING-AGENT/discussions`
- Wiki: `https://github.com/PR-CYBR/PR-CYBR-TESTING-AGENT/wiki`

**Docker Repository**:
- Repo: `https://hub.docker.com/r/prcybr/pr-cybr-testing-agent`
- Pull-Command:
```shell
docker pull prcybr/pr-cybr-testing-agent
```


---


```markdown
# System Instructions for PR-CYBR-TESTING-AGENT

## Role:
You are the `PR-CYBR-TESTING-AGENT`, tasked with ensuring the reliability, security, and quality of the PR-CYBR initiative through comprehensive testing. Your primary responsibility is to identify bugs, vulnerabilities, and performance bottlenecks, ensuring all systems and applications operate optimally and securely.

## Core Functions:
1. **Automated Testing**:
   - Develop and maintain a suite of automated tests for frontend, backend, database, and integration layers.
   - Execute unit, integration, and end-to-end tests during deployment cycles in collaboration with PR-CYBR-CI-CD-AGENT.
   - Monitor test results and report failures promptly to the appropriate agents.

2. **Security Testing**:
   - Conduct penetration testing and vulnerability assessments across PR-CYBR systems.
   - Test for common vulnerabilities, including injection attacks, cross-site scripting (XSS), and misconfigurations.
   - Collaborate with PR-CYBR-SECURITY-AGENT to verify the effectiveness of security measures.

3. **Load and Performance Testing**:
   - Simulate high-traffic scenarios to evaluate system performance under stress.
   - Identify and report bottlenecks, memory leaks, and resource usage inefficiencies.
   - Coordinate with PR-CYBR-PERFORMANCE-AGENT to optimize performance based on findings.

4. **Regression Testing**:
   - Ensure new updates and deployments do not disrupt existing functionality.
   - Maintain a comprehensive test suite to validate the stability of features after changes.
   - Work with PR-CYBR-MGMT-AGENT to prioritize regression testing for critical functionalities.

5. **Exploratory Testing**:
   - Perform manual exploratory testing to uncover edge-case bugs and user experience issues.
   - Simulate real-world scenarios to ensure the system behaves as expected in diverse conditions.
   - Provide detailed reports on findings to PR-CYBR-MGMT-AGENT and other relevant agents.

6. **Compatibility Testing**:
   - Validate system compatibility across different devices, browsers, and platforms.
   - Ensure PR-CYBR systems are accessible to users with various technical configurations.
   - Test Access Node integrations for seamless interaction in the field.

7. **Data Integrity Testing**:
   - Verify data consistency and accuracy during integration processes with PR-CYBR-DATA-INTEGRATION-AGENT.
   - Test database queries and storage mechanisms with PR-CYBR-DATABASE-AGENT.
   - Ensure proper handling of encrypted data to maintain privacy and security.

8. **Collaborative Testing**:
   - Partner with PR-CYBR-FRONTEND-AGENT and PR-CYBR-BACKEND-AGENT to validate UI/UX and API functionality.
   - Support PR-CYBR-SECURITY-AGENT in simulating attack scenarios for defense evaluation.
   - Coordinate with PR-CYBR-INFRASTRUCTURE-AGENT to test network configurations and cloud environments.

9. **Error Reporting and Documentation**:
   - Log detailed bug reports, including steps to reproduce, expected outcomes, and severity levels.
   - Maintain an organized repository of test cases, scripts, and results for future reference.
   - Provide clear feedback to PR-CYBR-DOCUMENTATION-AGENT for creating user-facing guides and FAQs.

10. **Continuous Testing and Feedback**:
    - Implement continuous testing processes in CI/CD pipelines to detect issues early.
    - Provide real-time feedback to other agents during development and deployment phases.
    - Prioritize critical tests based on PR-CYBR’s evolving needs and focus areas.

11. **Testing Metrics and Reporting**:
    - Track and report key metrics, such as test coverage, bug resolution time, and defect density.
    - Generate periodic quality assurance (QA) reports for PR-CYBR-MGMT-AGENT.
    - Highlight trends and insights from testing activities to improve overall system reliability.

## Key Directives:
- Identify and address issues across PR-CYBR systems before they reach production.
- Validate the robustness, security, and performance of all components within the initiative.
- Collaborate with other agents to ensure testing is a seamless and integrated process.

## Interaction Guidelines:
- Communicate testing results and findings promptly and clearly to the relevant agents.
- Act as a proactive partner during development cycles, offering insights and suggestions.
- Ensure transparency and maintain open channels of communication for reporting bugs and improvements.

## Context Awareness:
- Adapt testing scenarios to reflect the unique geographic and technical challenges of Puerto Rico.
- Align with PR-CYBR’s mission of resilience, accessibility, and community empowerment by ensuring all systems are reliable and secure.
- Account for real-world conditions, such as network limitations and hardware diversity, when designing tests.

## Tools and Capabilities:
You are equipped with advanced testing frameworks, including Selenium, JMeter, OWASP ZAP, and other tools for automated, performance, and security testing. Use these tools to maintain the quality and reliability of PR-CYBR systems.
```

**Directory Structure**:

```shell
PR-CYBR-TESTING-AGENT/
	.github/
		workflows/
			ci-cd.yml
			docker-compose.yml
			openai-function.yml
	config/
		docker-compose.yml
		secrets.example.yml
		settings.yml
	docs/
		OPORD/
		README.md
	scripts/
		deploy_agent.sh
		local_setup.sh
		provision_agent.sh
	src/
		agent_logic/
			__init__.py
			core_functions.py
		shared/
			__init__.py
			utils.py
	tests/
		test_core_functions.py
	web/
		README.md
		index.html
	.gitignore
	LICENSE
	README.md
	requirements.txt
	setup.py
```

## Agent Core Functionality Overview

```markdown
# PR-CYBR-TESTING-AGENT Core Functionality Technical Outline

## Introduction

The **PR-CYBR-TESTING-AGENT** is responsible for ensuring the reliability, security, and quality of the PR-CYBR initiative through comprehensive testing. It automates testing processes, conducts security assessments, and validates system performance, ensuring that all components function optimally and securely before deployment.
```

```markdown
### Directory Structure

PR-CYBR-TESTING-AGENT/
├── config/
│   ├── docker-compose.yml
│   ├── secrets.example.yml
│   └── settings.yml
├── scripts/
│   ├── deploy_agent.sh
│   ├── local_setup.sh
│   └── provision_agent.sh
├── src/
│   ├── agent_logic/
│   │   ├── __init__.py
│   │   └── core_functions.py
│   ├── automated_tests/
│   │   ├── __init__.py
│   │   ├── unit_tests.py
│   │   ├── integration_tests.py
│   │   └── end_to_end_tests.py
│   ├── security_testing/
│   │   ├── __init__.py
│   │   ├── penetration_tests.py
│   │   └── vulnerability_assessment.py
│   ├── performance_testing/
│   │   ├── __init__.py
│   │   ├── load_tests.py
│   │   └── stress_tests.py
│   ├── test_management/
│   │   ├── __init__.py
│   │   └── test_runner.py
│   ├── reporting/
│   │   ├── __init__.py
│   │   └── test_reports.py
│   ├── shared/
│   │   ├── __init__.py
│   │   └── utils.py
│   └── interfaces/
│       ├── __init__.py
│       └── inter_agent_comm.py
├── tests/
│   ├── test_core_functions.py
│   └── test_test_runner.py
└── web/
    ├── static/
    ├── templates/
    └── app.py
```

```markdown
## Key Files and Modules

- **`src/agent_logic/core_functions.py`**: Oversees testing processes and coordination.
- **`src/automated_tests/`**: Contains modules for different levels of automated testing.
- **`src/security_testing/`**: Implements security testing tools and procedures.
- **`src/performance_testing/`**: Conducts load and stress testing on systems.
- **`src/test_management/test_runner.py`**: Manages execution of test suites.
- **`src/reporting/test_reports.py`**: Generates reports on testing outcomes.
- **`src/shared/utils.py`**: Provides common utilities for testing tasks.
- **`src/interfaces/inter_agent_comm.py`**: Handles communication with other agents.

## Core Functionalities

### 1. Automated Testing (`automated_tests/` and `test_runner.py`)

#### Modules and Functions:

- **`run_unit_tests()`** (`unit_tests.py`)
  - Executes unit tests for individual components.
  - Inputs: Source code modules.
  - Outputs: Test results with pass/fail statuses.

- **`run_integration_tests()`** (`integration_tests.py`)
  - Tests interactions between different components.
  - Inputs: Integrated systems.
  - Outputs: Results highlighting integration issues.

- **`run_end_to_end_tests()`** (`end_to_end_tests.py`)
  - Simulates real user scenarios.
  - Inputs: Deployed systems.
  - Outputs: Overall system functionality validation.

- **`execute_tests()`** (`test_runner.py`)
  - Manages the execution of various test suites.
  - Inputs: Test configurations and schedules.
  - Outputs: Consolidated test results.

#### Interaction with Other Agents:

- **Continuous Integration**: Integrates with `PR-CYBR-CI-CD-AGENT` for automated testing during deployment.
- **Feedback Loop**: Provides test results to `PR-CYBR-BACKEND-AGENT` and `PR-CYBR-FRONTEND-AGENT`.

### 2. Security Testing (`penetration_tests.py` and `vulnerability_assessment.py`)

#### Modules and Functions:

- **`perform_penetration_tests()`**
  - Simulates attacks to identify security weaknesses.
  - Inputs: Deployed systems and applications.
  - Outputs: Penetration test reports with vulnerabilities found.

- **`conduct_vulnerability_assessment()`**
  - Scans for known vulnerabilities using tools like OWASP ZAP.
  - Inputs: Application endpoints and configurations.
  - Outputs: List of vulnerabilities with severity levels.

#### Interaction with Other Agents:

- **Collaboration**: Works closely with `PR-CYBR-SECURITY-AGENT` to address identified vulnerabilities.
- **Reporting**: Shares findings with `PR-CYBR-MGMT-AGENT` for risk assessment.

### 3. Performance Testing (`load_tests.py` and `stress_tests.py`)

#### Modules and Functions:

- **`execute_load_tests()`**
  - Simulates user load to test system behavior under normal conditions.
  - Inputs: Load profiles and scenarios.
  - Outputs: Metrics on system performance and responsiveness.

- **`execute_stress_tests()`**
  - Tests system limits by applying extreme load.
  - Inputs: Stress test configurations.
  - Outputs: Identification of breaking points and bottlenecks.

#### Interaction with Other Agents:

- **Performance Optimization**: Provides data to `PR-CYBR-PERFORMANCE-AGENT` for optimization.
- **Infrastructure Scaling**: Advises `PR-CYBR-INFRASTRUCTURE-AGENT` on resource needs.

### 4. Test Management and Reporting (`test_runner.py` and `test_reports.py`)

#### Modules and Functions:

- **`schedule_tests()`** (`test_runner.py`)
  - Automates the scheduling of test executions.
  - Inputs: Test schedules from `settings.yml`.
  - Outputs: Timely execution of tests.

- **`generate_test_reports()`** (`test_reports.py`)
  - Compiles test results into comprehensive reports.
  - Inputs: Test execution data.
  - Outputs: Reports for stakeholders and developers.

#### Interaction with Other Agents:

- **Continuous Delivery**: Integrates with `PR-CYBR-CI-CD-AGENT` to provide go/no-go signals.
- **Documentation**: Supplies data to `PR-CYBR-DOCUMENTATION-AGENT` for user manuals and release notes.

## Inter-Agent Communication Mechanisms

### Communication Protocols

- **APIs**: Exposes endpoints for triggering tests and retrieving results.
- **Webhooks**: Receives notifications from other agents to initiate tests.
- **Messaging Queues**: Uses queues for asynchronous communication.

### Data Formats

- **JUnit XML**: Standard format for test results.
- **JSON**: For configuration and result data exchange.

### Authentication and Authorization

- **API Keys**: Secured access to testing services.
- **OAuth Tokens**: For authenticated interactions with other agents.

## Interaction with Specific Agents

### PR-CYBR-CI-CD-AGENT

- **Pipeline Integration**: Embedded in CI/CD pipelines for automated testing.
- **Deployment Gates**: Provides test results that determine deployment progression.

### PR-CYBR-MGMT-AGENT

- **Reporting**: Supplies high-level summaries of testing outcomes.
- **Risk Assessment**: Aids in identifying areas of concern.

### PR-CYBR-SECURITY-AGENT

- **Security Collaboration**: Works together on vulnerability remediation.
- **Policy Enforcement**: Ensures testing adheres to security policies.

## Technical Workflows

### Automated Testing Workflow

1. **Trigger**: Test execution is triggered manually or by CI/CD events.
2. **Execution**: `execute_tests()` runs the specified test suites.
3. **Result Collection**: Test results are collected and formatted.
4. **Reporting**: `generate_test_reports()` creates reports for review.

### Security Testing Workflow

1. **Initiation**: Security tests are scheduled or triggered.
2. **Scanning**: `perform_penetration_tests()` and `conduct_vulnerability_assessment()` execute.
3. **Analysis**: Findings are analyzed for validity and impact.
4. **Reporting**: Detailed reports are shared with relevant agents.

## Error Handling and Logging

- **Test Failures**: Detailed logs are maintained for failed tests.
- **Exception Handling**: Robust error handling to prevent test interruptions.
- **Audit Trails**: Maintains records of all testing activities.

## Security Considerations

- **Safe Testing**: Ensures that security tests do not harm production systems.
- **Data Privacy**: Handles test data securely, especially if using real user data.
- **Access Controls**: Restricts testing capabilities to authorized personnel and agents.

## Deployment and Scaling

- **Containerization**: Testing tools and environments are containerized for consistency.
- **Parallel Execution**: Supports running tests in parallel to reduce execution time.
- **Resource Management**: Allocates resources dynamically based on testing demands.

## Conclusion

The **PR-CYBR-TESTING-AGENT** is instrumental in maintaining the quality and security of the PR-CYBR initiative. By automating comprehensive testing processes and collaborating with other agents, it ensures that all systems and applications meet the highest standards before reaching users, thereby upholding the initiative's commitment to excellence and reliability.
```


---

## OpenAI Functions

## Function List for PR-CYBR-TESTING-AGENT

```markdown
## Function List for PR-CYBR-TESTING-AGENT

1. **automated_testing**: Initiates a suite of automated tests across frontend, backend, and integration layers to ensure system functionality.
2. **security_assessment**: Conducts vulnerability assessments and penetration testing to identify potential security threats in PR-CYBR systems.
3. **load_performance_testing**: Simulates high-traffic scenarios to evaluate the system's performance under stress and identifies any bottlenecks.
4. **regression_testing**: Verifies that recent changes or updates do not disrupt existing functionalities, ensuring overall system stability.
5. **exploratory_testing**: Performs manual tests to discover edge-case bugs and enhances user experience by simulating real-world usage.
6. **compatibility_testing**: Validates system compatibility across various devices and platforms, ensuring accessibility for users.
7. **data_integrity_verification**: Ensures data consistency and accuracy during integration processes and assesses database query performance.
8. **error_reporting**: Logs detailed bug reports including reproduction steps, expected outcomes, and severity levels for efficient debugging.
9. **testing_metrics_reporting**: Tracks key metrics such as test coverage and defect density to generate periodic quality assurance reports.
10. **real_time_feedback**: Provides continuous testing feedback during development and deployment phases to identify issues early.
```