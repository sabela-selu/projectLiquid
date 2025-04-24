# Memory Bank System - WindSurf Rules Implementation

[rule.MemoryBankSystem]
description = "Central hub for memory and process management"
children = ["CustomModes", "JITRuleLoading", "VisualProcessMaps", "MemoryBank"]
path = "memory_bank/"

[rule.MemoryBank]
description = "Handles storing, retrieving, and updating project memory."
parent = "MemoryBankSystem"
triggers = [
    "memory_query",
    "memory_update",
    "memory_insert",
    "stage_transition",
    "feature_completed",
    "decision_made"
]
actions = [
    "store_memory_entry",
    "retrieve_memory_entry",
    "update_memory_entry",
    "log_memory_access"
]
enforced = true
