/**
 * @name mesh-modules
 * @description Python modules under app/ as mesh planes
 * @kind problem
 * @problem.severity info
 * @id py/mesh/modules
 */
import python

from Module m
where m.getLocation().getFile().getRelativePath().matches("app/%")
select m,
  "module|" + m.getName() + "|" +
  m.getLocation().getFile().getRelativePath()
