/**
 * @name Belnap verdict mapping is total
 * @description Grounds claim 5.1-5.2: verdict is decidable and total.
 * @id dcs/finite/belnap-total
 * @kind problem
 * @problem.severity error
 */
import python

// Every dict literal mapping verdicts must contain all four Belnap states.
from Dict d, String k
where
  exists(String s | d.getAKey().(String).getText() = s |
    s in ["PASS", "FAIL", "UNKNOWN", "CONFLICT"])
  and d.getAKey() = k
  and k.getText() not in ["PASS", "FAIL", "UNKNOWN", "CONFLICT"]
select d, "Belnap mapping contains unexpected key: " + k.getText()
