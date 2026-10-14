/**
 * @name mesh-skills
 * @description Documented functions as mesh skills
 * @kind problem
 * @problem.severity info
 * @id py/mesh/skills
 */
import python

from Function f
where
  f.getLocation().getFile().getRelativePath().matches("app/%") and
  f.getDocstring() != ""
select f,
  "skill|" + f.getQualifiedName() + "|" +
  f.getLocation().getFile().getRelativePath() + "|" +
  f.getLocation().getStartLine().toString()
