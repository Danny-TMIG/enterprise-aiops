/**
 * @name detect_rogue called in verification paths
 * @description Grounds claim 4.1-4.2: detection cost is bounded, deterministic.
 * @id dcs/prevention/detect-called
 * @kind problem
 * @problem.severity warning
 */
import python

from Call c
where
  c.getFunc().(Name).getId() = "detect_rogue"
select c, "detect_rogue call site: " + c.getLocation().getFile().getBaseName()
    + ":" + c.getLocation().getStartLine().toString()
