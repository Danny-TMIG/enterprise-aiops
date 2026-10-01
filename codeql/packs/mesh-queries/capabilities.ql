/**
 * @name mesh-capabilities
 * @description Functions in app/ as mesh capabilities
 * @kind problem
 * @problem.severity info
 * @id py/mesh/capabilities
 */
import python

from Function f
where f.getLocation().getFile().getRelativePath().matches("app/%")
select f,
  "capability|" + f.getQualifiedName() + "|" +
  f.getLocation().getFile().getRelativePath() + "|" +
  f.getLocation().getStartLine().toString()
