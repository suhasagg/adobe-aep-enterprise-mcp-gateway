from app.policy import PolicyEngine
def test_reads_no_approval():
    d=PolicyEngine().evaluate(risk="READ",principal="p",tenant="t")
    assert d.allowed and not d.approval_required
def test_writes_require_approval():
    assert PolicyEngine().evaluate(risk="WRITE",principal="p",tenant="t").approval_required
