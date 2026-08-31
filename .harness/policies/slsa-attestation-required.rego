# Act 4: Pre-deploy governance gate.
# Purpose: Require SLSA L2+ attestation and cosign verification before deploy.

package harness.deploy.governance

import rego.v1

default deny := false

deny if {
	not input.artifact.attestation
}

deny if {
	input.artifact.attestation.slsa_level < 2
}

deny if {
	not input.artifact.attestation.cosign_verified
}

message contains msg if {
	not input.artifact.attestation
	msg := "Deploy blocked: artifact has no SLSA attestation"
}

message contains msg if {
	input.artifact.attestation.slsa_level < 2
	msg := sprintf("Deploy blocked: SLSA level %d does not meet minimum L2 requirement", [input.artifact.attestation.slsa_level])
}

message contains msg if {
	input.artifact.attestation.cosign_verified != true
	msg := "Deploy blocked: artifact signature not verified by cosign"
}
