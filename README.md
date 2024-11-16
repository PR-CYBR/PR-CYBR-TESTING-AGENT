# PR-CYBR-TESTING-AGENT

## Overview

The **PR-CYBR-TESTING-AGENT** ensures the quality and reliability of the PR-CYBR ecosystem by providing automated and comprehensive testing capabilities. It is designed to validate functionality, performance, and integration across all agents and systems.

## Key Features

- **Automated Testing**: Executes unit tests, integration tests, and performance benchmarks automatically.
- **Continuous Validation**: Integrates with CI/CD workflows to enforce quality checks on every commit or pull request.
- **Cross-Agent Compatibility**: Tests interdependencies and interactions across multiple agents.
- **Customizable Test Suites**: Allows developers to define and extend test cases as per project requirements.
- **Detailed Reporting**: Generates comprehensive reports on test results, including failures and coverage metrics.

## Getting Started

### Prerequisites

- **Git**: For cloning the repository.
- **Python 3.8+**: Required for running scripts.
- **Docker**: Required for containerization and deployment.
- **Access to GitHub Actions**: For automated workflows.

### Local Setup

To set up the `PR-CYBR-TESTING-AGENT` locally on your machine:

1. **Clone the Repository**

```bash
git clone https://github.com/PR-CYBR/PR-CYBR-TESTING-AGENT.git
cd PR-CYBR-TESTING-AGENT
```

2. **Run Local Setup Script**

```bash
./scripts/local_setup.sh
```
_This script will install necessary dependencies and set up the local environment._

3. **Provision the Agent**

```bash
./scripts/provision_agent.sh
```
_This script configures the agent with default settings for local development._

### Cloud Deployment

To deploy the agent to a cloud environment:

1. **Configure Repository Secrets**

- Navigate to `Settings` > `Secrets and variables` > `Actions` in your GitHub repository.
- Add the required secrets:
   - `CLOUD_API_KEY`
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_PASSWORD`
   - Any other cloud-specific credentials.

2. **Deploy Using GitHub Actions**

- The deployment workflow is defined in `.github/workflows/docker-compose.yml`.
- Push changes to the `main` branch to trigger the deployment workflow automatically.

3. **Manual Deployment**

- Use the deployment script for manual deployment:

```bash
./scripts/deploy_agent.sh
```

- Ensure you have Docker and cloud CLI tools installed and configured on your machine.

## Integration

The `PR-CYBR-TESTING-AGENT` integrates with other PR-CYBR agents to provide comprehensive testing across the ecosystem. It works closely with:

- **PR-CYBR-CI-CD-AGENT**: Integrates into the CI/CD pipeline to run tests on each build.
- **PR-CYBR-BACKEND-AGENT** and **PR-CYBR-FRONTEND-AGENT**: Executes tests on backend and frontend codebases.
- **PR-CYBR-SECURITY-AGENT**: Collaborates to include security tests in the test suites.
- **PR-CYBR-PERFORMANCE-AGENT**: Works together for performance testing and benchmarking.

## Usage

- **Development**

  - Run tests locally:

```bash
python -m unittest discover tests
```

  - Add or modify test cases in the `tests/` directory.

- **Testing**

  - Execute specific test suites:

```bash
python -m unittest tests/test_suite_name.py
```

- **Building for Production**

  - Build the agent for production use:

```bash
python setup.py install
```

## License

This project is licensed under the **MIT License**. See the [`LICENSE`](LICENSE) file for details.

---

For more information, refer to the [PR-CYBR Documentation](https://github.com/PR-CYBR/PR-CYBR-TESTING-AGENT/Wiki) or contact the PR-CYBR team.
