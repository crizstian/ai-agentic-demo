# Act 3: Blocks pipeline after STO scan.
# Purpose: Block pipeline if SAST found CRITICAL or HIGH (CVSS >= 9.0) findings.

package harness.security

import rego.v1

default deny := false

deny if {
	some finding in input.pipeline.security_scan.findings
	finding.severity == "CRITICAL"
}

deny if {
	some finding in input.pipeline.security_scan.findings
	finding.severity == "HIGH"
	finding.cvss >= 9.0
}

message contains msg if {
	critical := [f | some f in input.pipeline.security_scan.findings; f.severity == "CRITICAL"]
	high := [f | some f in input.pipeline.security_scan.findings; f.severity == "HIGH"; f.cvss >= 9.0]
	total := count(critical) + count(high)
	total > 0
	msg := sprintf("Pipeline blocked: %d critical/high-severity finding(s) detected by SAST scan", [total])
}
