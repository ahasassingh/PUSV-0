"""
Deterministic Requirement Normalizer and Gap Analyzer.
Extracts fields (system, subsystem, inputs, outputs, conditions, threshold, timing, ASIL)
based strictly on deterministic rules, patterns, and controlled vocabularies.
Never fabricates values. Missing safety values trigger specification gaps.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from app.services.document_extractor import DocumentUnit

# Generalized Requirement ID regex:
# Matches patterns like:
# BRK-001, BRK-REQ-001, ADAS-REQ-101, SRS-001, REQ-001, TPMS-REQ-004, COMM-REQ-012, PUSV-SYS-001
REQ_ID_PATTERN = re.compile(
    r'\b([A-Z]{2,6}(?:-[A-Z]{2,6})*-\d{3,4})\b[:\s\-]*',
    re.IGNORECASE
)

# System and subsystem taxonomy
SYSTEM_TAXONOMY = {
    "Braking": {
        "keywords": ["brake", "braking", "abs", "caliper", "hydraulic pressure", "deceleration", "ebld", "ebd", "wheel slip", "stop within"],
        "default_subsystem": "Brake Control",
        "subsystems": {
            "Emergency Braking": ["emergency", "peak deceleration", "maximum brake", "collision stop"],
            "ABS Modulation": ["abs", "wheel slip", "anti-lock", "lockup"],
            "Electronic Brakeforce Distribution": ["proportioning", "axle load", "ebld", "ebd"],
            "Brake Assist": ["assist", "pedal velocity", "boost"],
            "Deceleration Degradation": ["friction", "wet surface", "low friction"]
        }
    },
    "ADAS": {
        "keywords": ["adas", "collision warning", "fcw", "aeb", "lane keep", "radar", "camera", "pedestrian", "obstacle", "ttc", "time-to-collision", "cut-in"],
        "default_subsystem": "Perception & Active Safety",
        "subsystems": {
            "Forward Collision Warning": ["fcw", "collision warning", "warning buzzer", "ttc"],
            "Autonomous Emergency Braking": ["aeb", "autonomous emergency", "emergency braking trigger"],
            "Sensor Fusion": ["fusion", "radar and camera", "camera and radar"],
            "Lane Keeping Assistance": ["lane", "lka", "lane departure", "boundary"]
        }
    },
    "TPMS": {
        "keywords": ["tpms", "tyre pressure", "tire pressure", "deflation", "bar", "psi", "wheel tyre", "wheel tire"],
        "default_subsystem": "Tyre Pressure Monitoring",
        "subsystems": {
            "Pressure Monitoring": ["pressure below", "low pressure", "threshold bar", "rapid deflation"],
            "Temperature Monitoring": ["temperature", "thermal", "overheat"]
        }
    },
    "Dynamics": {
        "keywords": ["esc", "esp", "stability", "yaw rate", "sideslip", "lateral accel", "traction", "understeer", "oversteer", "rollover"],
        "default_subsystem": "Vehicle Dynamics Control",
        "subsystems": {
            "Electronic Stability Control": ["yaw rate", "sideslip", "stability control", "understeer"],
            "Traction Control": ["traction", "spin", "torque reduction"]
        }
    },
    "Powertrain": {
        "keywords": ["powertrain", "torque", "motor", "engine", "throttle", "gear", "rpm", "transmission", "drive-by-wire"],
        "default_subsystem": "Propulsion Control",
        "subsystems": {
            "Torque Delivery": ["torque demand", "throttle mapping", "power limit"],
            "Transmission Management": ["gear shift", "gear ratio"]
        }
    },
    "Communication": {
        "keywords": ["can", "can-fd", "ethernet", "bus", "telematics", "lin", "heartbeat", "message", "packet", "latency", "bandwidth"],
        "default_subsystem": "In-Vehicle Networking",
        "subsystems": {
            "CAN Gateway": ["can", "message translation", "arbitration", "heartbeat"],
            "Telematics": ["cellular", "gps", "edr", "cloud", "remote"]
        }
    },
    "Diagnostics": {
        "keywords": ["dtc", "diagnostic", "fault code", "fail-safe", "recovery", "edr", "uds", "limp-home"],
        "default_subsystem": "On-Board Diagnostics",
        "subsystems": {
            "Fault Memory": ["dtc", "diagnostic trouble code", "freeze frame"],
            "Event Data Recorder": ["edr", "crash buffer", "non-volatile"]
        }
    }
}

# ASIL / Safety relevance patterns
ASIL_PATTERNS = [
    (re.compile(r'\bASIL[- ]?D\b', re.IGNORECASE), "ASIL-D"),
    (re.compile(r'\bASIL[- ]?C\b', re.IGNORECASE), "ASIL-C"),
    (re.compile(r'\bASIL[- ]?B\b', re.IGNORECASE), "ASIL-B"),
    (re.compile(r'\bASIL[- ]?A\b', re.IGNORECASE), "ASIL-A"),
    (re.compile(r'\bQM\b', re.IGNORECASE), "QM"),
    (re.compile(r'\b(safety[- ]critical|catastrophic|fail[- ]safe)\b', re.IGNORECASE), "ASIL-D"),
]

# Explicit timing patterns: "within 100 ms", "<= 40 ms", "in 500 milliseconds", "cycle time of 20 ms"
TIMING_PATTERN = re.compile(
    r'(?:within|<=|<|>=|>|latency\s*<=?|in|cycle(?: time)?(?: of)?)\s*(\d+(?:\.\d+)?\s*(?:ms|milliseconds?|s|seconds?|min|minutes?))\b',
    re.IGNORECASE
)

# Explicit numerical threshold patterns with units
THRESHOLD_PATTERNS = [
    re.compile(r'(\d+(?:\.\d+)?\s*(?:m/s2|m/s\^2|bar|psi|km/h|deg/s|%|m\b|meters?|bar/s|g\b))', re.IGNORECASE),
    re.compile(r'(?:below|exceeds?|exceeding|above|at least|greater than|less than)\s*(\d+(?:\.\d+)?\s*[a-zA-Z/%^2]+)', re.IGNORECASE)
]

# Explicit condition patterns
CONDITION_PATTERN = re.compile(
    r'\b(?:when|if|upon|in case of|provided that|on condition that)\s+([^,\.;]+)',
    re.IGNORECASE
)

# Known inputs/sensors
KNOWN_INPUTS = [
    ("wheel-speed sensor", ["wheel speed", "wheel-speed", "wss"]),
    ("brake pedal sensor", ["brake pedal", "pedal travel", "pedal velocity"]),
    ("master cylinder pressure sensor", ["master cylinder", "brake pressure"]),
    ("radar sensor", ["radar", "77ghz"]),
    ("camera sensor", ["camera", "optical", "vision"]),
    ("imu sensor", ["imu", "yaw rate sensor", "accelerometer"]),
    ("steering angle sensor", ["steering angle", "steering column"]),
    ("tyre pressure sensor", ["tyre pressure sensor", "tpms sensor", "tire pressure sensor"]),
    ("rain sensor", ["rain sensor", "wiper sensor"]),
]

# Known outputs/actuators
KNOWN_OUTPUTS = [
    ("brake actuator", ["hydraulic brake", "caliper pressure", "apply brake", "deceleration", "aeb"]),
    ("collision warning buzzer", ["warning buzzer", "audible alert", "chime", "hmi alert"]),
    ("cluster display warning", ["visual warning", "tell-tale", "cluster warning", "icon"]),
    ("throttle cut", ["torque reduction", "throttle reduction", "engine cut"]),
    ("hazard lights", ["hazard lamps", "emergency flasher"]),
    ("dtc logging", ["set dtc", "store fault", "log diagnostic", "lock buffer"]),
    ("sensor failure detection", ["detect wheel-speed sensor failure", "detect sensor failure", "issue warning"]),
]

class DetectedRequirement:
    def __init__(
        self,
        req_code: str,
        original_text: str,
        system: Optional[str] = None,
        subsystem: Optional[str] = None,
        ecu_id: Optional[str] = None,
        inputs: List[str] = None,
        outputs: List[str] = None,
        conditions: List[str] = None,
        threshold: Optional[str] = None,
        timing_constraint: Optional[str] = None,
        dependencies: List[str] = None,
        safety_relevance: str = "QM",
        completeness_status: str = "COMPLETE",
        source_traceability: Dict[str, Any] = None,
        specification_gaps: List[Dict[str, Any]] = None,
        is_duplicate: bool = False
    ):
        self.req_code = req_code
        self.original_text = original_text
        self.system = system
        self.subsystem = subsystem
        self.ecu_id = ecu_id
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.conditions = conditions or []
        self.threshold = threshold
        self.timing_constraint = timing_constraint
        self.dependencies = dependencies or []
        self.safety_relevance = safety_relevance
        self.completeness_status = completeness_status
        self.source_traceability = source_traceability or {}
        self.specification_gaps = specification_gaps or []
        self.is_duplicate = is_duplicate

def parse_requirement_id(text: str) -> Tuple[Optional[str], str]:
    """
    Checks if text starts with an explicit requirement ID.
    Returns (req_id, remaining_text).
    """
    match = REQ_ID_PATTERN.match(text)
    if match:
        full_match = match.group(0)
        req_id = match.group(1).upper()
        # Clean remaining text
        remaining = text[len(full_match):].strip()
        return req_id, remaining
    return None, text

def determine_system_and_subsystem(text: str) -> Tuple[str, Optional[str]]:
    """
    Deterministically maps text to system and subsystem using controlled taxonomy.
    """
    lower = text.lower()
    best_system = "General"
    best_subsystem = None
    max_matches = 0

    for system_name, data in SYSTEM_TAXONOMY.items():
        matches = sum(1 for kw in data["keywords"] if kw in lower)
        if matches > max_matches:
            max_matches = matches
            best_system = system_name
            best_subsystem = data["default_subsystem"]
            for sub_name, sub_kws in data["subsystems"].items():
                if any(skw in lower for skw in sub_kws):
                    best_subsystem = sub_name
                    break

    return best_system, best_subsystem

def determine_safety_relevance(text: str, system: str) -> str:
    """
    Extracts ASIL level from explicit text or automotive safety taxonomy defaults.
    """
    for pattern, asil in ASIL_PATTERNS:
        if pattern.search(text):
            return asil

    # Deterministic default based on system domain
    if system in ("Braking", "ADAS"):
        return "ASIL-D"
    elif system in ("Dynamics", "Powertrain"):
        return "ASIL-C"
    elif system in ("TPMS", "Communication"):
        return "ASIL-B"
    return "QM"

def extract_deterministic_fields(
    text: str,
    system: str,
    subsystem: Optional[str]
) -> Tuple[List[str], List[str], List[str], Optional[str], Optional[str]]:
    """
    Extracts inputs, outputs, conditions, threshold, and timing using regex/vocabularies.
    Does NOT invent missing values.
    """
    lower = text.lower()

    # Inputs
    inputs: List[str] = []
    for std_name, aliases in KNOWN_INPUTS:
        if any(alias in lower for alias in aliases):
            inputs.append(std_name)

    # Outputs
    outputs: List[str] = []
    for std_name, aliases in KNOWN_OUTPUTS:
        if any(alias in lower for alias in aliases):
            outputs.append(std_name)

    # Conditions
    conditions: List[str] = []
    for match in CONDITION_PATTERN.finditer(text):
        c_text = match.group(1).strip()
        # Clean trailing punctuation
        c_text = re.sub(r'[\.,;]+$', '', c_text)
        if len(c_text) > 3 and c_text not in conditions:
            conditions.append(c_text)

    # Timing
    timing_match = TIMING_PATTERN.search(text)
    timing_constraint = timing_match.group(1).strip() if timing_match else None

    # Threshold
    threshold = None
    for pattern in THRESHOLD_PATTERNS:
        thresh_match = pattern.search(text)
        if thresh_match:
            # Check it's not simply the timing value
            val = thresh_match.group(1).strip()
            if not any(u in val.lower() for u in ['ms', 'sec', 'min', 's']):
                threshold = val
                break

    return inputs, outputs, conditions, threshold, timing_constraint

def analyze_specification_gaps(
    req_code: str,
    original_text: str,
    system: str,
    subsystem: Optional[str],
    threshold: Optional[str],
    timing_constraint: Optional[str],
    safety_relevance: str
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Runs deterministic gap analysis on the requirement.
    Returns (completeness_status, list_of_gaps).
    """
    gaps: List[Dict[str, Any]] = []
    lower = original_text.lower()

    # Rule 1: Safety critical systems (ASIL C/D or Braking/ADAS) missing timing
    requires_timing = (
        safety_relevance in ("ASIL-C", "ASIL-D") or
        system in ("Braking", "ADAS") or
        any(k in lower for k in ["within", "latency", "reaction", "detect", "respond", "mitigate", "brake", "warn"])
    )
    if requires_timing and not timing_constraint:
        gaps.append({
            "gap_type": "MISSING_TIMEOUT",
            "severity": "HIGH" if safety_relevance == "ASIL-D" else "MEDIUM",
            "description": f"Requirement '{req_code}' specifies an action/detection but omits the required response time or timeout constraint.",
            "missing_parameter": "reaction_latency_ms",
            "suggested_action": "Engineering review required to define an explicit maximum latency/timeout before software sign-off."
        })

    # Rule 2: Physical action/metric lacking threshold
    requires_threshold = any(k in lower for k in [
        "pressure", "speed", "deceleration", "slip", "temperature", "distance",
        "threshold", "maintain", "exceeds", "reduce", "stop within", "low", "high"
    ])
    if requires_threshold and not threshold:
        gaps.append({
            "gap_type": "MISSING_THRESHOLD",
            "severity": "HIGH" if safety_relevance in ("ASIL-C", "ASIL-D") else "MEDIUM",
            "description": f"Requirement '{req_code}' references dynamic thresholds or operating parameters without defining an exact numerical limit.",
            "missing_parameter": "activation_threshold",
            "suggested_action": "Specify precise engineering acceptance threshold with physical units (e.g., bar, km/h, m/s2)."
        })

    # Rule 3: High-level ambiguous statements
    is_ambiguous = any(phrase in lower for phrase in [
        "maintain vehicle stability", "appropriate action", "as soon as possible",
        "when necessary", "safe manner", "optimal performance"
    ])
    if is_ambiguous:
        gaps.append({
            "gap_type": "AMBIGUOUS_BOUNDARY",
            "severity": "MEDIUM",
            "description": f"Requirement '{req_code}' contains ambiguous qualitative terms without testable boundaries.",
            "missing_parameter": "operational_boundary",
            "suggested_action": "Replace ambiguous phrasing with measurable pass/fail engineering criteria."
        })

    completeness_status = "INCOMPLETE" if gaps else "COMPLETE"
    return completeness_status, gaps

def normalize_units_into_requirements(
    document_units: List[DocumentUnit],
    source_filename: str,
    existing_req_codes: set
) -> List[DetectedRequirement]:
    """
    Takes document units, detects explicit IDs or assigns deterministic TMP-REQ-XXX IDs,
    normalizes all fields, checks for duplicates, and computes specification gaps.
    """
    detected: List[DetectedRequirement] = []
    seen_in_document: set = set()
    tmp_counter = 1

    for unit in document_units:
        text = unit.text.strip()
        # Filter out very short or empty lines
        if len(text) < 15:
            continue

        explicit_id, req_body = parse_requirement_id(text)
        if explicit_id:
            req_code = explicit_id
            # Clean original text
            full_text = text
        else:
            # Check if this text reads like a requirement ("shall", "must", "will", "should", "detect", "trigger")
            lower_body = text.lower()
            if not any(req_kw in lower_body for req_kw in ["shall", "must", "required", "detect", "trigger", "monitor", "transmit", "prevent"]):
                continue

            req_code = f"TMP-REQ-{tmp_counter:03d}"
            tmp_counter += 1
            full_text = text

        # Check duplicate
        is_duplicate = False
        duplicate_reason = None
        if req_code in seen_in_document:
            is_duplicate = True
            duplicate_reason = f"Duplicate requirement ID '{req_code}' found within the same document."
        elif req_code in existing_req_codes:
            is_duplicate = True
            duplicate_reason = f"Requirement ID '{req_code}' conflicts with an existing database requirement."

        seen_in_document.add(req_code)

        # Determine taxonomy
        system, subsystem = determine_system_and_subsystem(full_text)
        safety_relevance = determine_safety_relevance(full_text, system)

        # Field extraction (deterministic, no hallucination)
        inputs, outputs, conditions, threshold, timing_constraint = extract_deterministic_fields(
            full_text, system, subsystem
        )

        # Specification gap analysis
        completeness_status, gaps = analyze_specification_gaps(
            req_code=req_code,
            original_text=full_text,
            system=system,
            subsystem=subsystem,
            threshold=threshold,
            timing_constraint=timing_constraint,
            safety_relevance=safety_relevance
        )

        traceability = {
            "source_document": source_filename,
            "source_page": unit.page,
            "source_section": unit.section,
            "source_location": unit.location
        }

        if is_duplicate and duplicate_reason:
            gaps.append({
                "gap_type": "CONFLICTING_REQUIREMENT",
                "severity": "HIGH",
                "description": duplicate_reason,
                "missing_parameter": "unique_requirement_identifier",
                "suggested_action": "Engineer must review and assign a distinct requirement code."
            })
            completeness_status = "AMBIGUOUS"

        detected.append(DetectedRequirement(
            req_code=req_code,
            original_text=full_text,
            system=system,
            subsystem=subsystem,
            ecu_id=None,
            inputs=inputs,
            outputs=outputs,
            conditions=conditions,
            threshold=threshold,
            timing_constraint=timing_constraint,
            dependencies=[],
            safety_relevance=safety_relevance,
            completeness_status=completeness_status,
            source_traceability=traceability,
            specification_gaps=gaps,
            is_duplicate=is_duplicate
        ))

    return detected
