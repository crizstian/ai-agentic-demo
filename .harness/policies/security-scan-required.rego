# Act 4: Ensures STO ran before deploy.
# Purpose: Require a completed security scan stage before deployment proceeds.

package harness.deploy.governance

import rego.v1

default deny := false

deny if {
	not security_scan_completed
}

security_scan_completed if {
	some stage in input.pipeline.stages
	stage.type == "security"
	stage.status == "completed"
}

message contains msg if {
	not security_scan_completed
	msg := "Deploy blocked: no completed security scan stage found in pipeline"
}
