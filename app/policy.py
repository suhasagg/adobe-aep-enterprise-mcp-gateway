from dataclasses import dataclass
@dataclass
class Decision:
    allowed:bool
    approval_required:bool=False
    reason:str=""

class PolicyEngine:
    def evaluate(self, *, risk:str, principal:str, tenant:str)->Decision:
        # Replace with OPA/Cedar/custom enterprise policy service.
        if risk=="BLOCKED": return Decision(False,False,"tool blocked by policy")
        if risk in {"WRITE","HIGH"}: return Decision(True,True,"mutating/high-risk action")
        return Decision(True,False,"read action")
