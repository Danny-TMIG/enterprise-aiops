/**
 * @name chain.append arity conformance
 * @description Grounds claim 1.1: every action in scope has one attestation.
 * @id dcs/aligned/chain-append-arity
 * @kind problem
 * @problem.severity error
 * @tags dcs grounded aligned
 */
import python

from Call c
where
  c.getFunc().(Attribute).getAttrName() = "append"
  and c.getFunc().(Attribute).getObject().(Name).getId() in ["chain", "self", "log"]
  and c.getNumArgument() < 4
select c, "chain.append called with fewer than 4 arguments; attestation incomplete"
