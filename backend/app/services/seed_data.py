import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle, ECU, Sensor, Actuator, Signal
from app.models.requirement import Requirement, SpecificationGap
from app.models.scenario import Scenario
from app.models.test_case import TestCase, TestResult
from app.models.job import GenerationJob

def seed_database(db: Session):
    # Check if already seeded
    if db.query(Vehicle).first():
        return

    # 1. Reference Vehicle PUSV-01
    pusv = Vehicle(
        id="veh_pusv01",
        name="PUSV-01",
        full_name="Pune Urban Safety Vehicle",
        vehicle_class="Compact Sedan",
        reference_model="Modern C-segment Compact Sedan (Reference Architecture)",
        sw_version="PUSV-SW-0.1",
        description="Fictional engineering reference vehicle platform for real-world Indian operational design domain software validation.",
        created_at=datetime.utcnow()
    )
    db.add(pusv)
    db.flush()

    # 2. 8 Logical ECUs
    ecus_data = [
        ("ecu_adas", "ADAS_ECU", "Active Safety", "Chassis / Safety", "Perception fusion, forward collision warning, automatic emergency braking, lane keep assistance.", "CAN-FD / Ethernet", "ASIL-D"),
        ("ecu_brake", "BRAKE_ECU", "Brake Control", "Chassis / Braking", "Electro-hydraulic brake booster control, ABS modulation, electronic brakeforce distribution.", "CAN-FD", "ASIL-D"),
        ("ecu_dynamics", "VEHICLE_DYNAMICS_ECU", "Vehicle Dynamics", "Chassis / Dynamics", "Electronic stability control, traction control system, yaw moment and sideslip control.", "CAN-FD", "ASIL-D"),
        ("ecu_tpms", "TPMS_ECU", "Tyre Monitoring", "Body / Safety", "Direct tyre pressure and temperature monitoring across 4 wheel locations, rapid deflation warning.", "CAN", "ASIL-B"),
        ("ecu_powertrain", "POWERTRAIN_ECU", "Propulsion", "Propulsion", "Engine/motor management, drive-by-wire torque arbitration, transmission gear scheduling.", "CAN-FD", "ASIL-C"),
        ("ecu_body", "BODY_ECU", "Body Electronics", "Body Electronics", "Lighting management, rain-sensing wipers, door/window access, interior alert buzzers.", "CAN / LIN", "ASIL-B"),
        ("ecu_gateway", "GATEWAY_ECU", "Central Gateway", "Networking", "Central communications router, message translation, firewall, diagnostic routing.", "Ethernet / CAN-FD", "ASIL-B"),
        ("ecu_telematics", "TELEMATICS_ECU", "Connectivity", "Telematics", "GPS/GNSS localization, cellular 4G/5G telemetry, event data recorder (EDR) logging.", "Ethernet / CAN", "QM")
    ]
    for eid, name, subs, dom, desc, bus, asil in ecus_data:
        db.add(ECU(
            id=eid, vehicle_id=pusv.id, name=name, subsystem=subs,
            domain=dom, description=desc, bus_type=bus, safety_integrity_level=asil
        ))
    db.flush()

    # 3. Sensors & Actuators
    sensors_data = [
        ("sens_front_radar", "ecu_adas", "77GHz Front Long-Range Radar", "RADAR", 20.0, 0.5, 200.0, "m", ["blindness", "misalignment", "multipath_clutter"]),
        ("sens_front_camera", "ecu_adas", "Front Wide-Angle Perception Camera", "CAMERA", 30.0, 0.2, 150.0, "m", ["optical_occlusion", "heavy_glare", "water_spray_blur"]),
        ("sens_driver_monitor", "ecu_adas", "Infrared Driver Monitoring Camera", "CAMERA", 15.0, 0.1, 1.5, "m", ["driver_gaze_loss", "infrared_shadow"]),
        ("sens_ws_fl", "ecu_brake", "Front-Left Wheel Speed Sensor", "HALL_EFFECT", 100.0, 0.0, 300.0, "km/h", ["air_gap_fault", "harness_disconnect", "signal_jitter"]),
        ("sens_ws_fr", "ecu_brake", "Front-Right Wheel Speed Sensor", "HALL_EFFECT", 100.0, 0.0, 300.0, "km/h", ["air_gap_fault", "harness_disconnect", "signal_jitter"]),
        ("sens_ws_rl", "ecu_brake", "Rear-Left Wheel Speed Sensor", "HALL_EFFECT", 100.0, 0.0, 300.0, "km/h", ["air_gap_fault", "harness_disconnect", "signal_jitter"]),
        ("sens_ws_rr", "ecu_brake", "Rear-Right Wheel Speed Sensor", "HALL_EFFECT", 100.0, 0.0, 300.0, "km/h", ["air_gap_fault", "harness_disconnect", "signal_jitter"]),
        ("sens_brake_press", "ecu_brake", "Master Cylinder Hydraulic Pressure Sensor", "PIEZORESISTIVE", 100.0, 0.0, 200.0, "bar", ["zero_drift", "clogged_port"]),
        ("sens_imu", "ecu_dynamics", "6-Axis Chassis Inertial Measurement Unit", "IMU", 100.0, -50.0, 50.0, "m/s2", ["bias_drift", "resonance_clipping"]),
        ("sens_steer_angle", "ecu_dynamics", "Steering Column Angle Sensor", "OPTICAL_ENCODER", 50.0, -720.0, 720.0, "deg", ["calib_loss", "dropped_ticks"]),
        ("sens_tpms_fl", "ecu_tpms", "Front-Left Tyre Pressure/Temp Sensor", "DIRECT_TPMS", 0.5, 0.0, 5.0, "bar", ["battery_depletion", "rf_interference"]),
        ("sens_tpms_fr", "ecu_tpms", "Front-Right Tyre Pressure/Temp Sensor", "DIRECT_TPMS", 0.5, 0.0, 5.0, "bar", ["battery_depletion", "rf_interference"]),
        ("sens_tpms_rl", "ecu_tpms", "Rear-Left Tyre Pressure/Temp Sensor", "DIRECT_TPMS", 0.5, 0.0, 5.0, "bar", ["battery_depletion", "rf_interference"]),
        ("sens_tpms_rr", "ecu_tpms", "Rear-Right Tyre Pressure/Temp Sensor", "DIRECT_TPMS", 0.5, 0.0, 5.0, "bar", ["battery_depletion", "rf_interference"]),
        ("sens_rain_light", "ecu_body", "Optical Rain and Ambient Light Sensor", "OPTICAL", 10.0, 0.0, 100.0, "%", ["lens_scratch", "dirt_cover"])
    ]
    for sid, eid, sname, stype, rate, rmin, rmax, unit, fmodes in sensors_data:
        s = Sensor(
            id=sid, ecu_id=eid, name=sname, sensor_type=stype,
            sampling_rate_hz=rate, range_min=rmin, range_max=rmax, unit=unit
        )
        s.failure_modes = fmodes
        db.add(s)

    actuators_data = [
        ("act_brake_mod", "ecu_brake", "Electro-Hydraulic Brake Pressure Modulator", "HYDRAULIC_VALVE", 80.0, "160 bar"),
        ("act_steering_assist", "ecu_dynamics", "Electric Power Steering Torque Actuator", "SERVO_MOTOR", 30.0, "12 Nm"),
        ("act_throttle", "ecu_powertrain", "Electronic Throttle Body Actuator", "STEPPER_MOTOR", 40.0, "100%"),
        ("act_cluster_chime", "ecu_body", "Instrument Cluster Alert Chime & Display", "HMI", 10.0, "90 dB")
    ]
    for aid, eid, aname, atype, rtime, mout in actuators_data:
        db.add(Actuator(
            id=aid, ecu_id=eid, name=aname, actuator_type=atype,
            response_time_ms=rtime, max_output=mout
        ))
    db.flush()

    # 4. Canonical CAN/CAN-FD Signals
    signals_data = [
        ("sig_veh_spd", "Vehicle_Speed", "ecu_brake", ["ecu_adas", "ecu_dynamics", "ecu_powertrain", "ecu_telematics"], "FLOAT", "km/h", 0.0, 260.0, 10, "0.0"),
        ("sig_col_risk", "Collision_Risk_Index", "ecu_adas", ["ecu_brake", "ecu_body", "ecu_telematics"], "FLOAT", "%", 0.0, 100.0, 20, "0.0"),
        ("sig_aeb_req", "AEB_Request", "ecu_adas", ["ecu_brake", "ecu_telematics"], "ENUM", "", 0.0, 3.0, 20, "0"), # 0=NONE, 1=PARTIAL, 2=FULL, 3=HOLD
        ("sig_fcw_warn", "FCW_Warning_State", "ecu_adas", ["ecu_body", "ecu_telematics"], "ENUM", "", 0.0, 2.0, 20, "0"),
        ("sig_target_dist", "Lead_Object_Distance", "ecu_adas", ["ecu_brake"], "FLOAT", "m", 0.0, 200.0, 20, "200.0"),
        ("sig_rel_spd", "Lead_Object_Rel_Speed", "ecu_adas", ["ecu_brake"], "FLOAT", "m/s", -80.0, 80.0, 20, "0.0"),
        ("sig_brk_press_act", "Brake_Pressure_Actual", "ecu_brake", ["ecu_adas", "ecu_dynamics"], "FLOAT", "bar", 0.0, 180.0, 10, "0.0"),
        ("sig_brk_press_dem", "Brake_Pressure_Demand", "ecu_brake", ["ecu_dynamics"], "FLOAT", "bar", 0.0, 180.0, 10, "0.0"),
        ("sig_abs_active", "ABS_Active_State", "ecu_brake", ["ecu_dynamics", "ecu_telematics"], "BOOLEAN", "", 0.0, 1.0, 10, "0"),
        ("sig_yaw_rate", "Yaw_Rate_Actual", "ecu_dynamics", ["ecu_adas", "ecu_brake"], "FLOAT", "deg/s", -120.0, 120.0, 10, "0.0"),
        ("sig_lat_accel", "Lateral_Acceleration", "ecu_dynamics", ["ecu_adas", "ecu_brake"], "FLOAT", "m/s2", -25.0, 25.0, 10, "0.0"),
        ("sig_vert_accel", "Vertical_Acceleration_Shock", "ecu_dynamics", ["ecu_telematics"], "FLOAT", "m/s2", -40.0, 40.0, 10, "0.0"),
        ("sig_tpms_state", "TPMS_Warning_Level", "ecu_tpms", ["ecu_body", "ecu_telematics", "ecu_dynamics"], "ENUM", "", 0.0, 3.0, 100, "0"),
        ("sig_tpms_p_fr", "Tyre_Pressure_FR", "ecu_tpms", ["ecu_telematics"], "FLOAT", "bar", 0.0, 5.0, 500, "2.3"),
        ("sig_pothole_flag", "Pothole_Event_Flag", "ecu_dynamics", ["ecu_telematics", "ecu_adas"], "BOOLEAN", "", 0.0, 1.0, 50, "0"),
        ("sig_can_hb_adas", "Heartbeat_ADAS", "ecu_adas", ["ecu_gateway", "ecu_brake"], "INTEGER", "counter", 0.0, 255.0, 20, "0"),
        ("sig_can_hb_brake", "Heartbeat_Brake", "ecu_brake", ["ecu_gateway", "ecu_adas"], "INTEGER", "counter", 0.0, 255.0, 20, "0")
    ]
    for sid, sname, src, cons, stype, unit, minv, maxv, cyc, dval in signals_data:
        sig = Signal(
            id=sid, name=sname, source_ecu_id=src, signal_type=stype,
            unit=unit, min_value=minv, max_value=maxv, cycle_time_ms=cyc, default_value=dval
        )
        sig.consumer_ecu_ids = cons
        db.add(sig)
    db.flush()

    # 5. 40 Requirements with intentional specification gaps
    # Format: (id, code, system, subsystem, ecu_id, original_text, threshold, timing, asil, status, inputs, outputs, conditions, deps, gaps)
    reqs_data = [
        # Braking requirements (15)
        ("req_brk_001", "BRK-REQ-001", "Braking", "Emergency Braking", "ecu_brake",
         "The brake system shall achieve a peak deceleration of at least 8.5 m/s2 when maximum brake pressure demand is received on dry asphalt.",
         "8.5 m/s2", "Onset <= 150 ms", "ASIL-D", "COMPLETE",
         ["Brake_Pressure_Demand", "Vehicle_Speed"], ["Brake_Pressure_Actual"], ["Road_Friction >= 0.80"], ["BRAKE_ECU"], []),

        ("req_brk_002", "BRK-REQ-002", "Braking", "ABS Modulation", "ecu_brake",
         "When individual wheel slip ratio exceeds 18%, ABS modulation shall reduce hydraulic brake caliper pressure to restore wheel rotation within 40 ms.",
         "18% slip", "Modulation cycle <= 40 ms", "ASIL-D", "COMPLETE",
         ["Wheel_Speed_FL", "Wheel_Speed_FR", "Vehicle_Speed"], ["Brake_Pressure_Actual", "ABS_Active_State"], ["Wheel_Slip > 0.18"], ["BRAKE_ECU"], []),

        ("req_brk_003", "BRK-REQ-003", "Braking", "Electronic Brakeforce Distribution", "ecu_brake",
         "The system shall dynamically adjust front-to-rear hydraulic pressure proportioning based on dynamic axle load estimation to prevent rear wheel premature lockup.",
         "Rear slip <= Front slip - 2%", "Update every 10 ms", "ASIL-D", "COMPLETE",
         ["Lateral_Acceleration", "Vehicle_Speed", "Brake_Pressure_Actual"], ["Brake_Pressure_Demand"], ["Braking_Active"], ["BRAKE_ECU"], []),

        ("req_brk_004", "BRK-REQ-004", "Braking", "Brake Assist", "ecu_brake",
         "If the driver applies brake pedal with velocity exceeding 250 bar/s, hydraulic boost assist shall amplify line pressure to maximum available pressure.",
         "250 bar/s pedal rate", "Latency <= 60 ms", "ASIL-C", "COMPLETE",
         ["Brake_Pressure_Actual"], ["Brake_Pressure_Demand"], ["Pedal_Rate > 250"], ["BRAKE_ECU"], []),

        ("req_brk_005", "BRK-REQ-005", "Braking", "Deceleration Degradation on Wet Surface", "ecu_brake",
         "On low friction surfaces (friction coefficient <= 0.45), the ABS system shall adapt pulse frequencies to maintain directional stability while maximizing deceleration.",
         "Stability slip target 12-15%", "Adaptation <= 80 ms", "ASIL-D", "COMPLETE",
         ["Wheel_Speed_FL", "Yaw_Rate_Actual"], ["ABS_Active_State"], ["Friction <= 0.45"], ["BRAKE_ECU", "VEHICLE_DYNAMICS_ECU"], []),

        ("req_brk_006", "BRK-REQ-006", "Braking", "Brake Temperature Fade Warning", "ecu_brake",
         "When estimated rotor surface temperature exceeds 450 deg C, the brake controller shall signal thermal fade compensation and transmit warning lamp request.",
         "450 deg C", "Signal period 100 ms", "ASIL-B", "COMPLETE",
         ["Brake_Energy_Accumulator"], ["Brake_Thermal_Fade_Alert"], ["Temp > 450"], ["BRAKE_ECU", "BODY_ECU"], []),

        ("req_brk_007", "BRK-REQ-007", "Braking", "Hydraulic Pressure Sensor Fault", "ecu_brake",
         "If the master cylinder pressure sensor output deviates outside 0.2V to 4.8V electrical range, the system shall transition to backup open-loop pressure estimation.",
         "0.2V - 4.8V", "Fault latch <= 20 ms", "ASIL-D", "COMPLETE",
         ["Master_Cylinder_Voltage"], ["Brake_System_Degraded_Flag"], ["Voltage_Out_Of_Range"], ["BRAKE_ECU"], []),

        ("req_brk_008", "BRK-REQ-008", "Braking", "Simultaneous Cornering and Braking", "ecu_brake",
         "During emergency braking while cornering (yaw rate > 15 deg/s), brake pressure to inner wheels shall be regulated to mitigate vehicle spin.",
         "Yaw deviation <= 3 deg/s", "Loop rate 10 ms", "ASIL-D", "COMPLETE",
         ["Yaw_Rate_Actual", "Steering_Angle", "Brake_Pressure_Demand"], ["Brake_Pressure_Actual"], ["Yaw_Rate > 15 deg/s"], ["BRAKE_ECU", "VEHICLE_DYNAMICS_ECU"], []),

        ("req_brk_009", "BRK-REQ-009", "Braking", "Post-Impact Braking", "ecu_brake",
         "Upon receiving severe crash deceleration trigger from Airbag ECU, the brake system shall command full 100 bar pressure until vehicle standstill.",
         "Full 100 bar", "Trigger <= 30 ms", "ASIL-D", "COMPLETE",
         ["Crash_Event_Signal"], ["Brake_Pressure_Demand"], ["Crash_Verified"], ["BRAKE_ECU", "BODY_ECU"], []),

        ("req_brk_010", "BRK-REQ-010", "Braking", "Pothole Transient Wheel Slip", "ecu_brake",
         "When a sudden vertical acceleration shock (> 2.5g) coincides with momentary wheel speed drop, ABS shall suppress false wheel-lock intervention for 60 ms.",
         "Vertical shock > 2.5g", "Suppression window 60 ms", "ASIL-C", "COMPLETE",
         ["Vertical_Acceleration_Shock", "Wheel_Speed_FL"], ["ABS_Active_State"], ["Pothole_Shock_Detected"], ["BRAKE_ECU", "VEHICLE_DYNAMICS_ECU"], []),

        ("req_brk_011", "BRK-REQ-011", "Braking", "Brake Line Air Ingestion Warning", "ecu_brake",
         "The system shall detect abnormal pedal compliance indicative of hydraulic air bubbles.",
         None, None, "ASIL-C", "INCOMPLETE",
         ["Brake_Pedal_Travel", "Brake_Pressure_Actual"], ["Service_Brake_Warning"], ["Compliance_Exceeded"], ["BRAKE_ECU"],
         [("GAP-001", "MISSING_THRESHOLD", "HIGH", "Pedal compliance volumetric threshold for air bubble detection is undefined.", "compliance_vol_threshold")]),

        ("req_brk_012", "BRK-REQ-012", "Braking", "Electric Parking Brake Dynamic Deceleration", "ecu_brake",
         "In the event of secondary hydraulic circuit loss, continuous driver actuation of EPB switch shall produce minimum 3.0 m/s2 deceleration.",
         "3.0 m/s2", "Ramp <= 400 ms", "ASIL-C", "COMPLETE",
         ["EPB_Switch_Status"], ["EPB_Actuator_Clamp_Force"], ["Hydraulic_Failure"], ["BRAKE_ECU"], []),

        ("req_brk_013", "BRK-REQ-013", "Braking", "Low Battery Voltage Degradation", "ecu_brake",
         "When supply voltage drops below 9.5V for longer than 500 ms, brake boost pump shall run in energy-saving mode and notify Gateway.",
         "9.5V", "500 ms debounce", "ASIL-B", "COMPLETE",
         ["Battery_Voltage"], ["Brake_Energy_Save_State"], ["Voltage < 9.5V"], ["BRAKE_ECU", "GATEWAY_ECU"], []),

        ("req_brk_014", "BRK-REQ-014", "Braking", "Automatic Emergency Braking Execution", "ecu_brake",
         "If collision risk exceeds configured threshold and the driver does not provide sufficient braking input, the system shall request automatic emergency braking.",
         None, None, "ASIL-D", "INCOMPLETE",
         ["Collision_Risk_Index", "Brake_Pressure_Actual", "Vehicle_Speed"], ["AEB_Request", "Brake_Pressure_Demand"], ["Collision_Risk > Threshold"], ["ADAS_ECU", "BRAKE_ECU"],
         [("GAP-002", "MISSING_THRESHOLD", "CRITICAL", "AEB intervention collision risk index and driver pressure override threshold undefined in BRK-REQ-014.", "collision_risk_threshold")]),

        ("req_brk_015", "BRK-REQ-015", "Braking", "Rapid Brake Pressure Release upon Kick-Down", "ecu_brake",
         "If accelerator pedal is abruptly depressed during partial braking, active braking pressure shall release immediately.",
         None, None, "ASIL-B", "AMBIGUOUS",
         ["Accelerator_Pedal_Position"], ["Brake_Pressure_Demand"], ["Driver_Override"], ["BRAKE_ECU", "POWERTRAIN_ECU"],
         [("GAP-003", "MISSING_TIMEOUT", "MEDIUM", "Maximum allowable latency for active brake release on throttle override is unspecified.", "brake_release_latency")]),

        # ADAS requirements (8)
        ("req_adas_001", "ADAS-REQ-001", "ADAS", "Forward Collision Warning Timing", "ecu_adas",
         "The ADAS ECU shall compute Time-to-Collision (TTC) using fused radar and camera tracking. FCW audible and visual alert shall trigger when TTC <= 2.4 seconds.",
         "TTC <= 2.4 s", "Latency <= 50 ms", "ASIL-B", "COMPLETE",
         ["Lead_Object_Distance", "Lead_Object_Rel_Speed", "Vehicle_Speed"], ["FCW_Warning_State"], ["TTC <= 2.4s"], ["ADAS_ECU", "BODY_ECU"], []),

        ("req_adas_002", "ADAS-REQ-002", "ADAS", "Two-Wheeler Urban Cut-in Detection", "ecu_adas",
         "The perception system shall identify lateral cut-ins by motorcycles or three-wheelers with lateral velocity >= 1.2 m/s and update collision risk within 80 ms.",
         "v_lat >= 1.2 m/s", "Classification <= 80 ms", "ASIL-D", "COMPLETE",
         ["Camera_Object_Bounding_Box", "Radar_Lateral_Velocity"], ["Collision_Risk_Index"], ["Cutin_Detected"], ["ADAS_ECU"], []),

        ("req_adas_003", "ADAS-REQ-003", "ADAS", "Monsoon Heavy Rain Camera Confidence Degradation", "ecu_adas",
         "When optical camera confidence drops due to heavy rain spray, perception fusion shall adjust weightings towards radar.",
         None, None, "ASIL-C", "INCOMPLETE",
         ["Wiper_Speed_State", "Camera_Confidence_Metric", "Radar_Tracking_State"], ["Sensor_Fusion_Confidence"], ["Heavy_Rain"], ["ADAS_ECU"],
         [("GAP-004", "MISSING_THRESHOLD", "HIGH", "Camera confidence score lower cutoff for perception weight shift is undefined.", "camera_confidence_cutoff")]),

        ("req_adas_004", "ADAS-REQ-004", "ADAS", "Pedestrian Crossing Emergency Braking", "ecu_adas",
         "At vehicle speeds between 10 km/h and 60 km/h, if a pedestrian enters ego vehicle projected path with TTC <= 1.4s, full AEB shall be demanded.",
         "10-60 km/h, TTC <= 1.4s", "Demand issue <= 40 ms", "ASIL-D", "COMPLETE",
         ["Camera_Object_Class", "Lead_Object_Distance", "Vehicle_Speed"], ["AEB_Request"], ["Pedestrian_In_Path"], ["ADAS_ECU", "BRAKE_ECU"], []),

        ("req_adas_005", "ADAS-REQ-005", "ADAS", "Lane Departure Warning with Pune Road Markings", "ecu_adas",
         "The system shall alert the driver upon unintentional lane crossing when lane markers are detected with at least 50% contrast.",
         "50% contrast, lateral deviation > 0.3m", "Alert within 100 ms", "ASIL-B", "COMPLETE",
         ["Camera_Lane_Geometry", "Turn_Signal_State"], ["LDW_Alert_State"], ["Departure_Without_Indicator"], ["ADAS_ECU", "BODY_ECU"], []),

        ("req_adas_006", "ADAS-REQ-006", "ADAS", "Traffic Sign Speed Limit Invalidation", "ecu_adas",
         "Traffic sign recognition shall clear recognized school zone speed restrictions after vehicle travels specified distance without re-detection.",
         None, None, "ASIL-A", "INCOMPLETE",
         ["Odometer_Distance", "TSR_Active_Sign"], ["Active_Speed_Limit"], ["No_Redetection"], ["ADAS_ECU"],
         [("GAP-005", "MISSING_THRESHOLD", "LOW", "Distance threshold to expire transient school zone speed limits is unspecified.", "speed_limit_expiry_dist")]),

        ("req_adas_007", "ADAS-REQ-007", "ADAS", "Blind Spot Monitoring Motorcycle Filtering", "ecu_adas",
         "Rear-corner radars shall track two-wheelers moving between lanes at speed differentials up to 30 km/h and illuminate door mirror indicators.",
         "Speed differential <= 30 km/h", "LED illumination <= 80 ms", "ASIL-B", "COMPLETE",
         ["Rear_Radar_Targets", "Turn_Signal_State"], ["BSM_Indicator_State"], ["Target_In_Blind_Zone"], ["ADAS_ECU", "BODY_ECU"], []),

        ("req_adas_008", "ADAS-REQ-008", "ADAS", "Sensor Misalignment Self-Calibration", "ecu_adas",
         "If front radar horizontal misalignment exceeds 2.5 degrees, ADAS shall disable ACC and log DTC.",
         "2.5 degrees deviation", "Detection within 5 km driving", "ASIL-C", "COMPLETE",
         ["Radar_Static_Target_Angles"], ["ADAS_Degraded_Mode_DTC"], ["Misalignment > 2.5 deg"], ["ADAS_ECU"], []),

        # TPMS requirements (5)
        ("req_tpms_001", "TPMS-REQ-001", "TPMS", "Cold Low Pressure Warning", "ecu_tpms",
         "The TPMS ECU shall illuminate the low tyre pressure warning indicator when any tyre pressure falls below 20% of placard pressure (2.3 bar).",
         "Pressure < 1.84 bar (20% loss)", "Broadcast within 15 seconds", "ASIL-B", "COMPLETE",
         ["Tyre_Pressure_FL", "Tyre_Pressure_FR", "Tyre_Pressure_RL", "Tyre_Pressure_RR"], ["TPMS_Warning_Level"], ["Pressure < 1.84 bar"], ["TPMS_ECU", "BODY_ECU"], []),

        ("req_tpms_002", "TPMS-REQ-002", "TPMS", "High Temperature Warning", "ecu_tpms",
         "If tyre cavity temperature exceeds 80 deg C during highway driving, TPMS shall raise Level 2 warning.",
         "80 deg C", "Warning within 5 seconds", "ASIL-B", "COMPLETE",
         ["Tyre_Temp_FR", "Tyre_Pressure_FR"], ["TPMS_Warning_Level"], ["Temp > 80 C"], ["TPMS_ECU"], []),

        ("req_tpms_003", "TPMS-REQ-003", "TPMS", "Dynamic Temperature Pressure Compensation", "ecu_tpms",
         "Tyre pressure readings shall be compensated for thermal expansion using ideal gas approximation.",
         None, None, "QM", "INCOMPLETE",
         ["Tyre_Pressure_FR", "Tyre_Temp_FR"], ["Compensated_Tyre_Pressure"], ["Ambient_Temp_Valid"], ["TPMS_ECU"],
         [("GAP-006", "MISSING_THRESHOLD", "MEDIUM", "Reference calibration temperature baseline is not specified.", "tpms_ref_temp")]),

        ("req_tpms_004", "TPMS-REQ-004", "TPMS", "Puncture Rapid Deflation Warning", "ecu_tpms",
         "In the event of a sudden tyre puncture, the system shall broadcast a critical rapid loss alarm.",
         None, None, "ASIL-B", "INCOMPLETE",
         ["Tyre_Pressure_FR"], ["TPMS_Warning_Level"], ["Pressure_Dropping_Rapidly"], ["TPMS_ECU", "GATEWAY_ECU"],
         [("GAP-007", "MISSING_THRESHOLD", "HIGH", "Deflation gradient dP/dt threshold for puncture alarm is missing.", "dp_dt_leak_threshold")]),

        ("req_tpms_005", "TPMS-REQ-005", "TPMS", "Sensor Radio Frequency Loss Timeout", "ecu_tpms",
         "If no valid RF telegram is received from a wheel transmitter for longer than 120 seconds while driving > 25 km/h, TPMS sensor fault shall be declared.",
         "120 seconds timeout at speed > 25 km/h", "Fault declare <= 120 s", "ASIL-A", "COMPLETE",
         ["TPMS_RF_Telegram_Timestamp", "Vehicle_Speed"], ["TPMS_Sensor_Fault_DTC"], ["Timeout > 120s"], ["TPMS_ECU"], []),

        # Suspension & Road Monitoring requirements (5)
        ("req_rod_001", "ROD-REQ-001", "Suspension", "Speed Breaker Detection", "ecu_dynamics",
         "When vertical acceleration displays twin-peak profile with amplitude between 1.2g and 2.0g and duration 200-500 ms at speeds < 40 km/h, classify as speed breaker.",
         "1.2g - 2.0g, 200-500 ms", "Classify <= 50 ms after exit", "QM", "COMPLETE",
         ["Vertical_Acceleration_Shock", "Vehicle_Speed"], ["Road_Profile_State"], ["Speed_Breaker_Profile"], ["VEHICLE_DYNAMICS_ECU"], []),

        ("req_rod_002", "ROD-REQ-002", "Suspension", "Pothole Impact Detection", "ecu_dynamics",
         "The system shall detect severe pothole impacts and notify chassis controllers to suppress spurious active intervention.",
         None, None, "ASIL-B", "INCOMPLETE",
         ["Vertical_Acceleration_Shock", "Wheel_Speed_FR"], ["Pothole_Event_Flag"], ["Vertical_Shock_Occurred"], ["VEHICLE_DYNAMICS_ECU", "BRAKE_ECU"],
         [("GAP-008", "MISSING_THRESHOLD", "HIGH", "Pothole acceleration threshold and frequency window undefined.", "pothole_shock_threshold")]),

        ("req_rod_003", "ROD-REQ-003", "Suspension", "Road Roughness Estimation Index", "ecu_dynamics",
         "The Vehicle Dynamics ECU shall compute continuous road roughness metric using rolling RMS of vertical acceleration over 2.0 second window.",
         "RMS window 2.0 s", "Update rate 5 Hz", "QM", "COMPLETE",
         ["Vertical_Acceleration_Shock"], ["Road_Roughness_Index"], ["Vehicle_Speed > 15 km/h"], ["VEHICLE_DYNAMICS_ECU"], []),

        ("req_rod_004", "ROD-REQ-004", "Suspension", "Low Tyre Pressure Combined with Pothole", "ecu_dynamics",
         "If a pothole event is detected on a wheel where TPMS has declared low pressure, transmit high-risk rim damage advisory to Telematics.",
         "Pothole_Event = True AND TPMS_Warning_Level >= 1", "Transmit <= 200 ms", "QM", "COMPLETE",
         ["Pothole_Event_Flag", "TPMS_Warning_Level"], ["Rim_Damage_Advisory_Flag"], ["Pothole_On_Soft_Tyre"], ["VEHICLE_DYNAMICS_ECU", "TELEMATICS_ECU"], []),

        ("req_rod_005", "ROD-REQ-005", "Suspension", "Suspension Bottoming Out Detection", "ecu_dynamics",
         "When chassis bottoming out occurs, log suspension overload event.",
         None, None, "QM", "INCOMPLETE",
         ["Vertical_Acceleration_Shock"], ["Suspension_Overload_DTC"], ["Overload_Spike"], ["VEHICLE_DYNAMICS_ECU"],
         [("GAP-009", "MISSING_THRESHOLD", "LOW", "Bottoming out vertical shock g-force threshold undefined.", "bottoming_out_threshold")]),

        # CAN & Communication requirements (5)
        ("req_com_001", "COM-REQ-001", "Communication", "CAN-FD Frame Integrity & CRC", "ecu_gateway",
         "All safety-critical frames shall implement rolling alive counters (0-15) and 16-bit CRC checksum. Corrupted frames shall be discarded.",
         "CRC-16, Alive counter mismatch > 1", "Discard within current cycle", "ASIL-D", "COMPLETE",
         ["CAN_Raw_Frame"], ["CAN_Frame_Valid_Flag"], ["CRC_Error OR Alive_Jump"], ["GATEWAY_ECU"], []),

        ("req_com_002", "COM-REQ-002", "Communication", "ADAS to Brake Bus Timeout Detection", "ecu_brake",
         "The Brake ECU shall detect loss of ADAS heartbeat messages. Upon timeout, active AEB requests shall be inhibited and safety warning raised.",
         None, None, "ASIL-D", "INCOMPLETE",
         ["Heartbeat_ADAS"], ["Brake_System_Degraded_Flag"], ["No_Heartbeat_Received"], ["BRAKE_ECU", "ADAS_ECU"],
         [("GAP-010", "MISSING_TIMEOUT", "CRITICAL", "CAN timeout threshold for ADAS heartbeat detection is missing.", "can_hb_timeout_ms")]),

        ("req_com_003", "COM-REQ-003", "Communication", "CAN Bus-Off Recovery State Machine", "ecu_gateway",
         "When transmit error counter exceeds 255, the ECU shall enter Bus-Off state, disconnect from bus, and attempt automatic recovery after 1000 ms.",
         "TEC > 255, Recovery wait 1000 ms", "State transition <= 5 ms", "ASIL-C", "COMPLETE",
         ["CAN_Transmit_Error_Counter"], ["CAN_Bus_Off_Status"], ["TEC > 255"], ["GATEWAY_ECU"], []),

        ("req_com_004", "COM-REQ-004", "Communication", "Stale Sensor Signal Detection", "ecu_dynamics",
         "If the wheel speed sensor message rolling counter freezes for 3 consecutive cycles (30 ms), the dynamics controller shall declare data stale.",
         "3 consecutive frozen cycles (30 ms)", "Detection <= 30 ms", "ASIL-D", "COMPLETE",
         ["Wheel_Speed_FL_Counter"], ["Wheel_Speed_FL_Stale_Flag"], ["Counter_Frozen"], ["VEHICLE_DYNAMICS_ECU"], []),

        ("req_com_005", "COM-REQ-005", "Communication", "Gateway Bus Routing Latency", "ecu_gateway",
         "The Gateway ECU shall route cross-domain safety messages between chassis CAN-FD and body CAN with latency not exceeding 5 ms.",
         "Routing latency <= 5 ms", "Max latency 5 ms", "ASIL-B", "COMPLETE",
         ["Ingress_Safety_Frame"], ["Egress_Safety_Frame"], ["Route_Active"], ["GATEWAY_ECU"], []),

        # Diagnostics requirements (5)
        ("req_dia_001", "DIA-REQ-001", "Diagnostics", "Wheel Speed Plausibility Cross-Check", "ecu_brake",
         "If one non-driven wheel speed differs from the average of the remaining three wheels by > 20% for > 200 ms while vehicle speed > 30 km/h, log sensor fault.",
         "20% deviation for 200 ms at speed > 30 km/h", "Debounce 200 ms", "ASIL-D", "COMPLETE",
         ["Wheel_Speed_FL", "Wheel_Speed_FR", "Wheel_Speed_RL", "Wheel_Speed_RR"], ["Wheel_Speed_Sensor_Fault_DTC"], ["Plausibility_Mismatch"], ["BRAKE_ECU"], []),

        ("req_dia_002", "DIA-REQ-002", "Diagnostics", "Yaw Rate Sensor Drift Calibration", "ecu_dynamics",
         "When vehicle is stationary for > 3.0 seconds, the IMU controller shall update yaw rate zero-bias offset.",
         "Stationary > 3.0 s, |Speed| < 0.5 km/h", "Calibrate within 500 ms", "ASIL-C", "COMPLETE",
         ["Yaw_Rate_Actual", "Vehicle_Speed"], ["Yaw_Rate_Zero_Bias"], ["Vehicle_Stationary"], ["VEHICLE_DYNAMICS_ECU"], []),

        ("req_dia_003", "DIA-REQ-003", "Diagnostics", "Degraded Limp-Home Mode on Primary Brake Fault", "ecu_powertrain",
         "Upon receiving primary brake degradation alert from Brake ECU, powertrain torque shall be capped to prevent high-speed operation.",
         None, None, "ASIL-C", "INCOMPLETE",
         ["Brake_System_Degraded_Flag"], ["Max_Engine_Torque_Cap"], ["Brake_Degraded"], ["POWERTRAIN_ECU", "BRAKE_ECU"],
         [("GAP-011", "MISSING_THRESHOLD", "HIGH", "Limp-home maximum vehicle speed or engine torque limit unspecified.", "limp_home_torque_limit")]),

        ("req_dia_004", "DIA-REQ-004", "Diagnostics", "Sensor Fault Recovery Qualification", "ecu_adas",
         "A transient camera occlusion fault shall automatically clear only after camera confidence remains above threshold for sustained duration.",
         None, None, "ASIL-B", "AMBIGUOUS",
         ["Camera_Confidence_Metric"], ["Camera_Fault_Cleared_Flag"], ["Confidence_Restored"], ["ADAS_ECU"],
         [("GAP-012", "MISSING_TIMEOUT", "MEDIUM", "Sustained qualification duration and hysteresis threshold for clearing camera fault undefined.", "camera_recovery_debounce_ms")]),

        ("req_dia_005", "DIA-REQ-005", "Diagnostics", "Crash Telemetry Non-Volatile Storage", "ecu_telematics",
         "Upon crash confirmation, 10 seconds of pre-crash and 5 seconds of post-crash CAN buffer telemetry shall be locked in non-volatile flash within 500 ms.",
         "-10s to +5s window", "Write complete <= 500 ms", "ASIL-B", "COMPLETE",
         ["Crash_Event_Signal", "Circular_CAN_Buffer"], ["EDR_Flash_Locked_Flag"], ["Crash_Event"], ["TELEMATICS_ECU"], [])
    ]

    for rid, rcode, rsys, rsubs, reid, otext, thresh, timing, asil, cstat, inps, outs, conds, deps, gaps in reqs_data:
        req = Requirement(
            id=rid, req_code=rcode, vehicle_id=pusv.id, ecu_id=reid, system=rsys,
            subsystem=rsubs, original_text=otext,
            normalized_summary=f"{rsys} requirement for {rsubs} with safety integrity {asil}.",
            threshold=thresh, timing_constraint=timing, safety_relevance=asil,
            completeness_status=cstat, created_at=datetime.utcnow()
        )
        req.inputs = inps
        req.outputs = outs
        req.conditions = conds
        req.dependencies = deps
        db.add(req)
        db.flush()

        for gid, gtype, gsev, gdesc, gparam in gaps:
            gap = SpecificationGap(
                id=gid, requirement_id=req.id, gap_type=gtype, severity=gsev,
                description=gdesc, missing_parameter=gparam, affected_ecu_id=reid,
                suggested_action="Engineering review required to define explicit numerical threshold before software sign-off.",
                status="OPEN", created_at=datetime.utcnow()
            )
            gap.affected_functions = [rsubs, rsys]
            db.add(gap)

    db.flush()

    # 6. 20 Pune / Indian Scenarios across 6 categories
    scenarios_data = [
        # DENSE_TRAFFIC (5)
        ("scen_pune_stopngo", "SCEN-TRF-001", "DENSE_TRAFFIC", "Swargate Junction Stop-and-Go Creep",
         "Ultra-dense bumper-to-bumper traffic on Tilak Road / Swargate junction with pedestrian crossing and erratic vehicle distances.",
         "Swargate Flyover descent during 6:30 PM peak rush hour with autos squeezing into safety cushion.",
         0.80, 5.0, "DENSE_STOP_AND_GO", {"ego_speed_kph": 18.0, "lead_gap_m": 2.2, "cutin_frequency": "HIGH"}),

        ("scen_pune_cutin", "SCEN-TRF-002", "DENSE_TRAFFIC", "Sudden Motorcycle Cut-in from Blind Gap",
         "Two-wheeler aggressively cuts diagonally across ego vehicle front fender from between stopped bus and divider.",
         "FC Road near Deccan Gymkhana with two-wheelers filtering through stopped traffic.",
         0.78, 10.0, "HIGH", {"ego_speed_kph": 40.0, "cutin_lateral_speed_mps": 2.4, "cutin_distance_m": 6.5}),

        ("scen_pune_jaywalk", "SCEN-TRF-003", "DENSE_TRAFFIC", "Pedestrian Emerges from Behind Pune PMT Bus",
         "A pedestrian suddenly steps into traffic from immediately in front of a stationary city transit bus.",
         "Karve Road near Nal Stop with pedestrians jaywalking around heavy PMT commuter buses.",
         0.82, 15.0, "HIGH", {"ego_speed_kph": 32.0, "ttc_sec": 1.4, "occlusion_pct": 75.0}),

        ("scen_pune_autorickshaw", "SCEN-TRF-004", "DENSE_TRAFFIC", "Three-Wheeler Sudden Passenger Pickup Stop",
         "Lead auto-rickshaw abruptly swerves across lane and brakes hard to pickup passenger without brake light functioning.",
         "Pune University Circle to Aundh corridor.",
         0.85, 0.0, "HIGH", {"lead_decel_mps2": 5.5, "lead_brake_light_functional": False}),

        ("scen_pune_wrong_side", "SCEN-TRF-005", "DENSE_TRAFFIC", "Contraflow Scooter on Narrow Street Margin",
         "Scooter traveling wrong-way along the road edge while ego vehicle navigates oncoming traffic.",
         "Camp MG Road one-way lane with wrong-way local two-wheelers.",
         0.80, 0.0, "NORMAL", {"scooter_closing_speed_kph": 30.0, "lateral_clearance_m": 0.8}),

        # ROAD_CONDITIONS (4)
        ("scen_pune_pothole_deep", "SCEN-ROD-001", "ROAD_CONDITIONS", "Deep Unmarked Pothole Impact",
         "12 cm deep water-filled pothole encountered at 45 km/h generating severe vertical chassis acceleration spike.",
         "Sinhagad Road monsoon crater pothole with sharp asphalt edge.",
         0.65, 10.0, "NORMAL", {"pothole_depth_cm": 12.0, "shock_g": 3.8, "speed_kph": 45.0}),

        ("scen_pune_speedbreaker", "SCEN-ROD-002", "ROAD_CONDITIONS", "Unpainted Steep Concrete Speed Breaker",
         "Sharp unmarked municipal rumble hump with abrupt entry ramp exceeding standard IRC specifications.",
         "Viman Nagar residential connector lane.",
         0.85, 0.0, "NORMAL", {"hump_height_cm": 16.0, "hump_duration_ms": 320}),

        ("scen_pune_uneven_pavers", "SCEN-ROD-003", "ROAD_CONDITIONS", "Loose Paver Blocks on Dug-up Utility Trench",
         "Uneven road trench filled with loose interlocking pavers creating high-frequency wheel speed vibration.",
         "Smart City trench work on Baner Road with loose paver surface.",
         0.60, 0.0, "NORMAL", {"vibration_freq_hz": 18.0, "wheel_slip_jitter": 0.08}),

        ("scen_pune_rumble_strip", "SCEN-ROD-004", "ROAD_CONDITIONS", "High-Speed Highway Rumble Strips",
         "Series of 6 closely-spaced thermoplastic rumble strips approaching highway toll plaza.",
         "Old Pune-Mumbai Highway near Dehu Road bypass.",
         0.82, 0.0, "NORMAL", {"strip_count": 6, "pitch_cm": 30.0}),

        # MONSOON (4)
        ("scen_pune_monsoon_puddle", "SCEN-MON-001", "MONSOON", "Heavy Monsoon Rain with Standing Water Aquaplaning",
         "Torrential July downpour causing 3 cm standing water puddle with severe drop in road friction coefficient.",
         "Pune Mumbai Expressway ghat section during continuous cloudburst downpour.",
         0.42, 45.0, "HIGH", {"water_depth_mm": 35.0, "friction_mu": 0.42, "visibility_pct": 55.0}),

        ("scen_pune_monsoon_spray", "SCEN-MON-002", "MONSOON", "Heavy Truck Mud-Water Spray Occluding Camera",
         "Overtaking heavy dumper truck tosses muddy spray across windshield, temporarily degrading front camera perception.",
         "Katraj Bypass tunnel exit in monsoon evening.",
         0.50, 60.0, "HIGH", {"camera_occlusion_pct": 80.0, "duration_sec": 3.5}),

        ("scen_pune_submerged_road", "SCEN-MON-003", "MONSOON", "Waterlogged Undercrossing with Hidden Obstacles",
         "Submerged bridge underpass with 15 cm muddy water concealing sunken debris and curbstones.",
         "Pulgate railway underpass during peak monsoon water accumulation.",
         0.38, 30.0, "DENSE_STOP_AND_GO", {"water_level_cm": 15.0, "lead_vehicle_loss": True}),

        ("scen_pune_monsoon_braking", "SCEN-MON-004", "MONSOON", "Emergency Braking on Wet Polished Asphalt",
         "Maximum braking deceleration event on wet polished asphalt surface with oil slick film.",
         "Senapati Bapat Road junction wet surface braking.",
         0.45, 25.0, "NORMAL", {"friction_mu": 0.45, "oil_film_present": True}),

        # INTERSECTIONS (3)
        ("scen_pune_signal_blind", "SCEN-INT-001", "INTERSECTIONS", "Obstructed Traffic Signal at Tree-Canopied Junction",
         "Traffic light partially hidden behind banyan tree canopy with ambiguity between yellow and red states.",
         "Model Colony junction with overgrown tree branches blocking overhead signal.",
         0.85, 20.0, "NORMAL", {"signal_visibility_pct": 35.0, "signal_state": "YELLOW_TO_RED"}),

        ("scen_pune_junction_cross", "SCEN-INT-002", "INTERSECTIONS", "Uncontrolled T-Junction with Cross Traffic Incursion",
         "Bystander motorcycle crosses uncontrolled four-way junction against cross traffic without stopping.",
         "Koregaon Park North Main Road intersection.",
         0.80, 0.0, "HIGH", {"cross_speed_kph": 35.0, "ttc_sec": 1.6}),

        ("scen_pune_roundabout", "SCEN-INT-003", "INTERSECTIONS", "Multi-Lane Rotary Infiltration without Lane Discipline",
         "Five-lane entry into Sancheti Hospital circle where vehicles from left and right merge simultaneously.",
         "Sancheti Chowk roundabout chaotic morning flow.",
         0.75, 5.0, "HIGH", {"concurrent_merging_vehicles": 4}),

        # TYRE_CONDITIONS (2)
        ("scen_pune_tyre_puncture", "SCEN-TYR-001", "TYRE_CONDITIONS", "Front-Right Tyre Rapid Nail Puncture",
         "Sharp construction nail puncture on highway causing rapid pressure drop from 2.3 bar to 1.2 bar in 8 seconds.",
         "Hinjawadi Phase 3 IT park access expressway with loose metal debris.",
         0.70, 0.0, "NORMAL", {"target_tyre": "FR", "pressure_start_bar": 2.3, "pressure_end_bar": 1.2, "leak_time_sec": 8.0}),

        ("scen_pune_tyre_thermal", "SCEN-TYR-002", "TYRE_CONDITIONS", "High Ambient Summer Highway Thermal Buildup",
         "Ambient 44 deg C heat with sustained 100 km/h driving causing tyre cavity temperature to surge past 82 deg C.",
         "Pune-Solapur highway stretch in peak May afternoon.",
         0.88, 0.0, "LOW", {"ambient_temp_c": 44.0, "tyre_temp_c": 83.5, "pressure_bar": 2.85}),

        # SENSOR_FAILURES (2)
        ("scen_pune_cam_blindness", "SCEN-SNS-001", "SENSOR_FAILURES", "Direct Low-Angle Sun Glare Camera Blindness",
         "Direct blinding evening sunset glare directly into windshield camera reducing optical contrast to zero.",
         "Westbound driving on Paud Road facing sunset.",
         0.85, 75.0, "NORMAL", {"optical_contrast": 0.05, "glare_lux": 95000}),

        ("scen_pune_can_loss", "SCEN-SNS-002", "SENSOR_FAILURES", "Chassis CAN-FD Intermittent Frame Jitter and Drop",
         "Loose wiring connector causing 4 consecutive dropped CAN frames between ADAS and Brake ECUs.",
         "Vibrational harness fatigue after driving 20 km over broken rural tarmac.",
         0.80, 0.0, "NORMAL", {"dropped_frames": 4, "jitter_ms": 45.0})
    ]

    for sid, scode, scat, sname, sdesc, spune, fric, vis, dens, sparams in scenarios_data:
        scen = Scenario(
            id=sid, code=scode, category=scat, name=sname, description=sdesc,
            pune_context=spune, road_friction=fric, visibility_reduction_pct=vis,
            traffic_density=dens, created_at=datetime.utcnow()
        )
        scen.parameters = sparams
        db.add(scen)

    db.flush()

    # 7. 60+ Seed Automotive Test Cases covering diverse test types and multi-ECU interactions
    test_cases_data = [
        # TC-BRK-001 to TC-BRK-015
        ("tc_brk_001", "TC-BRK-001", "Peak deceleration verification on high friction asphalt", "Functional", "P0",
         ["req_brk_001"], ["BRAKE_ECU"], ["sens_ws_fl", "sens_brake_press", "act_brake_mod"],
         ["Vehicle speed = 80 km/h", "Dry asphalt friction mu = 0.85", "Brake temperature = 80 C"],
         "Straight line emergency stop from 80 km/h on dry flat road.",
         [{"signal": "Brake_Pressure_Demand", "value": 140, "unit": "bar"}, {"signal": "Vehicle_Speed", "value": 80, "unit": "km/h"}],
         ["Accelerate ego vehicle to stable 80 km/h", "Inject 140 bar step brake pressure command", "Record deceleration curve via chassis IMU"],
         ["Deceleration reaches >= 8.5 m/s2 within 150 ms", "Stopping distance <= 29.5 meters", "No wheel lockup"],
         [], [], "Deceleration >= 8.5 m/s2 and zero ABS error flags.", "Standard baseline braking homologation test.", 0.98,
         ["Dry asphalt condition", "Tire pressure nominal at 2.3 bar"], [], "VALIDATED", "PASS", None),

        ("tc_brk_002", "TC-BRK-002", "ABS slip regulation under split-mu (asymmetric friction) surface", "Boundary", "P0",
         ["req_brk_002", "req_brk_008"], ["BRAKE_ECU", "VEHICLE_DYNAMICS_ECU"], ["sens_ws_fl", "sens_ws_fr", "sens_imu"],
         ["Left wheels on wet steel plate (mu=0.25)", "Right wheels on dry asphalt (mu=0.85)", "Vehicle speed = 60 km/h"],
         "Braking across split friction surface with high yaw disturbance.",
         [{"signal": "Vehicle_Speed", "value": 60, "unit": "km/h"}, {"signal": "Brake_Pressure_Demand", "value": 120, "unit": "bar"}],
         ["Drive onto split-mu transition surface", "Apply full brake pedal demand", "Observe individual caliper pressure modulation"],
         ["Left caliper pressure modulated to prevent lockup", "Yaw deviation compensated within 2.5 deg/s", "ABS active on left wheels"],
         [], [], "Vehicle maintains course without exceeding 0.3m lateral lane deviation.", "Critical vehicle stability test.", 0.95,
         ["Electronic stability control active"], [], "VALIDATED", "PASS", None),

        ("tc_brk_003", "TC-BRK-003", "Emergency braking with uncalibrated master cylinder pressure sensor", "Fault injection", "P0",
         ["req_brk_007"], ["BRAKE_ECU"], ["sens_brake_press"],
         ["Vehicle speed = 50 km/h", "Sensor signal forced to 0.05V (open circuit fault)"],
         "Sensor electrical line disconnect during normal driving.",
         [{"signal": "Master_Cylinder_Voltage", "value": 0.05, "unit": "V"}],
         ["Drive at 50 km/h", "Inject voltage clamp at 0.05V", "Issue driver braking input"],
         ["ECU declares sensor electrical fault within 20 ms", "Switches to open-loop backup pressure model", "Warning lamp lit"],
         ["Clamp Master_Cylinder_Voltage to 0.05V at t=1.0s"], ["Restore voltage to 1.5V"],
         "Backup mode engages within 20 ms with decelerating capability preserved.", "Sensor failure degradation mode.", 0.92,
         ["Backup throttle map available"], [], "VALIDATED", "PASS", None),

        ("tc_brk_014", "TC-BRK-014", "Automatic Emergency Braking execution on sudden motorcycle cut-in", "Compound scenario", "P0",
         ["req_brk_014", "req_adas_002"], ["ADAS_ECU", "BRAKE_ECU", "VEHICLE_DYNAMICS_ECU"], ["sens_front_radar", "sens_front_camera", "act_brake_mod"],
         ["Vehicle speed = 42 km/h", "Lead motorcycle cuts in with 2.4 m/s lateral speed", "Driver brake pedal input = 0 bar"],
         "Pune FC Road high-density motorcycle cut-in during urban commute.",
         [{"signal": "Vehicle_Speed", "value": 42, "unit": "km/h"}, {"signal": "Lead_Object_Distance", "value": 14.5, "unit": "m"}, {"signal": "Collision_Risk_Index", "value": 92, "unit": "%"}],
         ["Ego vehicle cruises at 42 km/h", "Motorcycle intrudes into ego path at 14.5m distance", "ADAS identifies collision risk", "BRAKE_ECU receives AEB_Request"],
         ["AEB_Request commanded to FULL", "Hydraulic pressure increases to 110 bar within 180 ms", "Collision avoided with > 1.2m residual gap"],
         [], [], "AEB intervention halts ego vehicle prior to contact.", "Primary urban active safety feature.", 0.75,
         ["Tire friction is dry"],
         ["SPECIFICATION GAP: AEB intervention collision risk index and driver pressure override threshold undefined in BRK-REQ-014."],
         "BLOCKED", "BLOCKED", "AEB intervention threshold is not specified in source requirement BRK-REQ-014."),

        ("tc_brk_015", "TC-BRK-015", "Pothole vertical impact during hard ABS braking", "Inter-ECU integration", "P1",
         ["req_brk_010", "req_rod_002"], ["BRAKE_ECU", "VEHICLE_DYNAMICS_ECU"], ["sens_ws_fr", "sens_imu"],
         ["Vehicle decelerating at 7.0 m/s2", "Front-right wheel drops into 10 cm pothole", "Vertical acceleration = 3.5g"],
         "Monsoon pothole encountered while actively braking hard.",
         [{"signal": "Vertical_Acceleration_Shock", "value": 3.5, "unit": "g"}, {"signal": "Wheel_Speed_FR", "value": 15, "unit": "km/h"}],
         ["Initiate full braking from 60 km/h", "Inject 3.5g vertical shock pulse for 80 ms", "Monitor ABS pressure modulation response"],
         ["ABS does not falsely vent caliper pressure", "Braking force maintained after pothole exit", "Pothole event logged"],
         ["Inject 3.5g vertical shock and momentary wheel speed drop"], ["Chassis stabilizes after 120 ms"],
         "No false ABS pressure dump causing stopping distance blowout.", "Chassis shock and braking interaction.", 0.91,
         ["IMU sampling rate 100 Hz"],
         ["SPECIFICATION GAP: Pothole acceleration threshold and frequency window undefined in ROD-REQ-002."],
         "BLOCKED", "BLOCKED", "Pothole acceleration threshold and frequency window undefined in ROD-REQ-002."),

        # TC-ADAS-001 to TC-ADAS-008
        ("tc_adas_001", "TC-ADAS-001", "Forward Collision Warning TTC threshold detection at 60 km/h", "Functional", "P1",
         ["req_adas_001"], ["ADAS_ECU", "BODY_ECU"], ["sens_front_radar", "sens_front_camera", "act_cluster_chime"],
         ["Ego speed = 60 km/h", "Stationary target object at 65 meters", "Relative speed = -16.6 m/s"],
         "Approaching stationary car stopped at Pune University junction.",
         [{"signal": "Vehicle_Speed", "value": 60, "unit": "km/h"}, {"signal": "Lead_Object_Distance", "value": 40, "unit": "m"}],
         ["Approach stationary target at 60 km/h", "TTC decreases linearly", "Observe warning alert onset time"],
         ["FCW audible and visual warning triggers exactly when TTC <= 2.4s (distance <= 40m)", "Alert broadcast on CAN within 30 ms"],
         [], [], "Alert triggered within +/- 50 ms of 2.4s TTC threshold.", "Homologation active safety warning test.", 0.97,
         ["Clear radar sightlines"], [], "VALIDATED", "PASS", None),

        ("tc_adas_003", "TC-ADAS-003", "Camera perception degradation in monsoon heavy rain spray", "Environmental", "P1",
         ["req_adas_003"], ["ADAS_ECU"], ["sens_front_camera", "sens_front_radar"],
         ["Heavy rainfall rate > 30 mm/h", "Truck spray active", "Camera optical confidence falls below threshold"],
         "Pune-Mumbai expressway monsoon truck spray overtaking scenario.",
         [{"signal": "Wiper_Speed_State", "value": 3, "unit": "level"}, {"signal": "Camera_Confidence_Metric", "value": 0.25, "unit": "norm"}],
         ["Simulate heavy rain and spray", "Ramp down camera confidence to 0.25", "Measure perception fusion output weighting"],
         ["Perception fusion degrades camera weighting", "Relies primarily on radar tracking", "Driver notified of weather degraded mode"],
         ["Inject camera optical blur and low contrast"], ["Rain clears and confidence recovers above 0.70"],
         "Perception tracks lead vehicle without phantom braking.", "Adverse weather sensor robustness.", 0.70,
         ["Radar antenna free of mud buildup"],
         ["SPECIFICATION GAP: Camera confidence score lower cutoff for perception weight shift is undefined in ADAS-REQ-003."],
         "BLOCKED", "BLOCKED", "Camera confidence score lower cutoff for perception weight shift is undefined in ADAS-REQ-003."),

        ("tc_adas_004", "TC-ADAS-004", "Pedestrian emergency braking at 35 km/h", "Functional", "P0",
         ["req_adas_004"], ["ADAS_ECU", "BRAKE_ECU"], ["sens_front_camera", "act_brake_mod"],
         ["Ego vehicle speed = 35 km/h", "Adult pedestrian mannequin traverses path at 5 km/h"],
         "Pedestrian jaywalking between parked cars on Karve Road.",
         [{"signal": "Vehicle_Speed", "value": 35, "unit": "km/h"}, {"signal": "Lead_Object_Distance", "value": 18, "unit": "m"}],
         ["Drive at 35 km/h towards pedestrian mannequin", "TTC reaches 1.4s at 13.6m distance", "Validate AEB braking execution"],
         ["AEB commands maximum deceleration", "Vehicle stops with > 1.0m margin from mannequin", "Zero collision impact"],
         [], [], "Complete stop achieved without collision.", "Vulnerable Road User (VRU) compliance.", 0.96,
         ["Pedestrian optical silhouette visible"], [], "VALIDATED", "PASS", None),

        # TC-TPMS-001 to TC-TPMS-005
        ("tc_tpms_001", "TC-TPMS-001", "Low tyre pressure threshold alert at 1.80 bar", "Functional", "P1",
         ["req_tpms_001"], ["TPMS_ECU", "BODY_ECU"], ["sens_tpms_fr"],
         ["Placard pressure = 2.3 bar", "Front-right tyre deflates to 1.80 bar (21.7% loss)", "Vehicle speed = 50 km/h"],
         "Slow puncture on Baner Road commute.",
         [{"signal": "Tyre_Pressure_FR", "value": 1.80, "unit": "bar"}],
         ["Cruise at 50 km/h", "Deflate FR tyre to 1.80 bar", "Check cluster alert signal"],
         ["TPMS warning lamp illuminates within 15 seconds", "Diagnostic message identifies Front-Right wheel"],
         [], [], "Alert illuminates within 15 seconds for pressure < 1.84 bar.", "Standard tyre pressure compliance.", 0.99,
         ["TPMS sensor battery valid"], [], "VALIDATED", "PASS", None),

        ("tc_tpms_004", "TC-TPMS-004", "Highway rapid puncture leak detection under high speed", "Boundary", "P0",
         ["req_tpms_004"], ["TPMS_ECU", "GATEWAY_ECU", "VEHICLE_DYNAMICS_ECU"], ["sens_tpms_fr"],
         ["Vehicle speed = 90 km/h", "Nail puncture causing 0.15 bar/s pressure drop"],
         "Hinjawadi expressway rapid puncture event.",
         [{"signal": "Tyre_Pressure_FR", "value": 1.5, "unit": "bar"}, {"signal": "Vehicle_Speed", "value": 90, "unit": "km/h"}],
         ["Run vehicle at 90 km/h", "Vent FR pressure rapidly at 0.15 bar/sec", "Observe TPMS alarm severity"],
         ["Critical rapid deflation warning transmitted", "Stability control informed to adapt torque vectoring"],
         ["Rapid venting of FR tyre cavity"], ["Wheel replacement"],
         "Critical alarm issued before pressure drops below 1.2 bar.", "High-speed tyre blowout safety.", 0.72,
         ["Vehicle dynamics controller active"],
         ["SPECIFICATION GAP: Deflation gradient dP/dt threshold for puncture alarm is missing in TPMS-REQ-004."],
         "BLOCKED", "BLOCKED", "Deflation gradient dP/dt threshold for puncture alarm is missing in TPMS-REQ-004."),

        # TC-ROD-001 to TC-ROD-005
        ("tc_rod_001", "TC-ROD-001", "Speed breaker vertical acceleration twin-peak classification", "Functional", "P2",
         ["req_rod_001"], ["VEHICLE_DYNAMICS_ECU"], ["sens_imu", "sens_ws_fl"],
         ["Vehicle speed = 25 km/h", "Traversing 14 cm speed bump"],
         "Navigating residential speed bump in Kothrud.",
         [{"signal": "Vertical_Acceleration_Shock", "value": 1.6, "unit": "g"}, {"signal": "Vehicle_Speed", "value": 25, "unit": "km/h"}],
         ["Drive over speed bump at 25 km/h", "Record IMU Z-axis wave", "Verify classifier output"],
         ["Classifies event as SPEED_BREAKER within 40 ms of rear axle exit", "Does not raise false chassis fault"],
         [], [], "Correct classification with zero false alarms.", "Pune road profile characterization.", 0.94,
         ["IMU calibrated"], [], "VALIDATED", "PASS", None),

        # TC-COM-001 to TC-COM-005
        ("tc_com_002", "TC-COM-002", "Brake ECU response to ADAS CAN heartbeat communication timeout", "Communication failure", "P0",
         ["req_com_002"], ["BRAKE_ECU", "ADAS_ECU"], ["sens_front_radar"],
         ["Vehicle speed = 60 km/h", "CAN bus cable between ADAS and Brake disconnected"],
         "Wiring harness failure on rough road vibration.",
         [{"signal": "Heartbeat_ADAS", "value": 0, "unit": "counter"}],
         ["Drive at 60 km/h", "Halt ADAS CAN frame transmission", "Measure time until Brake ECU enters fail-safe"],
         ["Brake ECU inhibits automated AEB triggers", "Sets degraded brake DTC", "Alerts driver with audible chime"],
         ["Interrupt ADAS CAN transmission for 300 ms"], ["Resume CAN transmission"],
         "Fail-safe state entered within defined timeout period.", "CAN communication watchdog safety.", 0.65,
         ["Brake ECU power supply intact"],
         ["SPECIFICATION GAP: CAN timeout threshold for ADAS heartbeat detection is missing in COM-REQ-002."],
         "BLOCKED", "BLOCKED", "CAN timeout threshold for ADAS heartbeat detection is missing in COM-REQ-002."),

        # TC-DIA-001 to TC-DIA-005
        ("tc_dia_001", "TC-DIA-001", "Wheel speed sensor plausibility cross-check mismatch detection", "Sensor failure", "P1",
         ["req_dia_001"], ["BRAKE_ECU"], ["sens_ws_fl", "sens_ws_fr", "sens_ws_rl", "sens_ws_rr"],
         ["Vehicle speed = 50 km/h", "Front-Left wheel speed signal artificially clamped to 35 km/h (-30%)"],
         "Damaged tone ring or air gap fault on front-left hub.",
         [{"signal": "Wheel_Speed_FL", "value": 35, "unit": "km/h"}, {"signal": "Wheel_Speed_FR", "value": 50, "unit": "km/h"}],
         ["Drive at steady 50 km/h", "Clamp FL wheel speed to 35 km/h for 250 ms", "Observe diagnostic trouble code generation"],
         ["Sensor plausibility mismatch detected after 200 ms debounce", "ABS disables FL active control only", "DTC logged in non-volatile memory"],
         ["Signal clamp on FL wheel speed"], ["Release clamp"],
         "Sensor fault isolated to FL wheel and latched.", "Fault isolation and containment.", 0.96,
         ["Dry straight road driving"], [], "VALIDATED", "PASS", None),

        # TC-CMP-001: PRIMARY DEMO COMPOUND TEST CASE
        ("tc_cmp_001", "TC-CMP-001", "Pune Monsoon Emergency Braking with Motorcycle Cut-in and Low Tyre Pressure", "Compound scenario", "P0",
         ["req_brk_001", "req_brk_005", "req_brk_014", "req_adas_002", "req_adas_003", "req_tpms_001", "req_rod_002"],
         ["ADAS_ECU", "BRAKE_ECU", "VEHICLE_DYNAMICS_ECU", "TPMS_ECU", "BODY_ECU", "GATEWAY_ECU", "TELEMATICS_ECU"],
         ["sens_front_radar", "sens_front_camera", "sens_ws_fr", "sens_tpms_fr", "sens_imu", "act_brake_mod", "act_cluster_chime"],
         ["Ego speed = 40 km/h", "Wet uneven surface (mu=0.45)", "Front-right tyre pressure low (1.6 bar)", "Dense monsoon traffic"],
         "Pune monsoon evening peak hour: lead vehicle slows, two-wheeler cuts into path, road surface wet with pothole shock while FR tyre is under-inflated.",
         [{"signal": "Vehicle_Speed", "value": 40, "unit": "km/h"}, {"signal": "Lead_Object_Distance", "value": 12.0, "unit": "m"},
          {"signal": "Tyre_Pressure_FR", "value": 1.6, "unit": "bar"}, {"signal": "Vertical_Acceleration_Shock", "value": 2.8, "unit": "g"}],
         ["Ego vehicle operates in heavy rain at 40 km/h",
          "TPMS broadcasts low pressure advisory on FR wheel (1.6 bar)",
          "Motorcycle cuts in sharply across ego path at 12m distance",
          "Front camera confidence degraded by rain spray, radar maintains target track",
          "ADAS ECU computes high collision risk and issues AEB_Request to BRAKE_ECU",
          "BRAKE_ECU initiates emergency braking; wet road triggers ABS pulse modulation",
          "FR wheel strikes submerged pothole (2.8g shock); dynamics ECU informs ABS to suppress false lockup",
          "Ego vehicle decelerates smoothly to halt without spinning or contacting obstacle"],
         ["Multi-ECU coordination executed across 6 ECUs simultaneously",
          "Vehicle halts within 14.8m without lane departure",
          "Telematics logs combined incident telemetry to cloud"],
         ["Inject 1.6 bar tyre pressure", "Inject 2.8g pothole vertical shock during brake application", "Inject 40% camera blur"],
         ["Vehicle reaches standstill", "Driver acknowledges cluster warning"],
         "Zero collision, directional stability retained, all degraded states gracefully accommodated.",
         "High-stress compound multi-ECU edge case demonstrating real-world Indian road resilience.",
         0.78,
         ["Radar tracking unimpaired by water", "Driver does not panic-steer into oncoming lane"],
         ["SPECIFICATION GAP: AEB intervention collision risk index threshold undefined in BRK-REQ-014.",
          "SPECIFICATION GAP: Pothole acceleration threshold and frequency window undefined in ROD-REQ-002."],
         "BLOCKED", "BLOCKED", "AEB intervention threshold is not specified in source requirement BRK-REQ-014.")
    ]

    for (tcid, tcode, title, cat, pri, req_ids, ecus, deps, preconds,
         scen_desc, inps, steps, expected, faults, recovs, criteria,
         snotes, conf, assumps, spec_gaps, status, res_status, blk_reason) in test_cases_data:
        
        tc = TestCase(
            id=tcid, code=tcode, title=title, category=cat, priority=pri,
            scenario=scen_desc, pass_fail_criteria=criteria, safety_notes=snotes,
            confidence=conf, is_ai_generated=True, status=status, created_at=datetime.utcnow()
        )
        tc.requirement_ids = req_ids
        tc.ecu_under_test = ecus
        tc.dependencies = deps
        tc.preconditions = preconds
        tc.input_signals = inps
        tc.steps = steps
        tc.expected_results = expected
        tc.fault_injection = faults
        tc.recovery_conditions = recovs
        tc.assumptions = assumps
        tc.specification_gaps = spec_gaps
        db.add(tc)
        db.flush()

        # Add initial test result
        tres = TestResult(
            id=f"res_{tcid}",
            test_case_id=tc.id,
            status=res_status,
            blocked_reason=blk_reason,
            simulation_duration_ms=1800 if res_status != "BLOCKED" else 0,
            executed_at=datetime.utcnow()
        )
        tres.telemetry_data = [
            {"time_ms": 0, "ego_speed": 40, "brake_pressure": 0, "state": "CRUISE"},
            {"time_ms": 200, "ego_speed": 40, "brake_pressure": 15, "state": "WARNING"},
            {"time_ms": 500, "ego_speed": 35, "brake_pressure": 85, "state": "AEB_BRAKING"},
            {"time_ms": 1100, "ego_speed": 10, "brake_pressure": 110, "state": "ABS_MODULATION"},
            {"time_ms": 1600, "ego_speed": 0, "brake_pressure": 40, "state": "STANDSTILL"}
        ]
        tres.log_trace = [
            "Test scenario initialized: " + scen_desc,
            f"Preconditions validated: {', '.join(preconds)}",
            f"ECUs engaged: {', '.join(ecus)}",
            f"Execution status evaluated: {res_status}" + (f" - {blk_reason}" if blk_reason else "")
        ]
        db.add(tres)

    # 8. Recent generation job
    db.add(GenerationJob(
        id="job_init_01",
        requirement_code="BRK-REQ-014",
        scenario_name="Pune Monsoon Emergency Braking with Motorcycle Cut-in",
        tests_generated=5,
        status="COMPLETED",
        created_at=datetime.utcnow()
    ))

    db.commit()
