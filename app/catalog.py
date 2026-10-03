# Explicit allowlisted examples. Paths should be validated against the API version enabled
# for the customer's Adobe organization before production use.
TOOLS=[
 {"name":"aep.list_datasets","product":"AEP","description":"List accessible AEP datasets",
  "method":"GET","path":"/data/foundation/catalog/dataSets","risk":"READ",
  "input_schema":{"type":"object","properties":{"limit":{"type":"integer","minimum":1,"maximum":100}}}},
 {"name":"aep.list_schemas","product":"AEP","description":"List XDM schemas",
  "method":"GET","path":"/data/foundation/schemaregistry/tenant/schemas","risk":"READ",
  "input_schema":{"type":"object","properties":{}}},
 {"name":"aep.create_segment_job","product":"AEP","description":"Create a segmentation job",
  "method":"POST","path":"/data/core/ups/segment/jobs","risk":"WRITE",
  "input_schema":{"type":"object","additionalProperties":True}},
]
