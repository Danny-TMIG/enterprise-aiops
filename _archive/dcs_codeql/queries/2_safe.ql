/**
 * @name Signature verification is checked
 * @description Grounds claim 2.1: every executed action leaves a signed record.
 * @id dcs/safe/signature-checked
 * @kind problem
 * @problem.severity warning
 */
import python

from Call verify, Call caller
where
  verify.getFunc().(Attribute).getAttrName() = "verify"
  and verify.getFunc().(Attribute).getObject().(Name).getId() in ["att", "cert", "entry"]
  and caller.getScope() = verify.getScope()
  and not exists(If i | i.getScope() = verify.getScope() and i.contains(verify))
select verify, "Signature verification result not used in a conditional"
