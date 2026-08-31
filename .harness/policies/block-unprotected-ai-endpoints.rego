# Act 6: After WAAP detects zombie API attack.
# Purpose: Block deploy of services with unprotected AI endpoints or prompt injection vulnerabilities.

package harness.ai_security

import rego.v1

default deny := false

deny if {
	some endpoint in input.service.endpoints
	contains(endpoint.path, "/ai/")
	endpoint.auth_required == false
}

deny if {
	input.service.scan_results.prompt_injection == true
}

message contains msg if {
	unprotected := [e | some e in input.service.endpoints; contains(e.path, "/ai/"); e.auth_required == false]
	count(unprotected) > 0
	msg := sprintf("Deploy blocked: %d AI endpoint(s) missing authentication", [count(unprotected)])
}

message contains msg if {
	input.service.scan_results.prompt_injection == true
	msg := "Deploy blocked: prompt injection vulnerability detected in service"
}
