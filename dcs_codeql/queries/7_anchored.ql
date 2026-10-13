/**
 * @name STANDARDS_BODIES is a non-trivial finite set
 * @description Grounds claim 7.2: anchor resolution is finite and named.
 * @id dcs/anchored/bodies-finite
 * @kind problem
 * @problem.severity error
 */
import python

from Assign a, Set s
where
  a.getTarget().(Name).getId() = "STANDARDS_BODIES"
  and a.getValue() = s
  and exists(String el | s.getAnElement() = el | el.getText().length() < 2)
select s, "STANDARDS_BODIES contains an empty or trivial string"
