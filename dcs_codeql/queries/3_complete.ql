/**
 * @name HATS tuples are 5-tuples with anchor
 * @description Grounds claim 3.1-3.4: every hat in scope has anchor + layer.
 * @id dcs/complete/hat-anchor-present
 * @kind problem
 * @problem.severity error
 */
import python

from Assign a, List l, Tuple t
where
  a.getTarget().(Name).getId() = "HATS"
  and a.getValue() = l
  and l.getAnElement() = t
  and (
    not t.getElement(4) instanceof String
    or t.getElement(4).(String).getText().length() < 2
  )
select t, "HAT tuple missing or empty anchor at index 4"
