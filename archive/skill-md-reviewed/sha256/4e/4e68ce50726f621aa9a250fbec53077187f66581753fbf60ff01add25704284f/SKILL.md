---
name: hermes-bitwarden-setup
description: "Configure Bitwarden Secrets Manager for Hermes Agent to avoid BWS_ACCESS_TOKEN missing errors."
---
Triggers:
- User sees "Bitwarden Secrets Manager: secrets.bitwarden.enabled is true but BWS_ACCESS_TOKEN is not set."
- Need to set up Bitwarden CLI or environment variables for Hermes.
Steps:
  1. Install Bitwarden CLI (`bw`) if not present.
  2. Log in to Bitwarden via `bw login` (or use API key).
  3. Export the access token as environment variable `BWS_ACCESS_TOKEN`.
  4. Optionally store the token in Hermes secrets via `hermes secrets bitwarden setup`.
  5. Verify by running a Hermes command that previously failed.
Pitfalls:
  - Forgetting to unlock the vault before exporting token.
  - Using master password instead of API key for non-interactive environments.
  - Not setting the variable in the correct shell session (ensure it's exported before running Hermes).
References:
  - Bitwarden CLI documentation: https://bitwarden.com/help/cli/
  - Hermes secrets documentation: `hermes secrets --help`