terraform {
  required_version = ">= 1.5.0"
}

# The testing agent operates as a schema validation workspace.
# No infrastructure resources are managed from this repository.
# Terraform validate/plan are executed to guarantee the variable schema remains stable.
