/**
 * @name mesh-agents
 * @description Classes that look like mesh agents
 * @kind problem
 * @problem.severity info
 * @id py/mesh/agents
 */
import python

from Class c
where
  c.getLocation().getFile().getRelativePath().matches("app/%") and
  ( c.getName().matches("%Agent%") or
    c.getName().matches("%Runtime%") or
    c.getName().matches("%Mesh%")   or
    c.getName().matches("%Server%") or
    c.getName().matches("%Engine%") or
    c.getName().matches("%Router%") )
select c,
  "agent|" + c.getQualifiedName() + "|" +
  c.getLocation().getFile().getRelativePath() + "|" +
  c.getLocation().getStartLine().toString()
