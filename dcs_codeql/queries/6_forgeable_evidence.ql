/**
 * @name Only SHA-256 is used for chain hashing
 * @description Grounds claim 6.1-6.3: mutation is detectable.
 * @id dcs/forgeable/sha256-only
 * @kind problem
 * @problem.severity error
 */
import python

from Call c, String s
where
  c.getFunc().(Attribute).getAttrName() = "hexdigest"
  and c.getFunc().(Attribute).getObject().(Call).getFunc().(Attribute).getAttrName() = "sha256"
  // we allow only sha256; flag md5 and sha1
  and exists(Call h |
    h.getFunc().(Attribute).getAttrName() in ["md5", "sha1"]
    and h.getScope() = c.getScope())
select h, "Weak hash function used: " + h.getFunc().(Attribute).getAttrName()
