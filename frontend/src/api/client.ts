// CIVIC-AI API Client

export interface DashboardStats {
  vehicle_name: string;
  vehicle_class: string;
  sw_version: string;
  requirements_count: number;
  test_cases_count: number;
  validated_tests_count: number;
  blocked_tests_count: number;
  specification_gaps_count: number;
  ecus_count: number;
  scenario_categories_count: number;
  coverage: {
    requirement_coverage_pct: number;
    ecu_coverage_pct: number;
    scenario_coverage_pct: number;
    fault_coverage_pct: number;
    boundary_coverage_pct: number;
  };
  recent_jobs: Array<{
    id: string;
    requirement_code: string;
    scenario_name: string;
    tests_generated: number;
    status: string;
    timestamp: string;
  }>;
}

export interface ECUItem {
  id: string;
  name: string;
  subsystem: string;
  domain: string;
  description: string;
  bus_type: string;
  safety_integrity_level: string;
  sensors: Array<{ id: string; name: string; type: string }>;
  actuators: Array<{ id: string; name: string; type: string }>;
  signals_produced: Array<{ id: string; name: string; cycle_ms: number }>;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  domain?: string;
  subsystem?: string;
  extra?: any;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
}

export interface ArchitectureGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface RequirementItem {
  id: string;
  req_code: string;
  vehicle_id: string;
  ecu_id?: string;
  ecu_name: string;
  system: string;
  subsystem?: string;
  original_text: string;
  normalized_summary?: string;
  inputs: string[];
  outputs: string[];
  conditions: string[];
  threshold?: string;
  timing_constraint?: string;
  dependencies: string[];
  safety_relevance: string;
  completeness_status: string;
  gaps: Array<{
    id: string;
    gap_type: string;
    severity: string;
    description: string;
    missing_parameter?: string;
    suggested_action?: string;
    status: string;
  }>;
  test_count: number;
}

export interface ScenarioItem {
  id: string;
  code: string;
  category: string;
  name: string;
  description: string;
  pune_context?: string;
  road_friction: number;
  visibility_reduction_pct: number;
  traffic_density: string;
  parameters: Record<string, any>;
}

export interface TestCaseItem {
  id: string;
  code: string;
  title: string;
  category: string;
  priority: string;
  requirement_ids: string[];
  ecu_under_test: string[];
  dependencies: string[];
  preconditions: string[];
  scenario: string;
  input_signals: Array<{ signal: string; value: any; unit: string }>;
  steps: string[];
  expected_results: string[];
  fault_injection: string[];
  recovery_conditions: string[];
  pass_fail_criteria: string;
  safety_notes?: string;
  confidence: number;
  assumptions: string[];
  specification_gaps: string[];
  is_ai_generated: boolean;
  status: string;
  latest_result?: {
    id: string;
    test_case_id: string;
    status: string;
    blocked_reason?: string;
    simulation_duration_ms: number;
    telemetry_data: Array<{ time_ms: number; ego_speed: number; brake_pressure: number; state: string }>;
    log_trace: string[];
  };
}

export interface SpecificationGapItem {
  id: string;
  requirement_id: string;
  requirement_code: string;
  requirement_text: string;
  gap_type: string;
  severity: string;
  description: string;
  missing_parameter?: string;
  affected_ecu_id?: string;
  affected_ecu_name: string;
  affected_functions: string[];
  suggested_action?: string;
  status: string;
  created_at: string;
}

export interface CoverageData {
  summary: {
    requirement_coverage_pct: number;
    ecu_coverage_pct: number;
    scenario_coverage_pct: number;
    fault_coverage_pct: number;
    boundary_coverage_pct: number;
    total_requirements: number;
    total_test_cases: number;
    total_specification_gaps: number;
  };
  by_system: Array<{
    system: string;
    total_requirements: number;
    covered_requirements: number;
    coverage_pct: number;
  }>;
  by_ecu: Array<{
    ecu_id: string;
    ecu_name: string;
    domain: string;
    subsystem: string;
    test_count: number;
    status: string;
  }>;
  test_categories: Record<string, number>;
  completeness_distribution: Record<string, number>;
}

const API_BASE = '/api/v1';

export const api = {
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    if (!res.ok) throw new Error('Failed to fetch dashboard stats');
    return res.json();
  },

  async getArchitectureGraph(): Promise<ArchitectureGraph> {
    const res = await fetch(`${API_BASE}/architecture/graph`);
    if (!res.ok) throw new Error('Failed to fetch architecture graph');
    return res.json();
  },

  async getECUs(): Promise<ECUItem[]> {
    const res = await fetch(`${API_BASE}/architecture/ecus`);
    if (!res.ok) throw new Error('Failed to fetch ECUs');
    return res.json();
  },

  async getRequirements(filters?: { system?: string; status?: string; search?: string }): Promise<RequirementItem[]> {
    const params = new URLSearchParams();
    if (filters?.system) params.append('system', filters.system);
    if (filters?.status) params.append('completeness_status', filters.status);
    if (filters?.search) params.append('search', filters.search);
    const res = await fetch(`${API_BASE}/requirements/?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch requirements');
    return res.json();
  },

  async getRequirementDetail(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/requirements/${id}`);
    if (!res.ok) throw new Error('Failed to fetch requirement detail');
    return res.json();
  },

  async getScenarios(category?: string): Promise<ScenarioItem[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    const res = await fetch(`${API_BASE}/scenarios/?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch scenarios');
    return res.json();
  },

  async getTestCases(filters?: { ecu?: string; category?: string; status?: string; search?: string }): Promise<TestCaseItem[]> {
    const params = new URLSearchParams();
    if (filters?.ecu) params.append('ecu', filters.ecu);
    if (filters?.category) params.append('category', filters.category);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.search) params.append('search', filters.search);
    const res = await fetch(`${API_BASE}/tests/?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch test cases');
    return res.json();
  },

  async getTestCaseDetail(id: string): Promise<TestCaseItem> {
    const res = await fetch(`${API_BASE}/tests/${id}`);
    if (!res.ok) throw new Error('Failed to fetch test case detail');
    return res.json();
  },

  async getGaps(filters?: { severity?: string }): Promise<SpecificationGapItem[]> {
    const params = new URLSearchParams();
    if (filters?.severity) params.append('severity', filters.severity);
    const res = await fetch(`${API_BASE}/gaps/?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch gaps');
    return res.json();
  },

  async getCoverage(): Promise<CoverageData> {
    const res = await fetch(`${API_BASE}/coverage/`);
    if (!res.ok) throw new Error('Failed to fetch coverage');
    return res.json();
  },

  async runSimulation(testCaseId: string, overrides?: Record<string, any>): Promise<any> {
    const res = await fetch(`${API_BASE}/simulation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ test_case_id: testCaseId, overrides })
    });
    if (!res.ok) throw new Error('Failed to run simulation');
    return res.json();
  }
};
