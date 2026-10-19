"""
Role-Based Access Control (RBAC) Module
Implements permissions and visibility rules per the Security & Access Document.

Roles:
  1. CISO / Security Architect (Full administrative & executive access)
  2. Risk & Compliance Officer (Executive risk view; raw algorithm/key size masked)
  3. Cryptography / Infra Engineer (Technical engineering focus; exports disabled)
  4. Guest / Demo Viewer (Strictly read-only access)
"""

from typing import Dict, Any

ROLES = [
    "CISO / Security Architect",
    "Risk & Compliance Officer",
    "Cryptography / Infra Engineer",
    "Guest / Demo Viewer",
]

ROLE_PERMISSIONS: Dict[str, Dict[str, Any]] = {
    "CISO / Security Architect": {
        "can_upload_csv": True,
        "can_add_asset": True,
        "can_run_scoring": True,
        "can_export_reports": True,
        "can_simulate_scenarios": True,
        "see_technical_algo_keys": True,
        "badge_color": "#0B1F3A",
        "description": "Full enterprise privileges: architectural risk review, scoring execution, and audit exports.",
    },
    "Risk & Compliance Officer": {
        "can_upload_csv": False,
        "can_add_asset": False,
        "can_run_scoring": True,
        "can_export_reports": True,
        "can_simulate_scenarios": True,
        "see_technical_algo_keys": False,  # Masks raw algorithm & bitlength
        "badge_color": "#3A6EA5",
        "description": "Governance focus: high-level risk metrics, compliance status, and reporting (technical keys masked).",
    },
    "Cryptography / Infra Engineer": {
        "can_upload_csv": True,
        "can_add_asset": True,
        "can_run_scoring": True,
        "can_export_reports": False,
        "can_simulate_scenarios": False,
        "see_technical_algo_keys": True,
        "badge_color": "#219653",
        "description": "Engineering focus: key management, bitlength specs, and NIST PQC target implementation.",
    },
    "Guest / Demo Viewer": {
        "can_upload_csv": False,
        "can_add_asset": False,
        "can_run_scoring": False,
        "can_export_reports": False,
        "can_simulate_scenarios": False,
        "see_technical_algo_keys": True,
        "badge_color": "#6B7280",
        "description": "Read-only access: exploratory view of baseline dashboards and metrics without write permissions.",
    },
}

def get_role_permissions(role_name: str) -> Dict[str, Any]:
    """Returns permission configuration dictionary for a given role."""
    return ROLE_PERMISSIONS.get(role_name, ROLE_PERMISSIONS["Guest / Demo Viewer"])
