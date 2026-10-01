/**
 * @name mesh-endpoints
 * @description FastAPI-style decorated handlers as mesh endpoints
 * @kind problem
 * @problem.severity info
 * @id py/mesh/endpoints
 */
import python

from Function f, Call c
where
  c = f.getADecorator() and
  c.getFunc().(Attribute).getAttr().(Name).getId() in
    ["get", "post", "put", "delete", "patch"] and
  f.getLocation().getFile().getRelativePath().matches("app/%")
select f,
  "endpoint|" + f.getName() + "|" +
  f.getLocation().getFile().getRelativePath() + "|" +
  f.getLocation().getStartLine().toString()
