/**
 * @name Verification functions are offline
 * @description Grounds claim 8.2-8.4: verification requires no network.
 * @id dcs/externally-verifiable/offline
 * @kind problem
 * @problem.severity error
 */
import python

from Function f, Call c
where
  f.getName() in [
    "verify", "verify_license", "verify_all", "verify_chain",
    "verify_inclusion", "verify_attestation"
  ]
  and c.getScope() = f
  and c.getFunc().(Attribute).getAttrName() in [
    "urlopen", "get", "post", "request", "socket", "connect"
  ]
select c, "Verification function " + f.getName()
    + " makes network call: " + c.getFunc().(Attribute).getAttrName()
