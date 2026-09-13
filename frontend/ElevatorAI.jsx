import React, { useState, useEffect, useRef, useMemo } from "react";
import {
  LayoutDashboard, Activity, Brain, GitBranch, TrendingUp, HeartPulse,
  BarChart3, History, Wrench, Users, FileText, MessageSquare, Building2,
  Bell, ShieldCheck, Settings as SettingsIcon, ChevronLeft, ChevronRight,
  Search, Sun, Moon, ChevronDown, Wifi, Circle, ArrowUp, ArrowDown,
  AlertTriangle, CheckCircle2, XCircle, Info, Clock, Gauge, Thermometer,
  Zap, Waves, DoorClosed, DoorOpen, Disc3, Droplets, Play, Pause,
  RotateCcw, QrCode, X, Plus, Pencil, Trash2, Download, Eye, ChevronUp,
  Cpu, Server, Database, MonitorSmartphone, RadioTower, Send, Sparkles,
  MapPin, CalendarDays, ClipboardList, UserCheck, Filter, ArrowRight,
  ScanLine, Package, ListChecks, LogIn, FileBarChart2
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell,
  RadialBarChart, RadialBar, PolarAngleAxis, Legend
} from "recharts";

import { fetchElevators } from "./src/api/elevators.js";
import { fetchLatestSensors, fetchSingleSensorHistory } from "./src/api/sensors.js";
import { fetchSimulatorStatus, startSimulator, pauseSimulator, resumeSimulator, resetSimulator, setSimulatorScenario } from "./src/api/simulator.js";
import { connectElevatorTelemetry, connectFleetTelemetry } from "./src/websocket/telemetry.js";
import { triggerAIDetection, fetchRCA, fetchMLEvaluation, fetchAIStatus, runAIBenchmark } from "./src/api/ai.js";
import { fetchRegisteredDevices } from "./src/api/hardware.js";
import { fetchPredictiveStatus, triggerPredictiveAnalysis } from "./src/api/predictive.js";
import { fetchElevatorHealth, updateHealthWeights } from "./src/api/health.js";
import { fetchAlerts, acknowledgeAlert, resolveAlert } from "./src/api/alerts.js";
import { fetchMaintenanceTasks, createMaintenanceTask, assignTechnicianToTask, completeMaintenanceTask } from "./src/api/maintenance.js";
import { fetchTechnicians, recommendTechnician } from "./src/api/technicians.js";
import { fetchAnalyticsSummary, fetchFaultDistribution, fetchBuildingComparison, fetchFaultTrends, fetchMaintenanceTrends } from "./src/api/analytics.js";
import { fetchFaultTimeline } from "./src/api/timeline.js";
import { generateReport, fetchReportTemplates } from "./src/api/reports.js";
import { askAIAssistant } from "./src/api/assistant.js";

/* ============================================================
   DESIGN TOKENS
   ============================================================ */
const C = {
  bg: "#080B12",
  surface: "#0E1420",
  surface2: "#141C2C",
  surface3: "#1B2740",
  border: "#233054",
  borderSoft: "#182238",
  text: "#EAF0FA",
  textMuted: "#8A96B3",
  textFaint: "#5C6785",
  primary: "#2A63E0",
  primaryBright: "#5C8DFF",
  primaryDim: "#12234D",
  success: "#2ECC71",
  successDim: "#132C1F",
  warning: "#F5A524",
  warningDim: "#33230C",
  critical: "#F0454E",
  criticalDim: "#331319",
  info: "#38BDF8",
  infoDim: "#0F2734",
};

const LIGHT = {
  bg: "#F4F6FA",
  surface: "#FFFFFF",
  surface2: "#F8F9FC",
  surface3: "#EEF1F7",
  border: "#DDE3EE",
  borderSoft: "#E7EBF3",
  text: "#121826",
  textMuted: "#5B6478",
  textFaint: "#94A0B8",
  primary: "#1C4FC0",
  primaryBright: "#2A63E0",
  primaryDim: "#E7EEFF",
  success: "#1B9E56",
  successDim: "#E7F7EE",
  warning: "#B67506",
  warningDim: "#FBF0DA",
  critical: "#D42A34",
  criticalDim: "#FBE7E8",
  info: "#0E86C9",
  infoDim: "#E4F5FD",
};

const FONT_CSS = `
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
`;

/* ============================================================
   MOCK DATA
   ============================================================ */
const BUILDINGS = [
  { id: "BLD-A", name: "Skyline Tower A", location: "Nungambakkam, Chennai", elevators: 4 },
  { id: "BLD-B", name: "Horizon Business Park", location: "Whitefield, Bengaluru", elevators: 3 },
  { id: "BLD-C", name: "Marina Corporate Centre", location: "OMR, Chennai", elevators: 3 },
];

const ELEVATORS = [
  { id: "KONE-ELEV-001", buildingId: "BLD-A", building: "Skyline Tower A", floor: 8, dir: "up", status: "critical", health: 42, fault: "Bearing Degradation", risk: "High", speed: 1.6, load: 62, door: "closed", conn: "online", updated: "2 sec ago" },
  { id: "KONE-ELEV-002", buildingId: "BLD-A", building: "Skyline Tower A", floor: 3, dir: "down", status: "warning", health: 74, fault: "Door Alignment Drift", risk: "Medium", speed: 1.1, load: 40, door: "open", conn: "online", updated: "5 sec ago" },
  { id: "KONE-ELEV-003", buildingId: "BLD-A", building: "Skyline Tower A", floor: 12, dir: "idle", status: "healthy", health: 89, fault: null, risk: "Low", speed: 0, load: 18, door: "closed", conn: "online", updated: "1 sec ago" },
  { id: "KONE-ELEV-004", buildingId: "BLD-A", building: "Skyline Tower A", floor: 1, dir: "idle", status: "healthy", health: 92, fault: null, risk: "Low", speed: 0, load: 5, door: "open", conn: "online", updated: "3 sec ago" },
  { id: "KONE-ELEV-005", buildingId: "BLD-B", building: "Horizon Business Park", floor: 6, dir: "up", status: "warning", health: 68, fault: "Motor Temp Above Range", risk: "Medium", speed: 1.4, load: 71, door: "closed", conn: "online", updated: "4 sec ago" },
  { id: "KONE-ELEV-006", buildingId: "BLD-B", building: "Horizon Business Park", floor: 2, dir: "idle", status: "healthy", health: 95, fault: null, risk: "Low", speed: 0, load: 12, door: "closed", conn: "online", updated: "2 sec ago" },
  { id: "KONE-ELEV-007", buildingId: "BLD-B", building: "Horizon Business Park", floor: 15, dir: "down", status: "critical", health: 38, fault: "Motor Overheating", risk: "High", speed: 0.9, load: 84, door: "closed", conn: "online", updated: "1 sec ago" },
  { id: "KONE-ELEV-008", buildingId: "BLD-C", building: "Marina Corporate Centre", floor: 4, dir: "idle", status: "healthy", health: 90, fault: null, risk: "Low", speed: 0, load: 22, door: "open", conn: "online", updated: "6 sec ago" },
  { id: "KONE-ELEV-009", buildingId: "BLD-C", building: "Marina Corporate Centre", floor: 9, dir: "up", status: "healthy", health: 87, fault: null, risk: "Low", speed: 1.5, load: 55, door: "closed", conn: "online", updated: "3 sec ago" },
  { id: "KONE-ELEV-010", buildingId: "BLD-C", building: "Marina Corporate Centre", floor: 7, dir: "down", status: "warning", health: 71, fault: "Vibration Trending Up", risk: "Medium", speed: 1.2, load: 48, door: "closed", conn: "online", updated: "4 sec ago" },
];

const SENSOR_DEFS = [
  { key: "motorTemp", label: "Motor Temperature", unit: "°C", icon: Thermometer, normal: [40, 65], base: 78 },
  { key: "voltage", label: "Voltage", unit: "V", icon: Zap, normal: [380, 420], base: 402 },
  { key: "current", label: "Current", unit: "A", icon: Activity, normal: [10, 18], base: 19.4 },
  { key: "power", label: "Power Consumption", unit: "kW", icon: Gauge, normal: [4, 8], base: 7.6 },
  { key: "rpm", label: "Motor RPM", unit: "rpm", icon: RotateCcw, normal: [900, 1500], base: 1340 },
  { key: "vibration", label: "Vibration", unit: "mm/s", icon: Waves, normal: [0, 4.5], base: 6.8 },
  { key: "brake", label: "Brake Condition", unit: "%", icon: Disc3, normal: [80, 100], base: 88 },
  { key: "load", label: "Load Percentage", unit: "%", icon: Package, normal: [0, 90], base: 62 },
  { key: "humidity", label: "Humidity", unit: "%", icon: Droplets, normal: [30, 60], base: 47 },
  { key: "door", label: "Door Sensor", unit: "", icon: DoorClosed, normal: [0, 0], base: 0 },
];

function genSeries(base, points, spread) {
  const arr = [];
  for (let i = 0; i < points; i++) {
    const v = base + Math.sin(i * 0.4) * (spread * 0.2);
    arr.push({ t: i, v: Math.round(v * 10) / 10 });
  }
  return arr;
}

const FAULT_PROBS = [
  { name: "Bearing Failure", value: 94 },
  { name: "Motor Failure", value: 48 },
  { name: "Over Current", value: 22 },
  { name: "Brake Failure", value: 12 },
  { name: "Door Failure", value: 8 },
  { name: "Power Failure", value: 5 },
  { name: "Sensor Failure", value: 4 },
  { name: "Over Voltage", value: 3 },
  { name: "Under Voltage", value: 2 },
  { name: "Communication Failure", value: 1 },
];

const ROOT_CAUSE_CHAIN = [
  { label: "Abnormal Vibration", detail: "Vibration exceeded 4.5 mm/s threshold", sensor: "Vibration" },
  { label: "Motor Temperature Increased", detail: "Temperature rose 18% above baseline", sensor: "Motor Temp" },
  { label: "Current Consumption Increased", detail: "Current draw up 12% under equal load", sensor: "Current" },
  { label: "Bearing Wear Detected", detail: "Vibration + thermal + current signature matches wear model", sensor: "Fusion Model" },
  { label: "Root Cause Identified", detail: "Motor Bearing Wear — confidence 92%", sensor: "AI Engine" },
];

const CONTRIBUTING_FACTORS = [
  { label: "Vibration exceeded normal threshold", value: "6.8 mm/s vs 4.5 mm/s limit" },
  { label: "Motor temperature increased by 18%", value: "78°C vs 66°C baseline" },
  { label: "Current consumption increased by 12%", value: "19.4 A vs 17.3 A baseline" },
  { label: "RPM stability reduced", value: "±6.2% variance vs ±1.5% baseline" },
];

const PM_COMPONENTS = [
  { name: "Motor", health: 78, risk: "Low", rul: "180 Days", action: "Monitor — no action needed", icon: Cpu },
  { name: "Bearing", health: 42, risk: "High", rul: "12 Days", action: "Replace during next maintenance window", icon: Disc3 },
  { name: "Brake", health: 88, risk: "Low", rul: "220 Days", action: "Monitor — no action needed", icon: Disc3 },
  { name: "Door System", health: 65, risk: "Medium", rul: "45 Days", action: "Inspect alignment within 30 days", icon: DoorClosed },
  { name: "Controller", health: 91, risk: "Low", rul: "300 Days", action: "Monitor — no action needed", icon: Server },
  { name: "Drive System", health: 74, risk: "Medium", rul: "60 Days", action: "Schedule inspection next cycle", icon: Gauge },
];

const HEALTH_BREAKDOWN = {
  "KONE-ELEV-001": { motor: 78, bearing: 42, brake: 88, door: 76, electrical: 85, sensor: 93, drive: 79, overall: 71, summary: "Overall system health is stable. However, bearing degradation requires attention within the next 12 days." },
  "KONE-ELEV-003": { motor: 92, bearing: 88, brake: 94, door: 90, electrical: 91, sensor: 96, drive: 88, overall: 89, summary: "Overall system health is excellent. No components require immediate attention." },
  "KONE-ELEV-007": { motor: 51, bearing: 80, brake: 82, door: 85, electrical: 68, sensor: 90, drive: 77, overall: 65, summary: "Motor overheating is driving down overall health. Cooling system inspection recommended within 48 hours." },
};

const ALERTS = [
  { id: "AL-901", level: "critical", text: "Bearing failure risk is 94%", elevator: "KONE-ELEV-001", time: "2 min ago", read: false },
  { id: "AL-900", level: "critical", text: "Motor overheating detected", elevator: "KONE-ELEV-007", time: "6 min ago", read: false },
  { id: "AL-898", level: "warning", text: "Motor temperature above normal range", elevator: "KONE-ELEV-005", time: "18 min ago", read: false },
  { id: "AL-895", level: "warning", text: "Door alignment drift detected", elevator: "KONE-ELEV-002", time: "34 min ago", read: true },
  { id: "AL-891", level: "warning", text: "Vibration trending upward", elevator: "KONE-ELEV-010", time: "51 min ago", read: true },
  { id: "AL-888", level: "info", text: "Scheduled maintenance due tomorrow", elevator: "KONE-ELEV-004", time: "1 hr ago", read: true },
  { id: "AL-884", level: "info", text: "Edge gateway firmware update available", elevator: "System", time: "2 hr ago", read: true },
  { id: "AL-870", level: "resolved", text: "Brake pad wear resolved", elevator: "KONE-ELEV-006", time: "Yesterday", read: true },
];

const MAINT_TASKS = [
  { id: "MT-1042", elevator: "KONE-ELEV-001", building: "Skyline Tower A", fault: "Bearing Degradation", priority: "Critical", tech: "R. Karthik", date: "07 Sep 2026", status: "Scheduled" },
  { id: "MT-1041", elevator: "KONE-ELEV-007", building: "Horizon Business Park", fault: "Motor Overheating", priority: "Critical", tech: "S. Priya", date: "06 Sep 2026", status: "In Progress" },
  { id: "MT-1038", elevator: "KONE-ELEV-005", building: "Horizon Business Park", fault: "Temp Sensor Drift", priority: "Medium", tech: "D. Suresh", date: "09 Sep 2026", status: "Scheduled" },
  { id: "MT-1035", elevator: "KONE-ELEV-002", building: "Skyline Tower A", fault: "Door Alignment", priority: "High", tech: "A. Mohammed", date: "04 Sep 2026", status: "Overdue" },
  { id: "MT-1030", elevator: "KONE-ELEV-010", building: "Marina Corporate Centre", fault: "Vibration Inspection", priority: "Medium", tech: "V. Lakshmi", date: "10 Sep 2026", status: "Scheduled" },
  { id: "MT-1020", elevator: "KONE-ELEV-006", building: "Horizon Business Park", fault: "Brake Pad Wear", priority: "Low", tech: "V. Lakshmi", date: "28 Aug 2026", status: "Completed" },
  { id: "MT-1015", elevator: "KONE-ELEV-004", building: "Skyline Tower A", fault: "Routine Service", priority: "Low", tech: "A. Mohammed", date: "22 Aug 2026", status: "Completed" },
];

const TECHNICIANS = [
  { name: "R. Karthik", role: "Senior Maintenance Engineer", availability: "Available", current: 1, completed: 128, spec: "Motor & Drive Systems" },
  { name: "S. Priya", role: "Maintenance Engineer", availability: "On Task", current: 2, completed: 96, spec: "Electrical Systems" },
  { name: "A. Mohammed", role: "Technician", availability: "Available", current: 1, completed: 74, spec: "Door Systems" },
  { name: "V. Lakshmi", role: "Technician", availability: "On Task", current: 2, completed: 81, spec: "Brake Systems" },
  { name: "D. Suresh", role: "Senior Technician", availability: "Available", current: 1, completed: 103, spec: "Bearing & Vibration Analysis" },
];

const TIMELINE_EVENTS = [
  { time: "09:00", type: "info", title: "System Operating Normally", severity: "Info", sensor: "All Sensors", desc: "Baseline readings within normal operating range." },
  { time: "10:15", type: "warning", title: "Vibration Increased", severity: "Warning", sensor: "Vibration", desc: "Vibration rose from 2.1 mm/s to 4.9 mm/s over 20 minutes." },
  { time: "11:30", type: "warning", title: "Temperature Warning", severity: "Warning", sensor: "Motor Temperature", desc: "Motor temperature crossed 70°C, above the 65°C threshold." },
  { time: "12:10", type: "warning", title: "Current Consumption Increased", severity: "Warning", sensor: "Current", desc: "Current draw increased 12% under equivalent load conditions." },
  { time: "12:45", type: "critical", title: "Bearing Degradation Detected", severity: "Critical", sensor: "AI Fusion Model", desc: "Fault signature matched bearing wear pattern at 94% confidence." },
  { time: "13:00", type: "critical", title: "Critical Risk Alert Generated", severity: "Critical", sensor: "AI Engine", desc: "Elevator flagged for priority maintenance dispatch." },
];

const REPORTS = [
  { id: "RPT-2201", type: "Fault Analysis Report", elevator: "KONE-ELEV-001", date: "06 Sep 2026", status: "Ready" },
  { id: "RPT-2198", type: "Root Cause Analysis Report", elevator: "KONE-ELEV-007", date: "05 Sep 2026", status: "Ready" },
  { id: "RPT-2190", type: "Elevator Health Report", elevator: "Fleet-wide", date: "03 Sep 2026", status: "Ready" },
  { id: "RPT-2185", type: "Predictive Maintenance Report", elevator: "KONE-ELEV-001", date: "02 Sep 2026", status: "Ready" },
  { id: "RPT-2170", type: "Monthly Analytics Report", elevator: "All Buildings", date: "30 Aug 2026", status: "Ready" },
];

const AUDIT_LOG = [
  { time: "10:42:11", user: "R. Karthik", action: "Maintenance Task Created", elevator: "KONE-ELEV-001", status: "Success" },
  { time: "10:31:02", user: "AI Engine", action: "AI Analysis Started", elevator: "KONE-ELEV-001", status: "Success" },
  { time: "09:58:47", user: "S. Priya", action: "Technician Assigned", elevator: "KONE-ELEV-007", status: "Success" },
  { time: "09:20:15", user: "Admin", action: "Alert Threshold Updated", elevator: "System", status: "Success" },
  { time: "08:55:03", user: "V. Lakshmi", action: "Maintenance Completed", elevator: "KONE-ELEV-006", status: "Success" },
  { time: "08:12:40", user: "Manager", action: "Report Generated", elevator: "Fleet-wide", status: "Success" },
  { time: "07:45:22", user: "D. Suresh", action: "User Login", elevator: "—", status: "Success" },
];

const FAULT_TREND = [
  { d: "Mon", faults: 4 }, { d: "Tue", faults: 6 }, { d: "Wed", faults: 3 },
  { d: "Thu", faults: 8 }, { d: "Fri", faults: 5 }, { d: "Sat", faults: 2 }, { d: "Sun", faults: 3 },
];

const FAULT_MIX = [
  { name: "Bearing", value: 34 }, { name: "Motor", value: 22 }, { name: "Door", value: 18 },
  { name: "Electrical", value: 14 }, { name: "Sensor", value: 12 },
];

const NAV = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["Admin", "Maintenance Engineer", "Manager", "Technician"] },
  { id: "monitoring", label: "Live Monitoring", icon: Activity, roles: ["Admin", "Maintenance Engineer", "Technician"] },
  { id: "detection", label: "AI Fault Detection", icon: Brain, roles: ["Admin", "Maintenance Engineer"] },
  { id: "rootcause", label: "Root Cause Analysis", icon: GitBranch, roles: ["Admin", "Maintenance Engineer"] },
  { id: "predictive", label: "Predictive Maintenance", icon: TrendingUp, roles: ["Admin", "Maintenance Engineer", "Manager"] },
  { id: "health", label: "Elevator Health", icon: HeartPulse, roles: ["Admin", "Maintenance Engineer", "Manager", "Technician"] },
  { id: "analytics", label: "Analytics", icon: BarChart3, roles: ["Admin", "Manager"] },
  { id: "timeline", label: "Fault Timeline", icon: History, roles: ["Admin", "Maintenance Engineer"] },
  { id: "maintenance", label: "Maintenance", icon: Wrench, roles: ["Admin", "Maintenance Engineer", "Technician"] },
  { id: "technicians", label: "Technicians", icon: Users, roles: ["Admin", "Manager"] },
  { id: "reports", label: "Reports", icon: FileText, roles: ["Admin", "Maintenance Engineer", "Manager"] },
  { id: "assistant", label: "AI Assistant", icon: MessageSquare, roles: ["Admin", "Maintenance Engineer", "Manager", "Technician"] },
  { id: "buildings", label: "Buildings & Elevators", icon: Building2, roles: ["Admin", "Maintenance Engineer", "Manager"] },
  { id: "alerts", label: "Alerts & Notifications", icon: Bell, roles: ["Admin", "Maintenance Engineer", "Manager", "Technician"] },
  { id: "admin", label: "Admin Panel", icon: ShieldCheck, roles: ["Admin"] },
  { id: "settings", label: "Settings", icon: SettingsIcon, roles: ["Admin", "Maintenance Engineer", "Manager", "Technician"] },
];

/* ============================================================
   SMALL PRIMITIVES
   ============================================================ */
function useTheme(dark) {
  return dark ? C : LIGHT;
}

function StatusDot({ status, t }) {
  const map = { healthy: t.success, warning: t.warning, critical: t.critical, info: t.info };
  return <span style={{ width: 7, height: 7, borderRadius: 2, background: map[status] || t.textFaint, display: "inline-block", boxShadow: `0 0 6px ${map[status] || "transparent"}` }} />;
}

function StatusBadge({ status, t, label }) {
  const map = {
    healthy: { bg: t.successDim, fg: t.success, text: label || "Healthy" },
    warning: { bg: t.warningDim, fg: t.warning, text: label || "Warning" },
    critical: { bg: t.criticalDim, fg: t.critical, text: label || "Critical" },
    info: { bg: t.infoDim, fg: t.info, text: label || "Info" },
    resolved: { bg: t.surface3, fg: t.textMuted, text: label || "Resolved" },
  };
  const s = map[status] || map.info;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6, padding: "3px 9px",
      borderRadius: 4, fontSize: 11, fontWeight: 600, letterSpacing: 0.3,
      background: s.bg, color: s.fg, border: `1px solid ${s.fg}33`,
      fontFamily: "'IBM Plex Sans', sans-serif"
    }}>
      <StatusDot status={status} t={t} />{s.text}
    </span>
  );
}

function Card({ t, children, style, className, noPad }) {
  return (
    <div className={className} style={{
      background: t.surface, border: `1px solid ${t.border}`, borderRadius: 8,
      padding: noPad ? 0 : 18, ...style
    }}>
      {children}
    </div>
  );
}

function SectionTitle({ t, children, sub, right }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 14, gap: 12, flexWrap: "wrap" }}>
      <div>
        <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontWeight: 600, fontSize: 16, color: t.text, letterSpacing: 0.2 }}>{children}</div>
        {sub && <div style={{ fontSize: 12.5, color: t.textMuted, marginTop: 3 }}>{sub}</div>}
      </div>
      {right}
    </div>
  );
}

function Counter({ value, t, size = 30, suffix = "" }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    let raf, start;
    const dur = 700;
    function step(ts) {
      if (!start) start = ts;
      const p = Math.min(1, (ts - start) / dur);
      setN(Math.round(value * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(step);
    }
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [value]);
  return <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontWeight: 600, fontSize: size, color: t.text }}>{n}{suffix}</span>;
}

function KPICard({ t, label, value, suffix, delta, deltaGood, icon: Icon, accent }) {
  return (
    <Card t={t} style={{ display: "flex", flexDirection: "column", gap: 10, minWidth: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 11.5, color: t.textMuted, fontWeight: 600, letterSpacing: 0.3 }}>{label}</span>
        <div style={{ width: 26, height: 26, borderRadius: 6, background: (accent || t.primary) + "22", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Icon size={14} color={accent || t.primaryBright} />
        </div>
      </div>
      <Counter value={value} t={t} suffix={suffix} />
      {delta !== undefined && (
        <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11.5, color: deltaGood ? t.success : t.critical, fontWeight: 600 }}>
          {deltaGood ? <ArrowUp size={12} /> : <ArrowDown size={12} />}{delta}
        </div>
      )}
    </Card>
  );
}

function ProgressBar({ value, t, color, height = 6, track }) {
  return (
    <div style={{ width: "100%", height, borderRadius: 4, background: track || t.surface3, overflow: "hidden" }}>
      <div style={{ width: `${Math.min(100, Math.max(0, value))}%`, height: "100%", background: color, borderRadius: 4, transition: "width 0.6s ease" }} />
    </div>
  );
}

function healthColor(v, t) {
  if (v >= 80) return t.success;
  if (v >= 55) return t.warning;
  return t.critical;
}

function GaugeChart({ value, t, size = 150, label }) {
  const data = [{ v: value }];
  const color = healthColor(value, t);
  return (
    <div style={{ position: "relative", width: size, height: size * 0.62 }}>
      <ResponsiveContainer width="100%" height={size}>
        <RadialBarChart innerRadius="72%" outerRadius="100%" data={data} startAngle={180} endAngle={0} barSize={12}>
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar background={{ fill: t.surface3 }} dataKey="v" cornerRadius={6} fill={color} angleAxisId={0} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div style={{ position: "absolute", top: "48%", left: 0, right: 0, textAlign: "center" }}>
        <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: size * 0.19, fontWeight: 600, color: t.text }}>{value}</div>
        <div style={{ fontSize: 10.5, color: t.textMuted, marginTop: -2 }}>{label || "/ 100"}</div>
      </div>
    </div>
  );
}

function Sparkline({ data, color, t, height = 40 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id={`grad-${color.replace("#", "")}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.35} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area type="monotone" dataKey="v" stroke={color} strokeWidth={1.6} fill={`url(#grad-${color.replace("#", "")})`} dot={false} isAnimationActive={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

function ChartTooltip({ active, payload, label, t, unit }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div style={{ background: t.surface2, border: `1px solid ${t.border}`, borderRadius: 6, padding: "6px 10px", fontSize: 11.5, color: t.text, fontFamily: "'IBM Plex Mono', monospace" }}>
      {payload[0].value}{unit}
    </div>
  );
}

function RiskPill({ risk, t }) {
  const map = { High: t.critical, Medium: t.warning, Low: t.success };
  return <span style={{ color: map[risk] || t.textMuted, fontWeight: 600, fontSize: 12.5 }}>{risk}</span>;
}

/* ============================================================
   SIDEBAR + TOPBAR
   ============================================================ */
function Sidebar({ t, page, setPage, collapsed, setCollapsed, role }) {
  const items = NAV.filter(n => n.roles.includes(role));
  const disabledItems = NAV.filter(n => !n.roles.includes(role));
  return (
    <div style={{
      width: collapsed ? 68 : 244, minWidth: collapsed ? 68 : 244, background: t.surface,
      borderRight: `1px solid ${t.border}`, display: "flex", flexDirection: "column",
      transition: "width 0.2s ease, min-width 0.2s ease", height: "100vh", position: "sticky", top: 0
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "18px 16px", borderBottom: `1px solid ${t.borderSoft}`, minHeight: 60 }}>
        <div style={{ width: 30, height: 30, borderRadius: 6, background: `linear-gradient(135deg, ${t.primary}, ${t.primaryBright})`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <ArrowUp size={16} color="#fff" strokeWidth={2.5} />
        </div>
        {!collapsed && (
          <div style={{ overflow: "hidden" }}>
            <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontWeight: 700, fontSize: 14.5, color: t.text, whiteSpace: "nowrap" }}>ELEVATOR AI</div>
            <div style={{ fontSize: 10, color: t.textFaint, whiteSpace: "nowrap", letterSpacing: 0.4 }}>PREDICTIVE MAINTENANCE</div>
          </div>
        )}
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: "10px 8px" }}>
        {items.map(item => {
          const active = page === item.id;
          const Icon = item.icon;
          return (
            <button key={item.id} onClick={() => setPage(item.id)} title={collapsed ? item.label : undefined}
              style={{
                width: "100%", display: "flex", alignItems: "center", gap: 11, padding: "9px 11px",
                marginBottom: 2, borderRadius: 6, border: "none", cursor: "pointer",
                background: active ? t.primaryDim : "transparent",
                color: active ? t.primaryBright : t.textMuted,
                fontSize: 13, fontWeight: active ? 600 : 500, fontFamily: "'IBM Plex Sans', sans-serif",
                textAlign: "left", transition: "background 0.15s, color 0.15s",
                borderLeft: active ? `2px solid ${t.primaryBright}` : "2px solid transparent"
              }}
              onMouseEnter={e => { if (!active) e.currentTarget.style.background = t.surface2; }}
              onMouseLeave={e => { if (!active) e.currentTarget.style.background = "transparent"; }}
            >
              <Icon size={16} style={{ flexShrink: 0 }} />
              {!collapsed && <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.label}</span>}
            </button>
          );
        })}
        {!collapsed && disabledItems.length > 0 && (
          <div style={{ marginTop: 10, paddingTop: 10, borderTop: `1px solid ${t.borderSoft}` }}>
            <div style={{ fontSize: 9.5, color: t.textFaint, letterSpacing: 0.5, padding: "0 11px 6px" }}>RESTRICTED FOR {role.toUpperCase()}</div>
            {disabledItems.map(item => {
              const Icon = item.icon;
              return (
                <div key={item.id} style={{ display: "flex", alignItems: "center", gap: 11, padding: "9px 11px", color: t.textFaint, fontSize: 13, opacity: 0.5 }}>
                  <Icon size={16} /><span>{item.label}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
      <button onClick={() => setCollapsed(!collapsed)} style={{
        display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "12px",
        borderTop: `1px solid ${t.borderSoft}`, background: "transparent", border: "none", borderTopWidth: 1,
        borderTopStyle: "solid", borderTopColor: t.borderSoft, color: t.textMuted, cursor: "pointer", fontSize: 12
      }}>
        {collapsed ? <ChevronRight size={15} /> : <><ChevronLeft size={15} /> Collapse</>}
      </button>
    </div>
  );
}

function Topbar({ t, page, dark, setDark, buildings, building, setBuilding, elevators, elevator, setElevator, role, setRole, alertsUnread, onOpenAlerts, onOpenQR }) {
  const [roleOpen, setRoleOpen] = useState(false);
  const pageLabel = NAV.find(n => n.id === page)?.label || "Dashboard";
  return (
    <div style={{
      height: 64, minHeight: 64, borderBottom: `1px solid ${t.border}`, background: t.surface,
      display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 20px", gap: 16, position: "sticky", top: 0, zIndex: 20
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14, minWidth: 0 }}>
        <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontWeight: 600, fontSize: 15, color: t.text, whiteSpace: "nowrap" }}>{pageLabel}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, color: t.textFaint, fontSize: 12 }}>
          <Circle size={5} fill={t.textFaint} color={t.textFaint} />
          <span style={{ color: t.success, display: "flex", alignItems: "center", gap: 4 }}><Wifi size={12} /> All Systems Operational</span>
          <span style={{ background: t.primaryDim, border: `1px solid ${t.primaryBright}44`, borderRadius: 4, padding: "2px 6px", fontSize: 10.5, color: t.primaryBright, fontFamily: "'IBM Plex Mono', monospace", fontWeight: 600 }}>SIMULATION & DATASET REPLAY ACTIVE</span>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "nowrap", minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, background: t.surface2, border: `1px solid ${t.border}`, borderRadius: 6, padding: "6px 10px", minWidth: 160 }}>
          <Search size={13} color={t.textFaint} />
          <input placeholder="Search elevator, fault…" style={{ background: "transparent", border: "none", outline: "none", color: t.text, fontSize: 12.5, width: "100%" }} />
        </div>

        <select value={building} onChange={e => setBuilding(e.target.value)} style={selStyle(t)}>
          <option value="ALL">All Buildings</option>
          {buildings.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
        </select>

        <select value={elevator} onChange={e => setElevator(e.target.value)} style={selStyle(t)}>
          <option value="ALL">All Elevators</option>
          {elevators.map(e2 => <option key={e2.id} value={e2.id}>{e2.id}</option>)}
        </select>

        <button onClick={onOpenQR} title="Scan Elevator QR" style={iconBtn(t)}><QrCode size={16} /></button>
        <button onClick={() => setDark(!dark)} title="Toggle theme" style={iconBtn(t)}>{dark ? <Sun size={16} /> : <Moon size={16} />}</button>

        <button onClick={onOpenAlerts} title="Alerts" style={{ ...iconBtn(t), position: "relative" }}>
          <Bell size={16} />
          {alertsUnread > 0 && <span style={{ position: "absolute", top: 4, right: 4, width: 7, height: 7, borderRadius: "50%", background: t.critical, border: `1.5px solid ${t.surface}` }} />}
        </button>

        <div style={{ position: "relative" }}>
          <button onClick={() => setRoleOpen(!roleOpen)} style={{
            display: "flex", alignItems: "center", gap: 8, background: t.surface2, border: `1px solid ${t.border}`,
            borderRadius: 6, padding: "6px 10px", cursor: "pointer", color: t.text
          }}>
            <div style={{ width: 24, height: 24, borderRadius: "50%", background: `linear-gradient(135deg, ${t.primary}, ${t.info})`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10.5, fontWeight: 700, color: "#fff" }}>MK</div>
            <div style={{ textAlign: "left" }}>
              <div style={{ fontSize: 12, fontWeight: 600, lineHeight: 1.1 }}>Mohan K.</div>
              <div style={{ fontSize: 9.5, color: t.textFaint, lineHeight: 1.1 }}>{role}</div>
            </div>
            <ChevronDown size={13} color={t.textFaint} />
          </button>
          {roleOpen && (
            <div style={{ position: "absolute", right: 0, top: 42, background: t.surface2, border: `1px solid ${t.border}`, borderRadius: 8, width: 200, padding: 6, zIndex: 30, boxShadow: "0 12px 28px rgba(0,0,0,0.35)" }}>
              <div style={{ fontSize: 10, color: t.textFaint, padding: "6px 8px" }}>SWITCH ROLE (DEMO)</div>
              {["Admin", "Maintenance Engineer", "Manager", "Technician"].map(r => (
                <button key={r} onClick={() => { setRole(r); setRoleOpen(false); }} style={{
                  width: "100%", textAlign: "left", padding: "8px 8px", background: r === role ? t.primaryDim : "transparent",
                  color: r === role ? t.primaryBright : t.text, border: "none", borderRadius: 5, cursor: "pointer", fontSize: 12.5, marginBottom: 2
                }}>{r}</button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function selStyle(t) {
  return {
    background: t.surface2, border: `1px solid ${t.border}`, borderRadius: 6, color: t.text,
    fontSize: 12, padding: "7px 8px", outline: "none", maxWidth: 150
  };
}
function iconBtn(t) {
  return {
    width: 32, height: 32, borderRadius: 6, background: t.surface2, border: `1px solid ${t.border}`,
    color: t.textMuted, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", flexShrink: 0
  };
}

function primaryBtn(t) {
  return {
    display: "flex", alignItems: "center", gap: 6, padding: "7px 13px", borderRadius: 6, border: "none",
    background: `linear-gradient(120deg, ${t.primary}, ${t.primaryBright})`, color: "#fff",
    fontWeight: 600, fontSize: 12.5, cursor: "pointer", fontFamily: "'IBM Plex Sans', sans-serif"
  };
}

/* ============================================================
   SIMULATOR DEMO CONTROLS
   ============================================================ */
function SimulatorControlsBar({ t, elevatorId = "KONE-ELEV-001" }) {
  const [status, setStatus] = useState(null);
  const [scenario, setScenario] = useState("BEARING_DEGRADATION");
  const [speed, setSpeed] = useState(1);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(null);

  const refreshStatus = async () => {
    try {
      const res = await fetchSimulatorStatus();
      if (res) {
        setStatus(res);
        setApiError(null);
      }
    } catch (e) {
      // Keep existing status if transient poll fails
    }
  };

  useEffect(() => {
    refreshStatus();
    const iv = setInterval(refreshStatus, 1500);
    return () => clearInterval(iv);
  }, []);

  const handleStart = async () => {
    setLoading(true);
    setApiError(null);
    try {
      const res = await startSimulator({ elevatorId, scenario, replaySpeed: speed });
      if (res) {
        setStatus(res);
      } else {
        await refreshStatus();
      }
    } catch (e) {
      console.error("Start simulator error:", e);
      setApiError(e.message || "Failed to start simulator. Ensure backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  const handlePause = async () => {
    setLoading(true);
    setApiError(null);
    try {
      const res = await pauseSimulator();
      if (res) {
        setStatus(res);
      } else {
        await refreshStatus();
      }
    } catch (e) {
      console.error("Pause simulator error:", e);
      setApiError(e.message || "Failed to pause simulator.");
    } finally {
      setLoading(false);
    }
  };

  const handleResume = async () => {
    setLoading(true);
    setApiError(null);
    try {
      const currentState = status?.state;
      let res;
      if (currentState === "PAUSED") {
        try {
          res = await resumeSimulator();
        } catch (err) {
          res = await startSimulator({ elevatorId, scenario, replaySpeed: speed });
        }
      } else {
        res = await startSimulator({ elevatorId, scenario, replaySpeed: speed });
      }
      if (res) {
        setStatus(res);
      } else {
        await refreshStatus();
      }
    } catch (e) {
      console.error("Resume simulator error:", e);
      setApiError(e.message || "Failed to resume simulator.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    setApiError(null);
    try {
      const res = await resetSimulator();
      if (res) {
        setStatus(res);
      } else {
        await refreshStatus();
      }
    } catch (e) {
      console.error("Reset simulator error:", e);
      setApiError(e.message || "Failed to reset simulator.");
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioChange = async (e) => {
    const sc = e.target.value;
    setScenario(sc);
    setLoading(true);
    setApiError(null);
    try {
      const res = await setSimulatorScenario({ scenario: sc, elevatorId, replaySpeed: speed });
      if (res) {
        setStatus(res);
      } else {
        await refreshStatus();
      }
    } catch (err) {
      console.error("Scenario change error:", err);
      setApiError(err.message || "Failed to change scenario.");
    } finally {
      setLoading(false);
    }
  };

  const handleSpeedChange = async (e) => {
    const sp = Number(e.target.value);
    setSpeed(sp);
    if (status?.state === "RUNNING") {
      setLoading(true);
      setApiError(null);
      try {
        const res = await startSimulator({ elevatorId, scenario, replaySpeed: sp });
        if (res) setStatus(res);
      } catch (err) {
        console.error("Speed change error:", err);
        setApiError(err.message || "Failed to update speed.");
      } finally {
        setLoading(false);
      }
    }
  };

  const isRunning = status?.state === "RUNNING";
  const isPaused = status?.state === "PAUSED";
  const isCompleted = status?.state === "COMPLETED";
  const isIdle = !status || status?.state === "IDLE" || status?.state === "ERROR";

  return (
    <Card t={t} style={{ background: `linear-gradient(135deg, ${t.surface2}, ${t.surface})`, border: `1px solid ${apiError ? t.critical : t.primaryBright + "44"}`, marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 28, height: 28, borderRadius: 6, background: t.primaryDim, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Cpu size={15} color={t.primaryBright} />
          </div>
          <div>
            <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontWeight: 700, fontSize: 13.5, color: t.text }}>
              SIMULATOR CONTROLS
            </div>
            <div style={{ fontSize: 11, color: t.textMuted }}>
              Deterministic Telemetry Engine · Backend Single Source of Truth
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <select value={scenario} onChange={handleScenarioChange} disabled={loading} style={{ ...selStyle(t), maxWidth: 210, opacity: loading ? 0.7 : 1 }}>
            <option value="BEARING_DEGRADATION">Bearing Degradation</option>
            <option value="NORMAL">Normal Baseline</option>
            <option value="WARNING">Tool Wear Warning</option>
            <option value="MOTOR_OVERHEATING">Motor Overheating</option>
            <option value="DOOR_ALIGNMENT">Door Misalignment</option>
          </select>

          <select value={speed} onChange={handleSpeedChange} disabled={loading} style={{ ...selStyle(t), width: 70, opacity: loading ? 0.7 : 1 }}>
            <option value={0.5}>0.5x</option>
            <option value={1}>1.0x</option>
            <option value={2}>2.0x</option>
            <option value={5}>5.0x</option>
            <option value={10}>10x</option>
          </select>

          {(isIdle || isCompleted) && (
            <button onClick={handleStart} disabled={loading} style={{ ...primaryBtn(t), opacity: loading ? 0.7 : 1, cursor: loading ? "wait" : "pointer" }}>
              <Play size={13} /> {loading ? "Starting..." : isCompleted ? "Replay" : "Start"}
            </button>
          )}

          {isRunning && (
            <button onClick={handlePause} disabled={loading} style={{ ...iconBtn(t), width: 85, background: t.warningDim, color: t.warning, gap: 4, padding: "0 8px", opacity: loading ? 0.7 : 1, cursor: loading ? "wait" : "pointer" }}>
              <Pause size={13} /> {loading ? "..." : "Pause"}
            </button>
          )}

          {isPaused && (
            <>
              <button onClick={handleResume} disabled={loading} style={{ ...iconBtn(t), width: 90, background: t.successDim, color: t.success, gap: 4, padding: "0 8px", opacity: loading ? 0.7 : 1, cursor: loading ? "wait" : "pointer" }}>
                <Play size={13} /> {loading ? "..." : "Resume"}
              </button>
              <button onClick={handleStart} disabled={loading} style={{ ...primaryBtn(t), opacity: loading ? 0.7 : 1, cursor: loading ? "wait" : "pointer" }}>
                <RotateCcw size={13} /> Restart
              </button>
            </>
          )}

          <button onClick={handleReset} disabled={loading} style={{ ...iconBtn(t), opacity: loading ? 0.7 : 1 }} title="Reset Simulator"><RotateCcw size={13} /></button>

          <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 10px", background: t.surface3, borderRadius: 5, fontSize: 11, fontFamily: "'IBM Plex Mono', monospace" }}>
            <StatusDot status={isRunning ? "healthy" : isPaused ? "warning" : isCompleted ? "info" : "info"} t={t} />
            <span style={{ color: t.text }}>{status?.state || "IDLE"}</span>
            {status?.total_records > 0 && (
              <span style={{ color: t.textFaint }}>({status.records_emitted}/{status.total_records})</span>
            )}
            {isRunning && <span style={{ color: t.success, fontSize: 10 }}>● STREAMING</span>}
          </div>
        </div>
      </div>
      {apiError && (
        <div style={{ marginTop: 8, padding: "6px 12px", borderRadius: 4, background: `${t.critical}18`, border: `1px solid ${t.critical}44`, color: t.critical, fontSize: 11.5, fontFamily: "'IBM Plex Mono', monospace", display: "flex", alignItems: "center", gap: 6 }}>
          <span>⚠️ {apiError}</span>
        </div>
      )}
    </Card>
  );
}

/* ============================================================
   DASHBOARD PAGE
   ============================================================ */
function DashboardPage({ t, elevators, setPage, setSelectedElevator, now }) {
  const [fleetElevators, setFleetElevators] = useState(elevators);
  const [trendPoints, setTrendPoints] = useState([]);

  // 1. Initial load from API
  useEffect(() => {
    async function loadInitial() {
      try {
        const hist = await fetchSingleSensorHistory("KONE-ELEV-001", "vibration", 30);
        if (hist && hist.data) {
          const pts = hist.data.slice().reverse().map((pt, idx) => ({ t: idx, v: pt.value }));
          setTrendPoints(pts);
        }
      } catch (e) {
        // Fallback if API not running yet
      }
    }
    loadInitial();
  }, []);

  // 2. Subscribe to fleet-wide WebSockets
  useEffect(() => {
    const unsubscribe = connectFleetTelemetry((msg) => {
      const telem = msg.data;
      if (!telem || !telem.elevator_id) return;

      const elevId = telem.elevator_id;
      const vib = telem.vibration || 0;
      const temp = telem.motor_temp || 0;

      let newStatus = "healthy";
      let fault = null;
      let risk = "Low";
      let health = 92;

      if (vib > 15.0 || temp > 80.0) {
        newStatus = "critical";
        fault = temp > 80.0 ? "Motor Overheating" : "Bearing Degradation";
        risk = "High";
        health = Math.max(15, Math.round(100 - vib * 1.3));
      } else if (vib > 5.0 || temp > 68.0) {
        newStatus = "warning";
        fault = "Elevated Vibration / Temp";
        risk = "Medium";
        health = Math.max(45, Math.round(100 - vib * 1.8));
      }

      setFleetElevators((prev) =>
        prev.map((e) => {
          if (e.id === elevId) {
            return {
              ...e,
              status: newStatus,
              health,
              fault,
              risk,
              updated: "Just now",
            };
          }
          return e;
        })
      );

      if (elevId === "KONE-ELEV-001" && telem.vibration !== undefined) {
        setTrendPoints((prev) => {
          const next = [...prev, { t: prev.length, v: telem.vibration }];
          return next.slice(-40);
        });
      }
    });

    return () => unsubscribe();
  }, []);

  const total = fleetElevators.length;
  const healthy = fleetElevators.filter((e) => e.status === "healthy").length;
  const warning = fleetElevators.filter((e) => e.status === "warning").length;
  const critical = fleetElevators.filter((e) => e.status === "critical").length;
  const activeFaults = warning + critical;
  const avgHealth = Math.round(fleetElevators.reduce((a, e) => a + (e.health || 80), 0) / (total || 1));

  const fleetPie = [
    { name: "Healthy", value: healthy, color: t.success },
    { name: "Warning", value: warning, color: t.warning },
    { name: "Critical", value: critical, color: t.critical },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <SimulatorControlsBar t={t} elevatorId="KONE-ELEV-001" />

      <Card t={t} style={{ background: `linear-gradient(120deg, ${t.surface} 60%, ${t.primaryDim})`, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 14 }}>
        <div>
          <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontWeight: 700, fontSize: 22, color: t.text }}>Elevator Operations Intelligence</div>
          <div style={{ color: t.textMuted, fontSize: 13, marginTop: 4 }}>Real-time monitoring, AI-powered fault diagnosis and predictive maintenance.</div>
        </div>
        <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
          <MiniStat t={t} label="System Status" value="Operational" icon={CheckCircle2} color={t.success} />
          <MiniStat t={t} label="Connection" value="Live" icon={Wifi} color={t.info} pulse />
          <MiniStat t={t} label="Last Updated" value={now} icon={Clock} color={t.textMuted} mono />
        </div>
      </Card>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 14 }}>
        <KPICard t={t} label="TOTAL ELEVATORS" value={total} icon={Building2} />
        <KPICard t={t} label="HEALTHY" value={healthy} icon={CheckCircle2} accent={t.success} delta="Stable" deltaGood />
        <KPICard t={t} label="WARNING" value={warning} icon={AlertTriangle} accent={t.warning} />
        <KPICard t={t} label="CRITICAL" value={critical} icon={XCircle} accent={t.critical} delta="+1 today" deltaGood={false} />
        <KPICard t={t} label="ACTIVE FAULTS" value={activeFaults} icon={Zap} accent={t.warning} />
        <KPICard t={t} label="AVG FLEET HEALTH" value={avgHealth} suffix="%" icon={HeartPulse} accent={t.info} />
        <KPICard t={t} label="PREDICTED FAILURES" value={3} icon={Brain} accent={t.primaryBright} />
        <KPICard t={t} label="MAINTENANCE DUE" value={6} icon={Wrench} accent={t.warning} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr 1.3fr", gap: 14 }} className="responsive-grid-3">
        <Card t={t}>
          <SectionTitle t={t}>Overall Fleet Health</SectionTitle>
          <div style={{ display: "flex", justifyContent: "center" }}><GaugeChart value={avgHealth} t={t} size={170} label="FLEET AVG" /></div>
        </Card>
        <Card t={t}>
          <SectionTitle t={t}>Fleet Status</SectionTitle>
          <ResponsiveContainer width="100%" height={150}>
            <PieChart>
              <Pie data={fleetPie} dataKey="value" innerRadius={45} outerRadius={65} paddingAngle={3}>
                {fleetPie.map((e, i) => <Cell key={i} fill={e.color} stroke="none" />)}
              </Pie>
              <Tooltip content={<ChartTooltip t={t} />} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", justifyContent: "center", gap: 14, marginTop: -6, flexWrap: "wrap" }}>
            {fleetPie.map((e, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11.5, color: t.textMuted }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: e.color }} />{e.name} ({e.value})
              </div>
            ))}
          </div>
        </Card>
        <Card t={t}>
          <SectionTitle t={t}>Live Alerts</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 190, overflowY: "auto" }}>
            {ALERTS.slice(0, 5).map(a => (
              <div key={a.id} style={{ display: "flex", alignItems: "flex-start", gap: 8, fontSize: 12 }}>
                <StatusDot status={a.level === "resolved" ? "healthy" : a.level} t={t} />
                <div style={{ flex: 1 }}>
                  <div style={{ color: t.text }}>{a.text}</div>
                  <div style={{ color: t.textFaint, fontSize: 10.5 }}>{a.elevator} · {a.time}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: 14 }} className="responsive-grid-2">
        <Card t={t}>
          <SectionTitle t={t} sub="Real-time vibration stream from backend (mm/s)">Real-Time Sensor Trend</SectionTitle>
          <ResponsiveContainer width="100%" height={190}>
            <AreaChart data={trendPoints}>
              <defs>
                <linearGradient id="dashTrend" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={t.primaryBright} stopOpacity={0.35} />
                  <stop offset="100%" stopColor={t.primaryBright} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={t.borderSoft} vertical={false} />
              <XAxis dataKey="t" tick={{ fill: t.textFaint, fontSize: 10 }} axisLine={{ stroke: t.border }} tickLine={false} />
              <YAxis tick={{ fill: t.textFaint, fontSize: 10 }} axisLine={false} tickLine={false} width={28} />
              <Tooltip content={<ChartTooltip t={t} unit=" mm/s" />} />
              <Area type="monotone" dataKey="v" stroke={t.primaryBright} strokeWidth={2} fill="url(#dashTrend)" isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
        <Card t={t}>
          <SectionTitle t={t}>Recent Critical Faults</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {fleetElevators.filter(e => e.status === "critical").map(e => (
              <div key={e.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 10px", background: t.criticalDim, borderRadius: 6, border: `1px solid ${t.critical}33` }}>
                <div>
                  <div style={{ fontSize: 12.5, fontWeight: 600, color: t.text, fontFamily: "'IBM Plex Mono', monospace" }}>{e.id}</div>
                  <div style={{ fontSize: 11, color: t.textMuted }}>{e.fault}</div>
                </div>
                <RiskPill risk={e.risk} t={t} />
              </div>
            ))}
            <div style={{ fontSize: 11.5, color: t.textFaint, marginTop: 4 }}>AI predicts 3 additional components entering warning range within 14 days.</div>
          </div>
        </Card>
      </div>

      <Card t={t} noPad>
        <div style={{ padding: 18, paddingBottom: 0 }}>
          <SectionTitle t={t} sub="Click a row to open detailed monitoring">Fleet Overview</SectionTitle>
        </div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12.5 }}>
            <thead>
              <tr style={{ borderTop: `1px solid ${t.borderSoft}`, borderBottom: `1px solid ${t.borderSoft}` }}>
                {["Elevator ID", "Building", "Floor", "Status", "Health", "Active Fault", "Risk", "Updated"].map(h => (
                  <th key={h} style={{ textAlign: "left", padding: "10px 18px", color: t.textFaint, fontWeight: 600, fontSize: 10.5, letterSpacing: 0.3 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {fleetElevators.map(e => (
                <tr key={e.id} onClick={() => { setSelectedElevator(e.id); setPage("monitoring"); }}
                  style={{ borderBottom: `1px solid ${t.borderSoft}`, cursor: "pointer" }}
                  onMouseEnter={ev => ev.currentTarget.style.background = t.surface2}
                  onMouseLeave={ev => ev.currentTarget.style.background = "transparent"}
                >
                  <td style={{ padding: "10px 18px", fontFamily: "'IBM Plex Mono', monospace", color: t.text }}>{e.id}</td>
                  <td style={{ padding: "10px 18px", color: t.textMuted }}>{e.building}</td>
                  <td style={{ padding: "10px 18px", color: t.textMuted }}>{e.floor}</td>
                  <td style={{ padding: "10px 18px" }}><StatusBadge status={e.status} t={t} /></td>
                  <td style={{ padding: "10px 18px", width: 110 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{ width: 50 }}><ProgressBar value={e.health} t={t} color={healthColor(e.health, t)} /></div>
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", color: t.text, fontSize: 11.5 }}>{e.health}%</span>
                    </div>
                  </td>
                  <td style={{ padding: "10px 18px", color: t.textMuted }}>{e.fault || "—"}</td>
                  <td style={{ padding: "10px 18px" }}><RiskPill risk={e.risk} t={t} /></td>
                  <td style={{ padding: "10px 18px", color: t.textFaint, fontSize: 11 }}>{e.updated}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <ArchitectureCard t={t} />
    </div>
  );
}

function MiniStat({ t, label, value, icon: Icon, color, pulse, mono }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ width: 30, height: 30, borderRadius: 6, background: color + "22", display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
        <Icon size={14} color={color} />
        {pulse && <span className="pulse-dot" style={{ position: "absolute", top: -2, right: -2, width: 7, height: 7, borderRadius: "50%", background: color }} />}
      </div>
      <div>
        <div style={{ fontSize: 10, color: t.textFaint }}>{label}</div>
        <div style={{ fontSize: 12.5, fontWeight: 600, color: t.text, fontFamily: mono ? "'IBM Plex Mono', monospace" : "inherit" }}>{value}</div>
      </div>
    </div>
  );
}

function ArchitectureCard({ t }) {
  const layers = [
    { icon: RadioTower, label: "Sensors", sub: "Motor, vibration, thermal, load" },
    { icon: Cpu, label: "STM32", sub: "Data acquisition & real-time processing" },
    { icon: Server, label: "Raspberry Pi", sub: "Edge gateway & local processing" },
    { icon: Brain, label: "FastAPI / AI Engine", sub: "Fault detection & analytics" },
    { icon: Database, label: "PostgreSQL", sub: "Time-series & event storage" },
    { icon: MonitorSmartphone, label: "React Dashboard", sub: "Intelligence & visualization" },
  ];
  return (
    <Card t={t}>
      <SectionTitle t={t} sub="Future hardware-to-cloud integration path">System Architecture</SectionTitle>
      <div style={{ display: "flex", alignItems: "center", overflowX: "auto", gap: 4, paddingBottom: 4 }}>
        {layers.map((l, i) => (
          <React.Fragment key={i}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, minWidth: 128 }}>
              <div style={{ width: 42, height: 42, borderRadius: 8, background: t.surface2, border: `1px solid ${t.border}`, display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
                <l.icon size={18} color={t.primaryBright} />
                <span className="pulse-dot" style={{ position: "absolute", bottom: -2, right: -2, width: 8, height: 8, borderRadius: "50%", background: t.success, border: `2px solid ${t.surface}` }} />
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: 11.5, fontWeight: 600, color: t.text }}>{l.label}</div>
                <div style={{ fontSize: 9.5, color: t.textFaint, maxWidth: 120 }}>{l.sub}</div>
              </div>
            </div>
            {i < layers.length - 1 && <ArrowRight size={14} color={t.textFaint} style={{ flexShrink: 0 }} />}
          </React.Fragment>
        ))}
      </div>
    </Card>
  );
}

function formatTimeLabel(ts, index) {
  if (!ts) return index !== undefined ? `T+${index}` : "Now";
  try {
    const d = new Date(ts);
    if (!isNaN(d.getTime())) {
      const hh = String(d.getHours()).padStart(2, "0");
      const mm = String(d.getMinutes()).padStart(2, "0");
      const ss = String(d.getSeconds()).padStart(2, "0");
      return `${hh}:${mm}:${ss}`;
    }
  } catch (e) {}
  return String(ts);
}

function SensorMiniCard({ def, t, liveValue, historySeries, activeSensor, setActiveSensor, wsSeq }) {
  const val = typeof liveValue === "number" ? liveValue : def.base;
  const out = val < def.normal[0] || val > def.normal[1];
  const color = out ? (val > def.normal[1] * 1.3 ? t.critical : t.warning) : t.success;
  const isActive = activeSensor === def.key;

  // Always produce ≥2 data points so Recharts draws a visible line not just a dot.
  const sparkData = useMemo(() => {
    const base = (historySeries && historySeries.length > 0)
      ? historySeries.slice(-30).map((pt, idx) => ({ t: pt.t !== undefined ? pt.t : idx, v: pt.v !== undefined ? pt.v : pt.value }))
      : [{ t: 0, v: val }];
    if (base.length === 1) return [base[0], { t: base[0].t + 1, v: base[0].v }];
    return base;
  // wsSeq is intentionally in deps to re-derive when new WS data arrives
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [historySeries, val, wsSeq]);

  return (
    <Card
      t={t}
      style={{
        cursor: "pointer",
        outline: isActive ? `2px solid ${t.primaryBright}` : `1px solid ${t.border}`,
        borderColor: isActive ? t.primaryBright : t.border,
        boxShadow: isActive ? `0 0 14px ${t.primaryBright}33` : "none",
        transition: "all 0.15s ease",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: "14px 16px"
      }}
      className="sensor-card"
    >
      <div onClick={() => setActiveSensor(def.key)} style={{ display: "flex", flexDirection: "column", height: "100%" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 7, color: isActive ? t.primaryBright : t.textMuted, fontSize: 12, fontWeight: 600 }}>
            <def.icon size={15} color={isActive ? t.primaryBright : t.textMuted} />
            <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{def.label}</span>
          </div>
          <StatusDot status={out ? (color === t.critical ? "critical" : "warning") : "healthy"} t={t} />
        </div>

        <div style={{ display: "flex", alignItems: "baseline", gap: 5, marginBottom: 2 }}>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 22, fontWeight: 600, color: t.text, lineHeight: 1 }}>
            {typeof val === "number" ? val.toFixed(1) : val}
          </span>
          <span style={{ fontSize: 11, color: t.textFaint, fontWeight: 500 }}>{def.unit}</span>
        </div>

        <div style={{ fontSize: 10.5, color: t.textFaint, marginBottom: 8 }}>
          Normal: {def.normal[0]}–{def.normal[1]} {def.unit}
        </div>

        <div style={{ marginTop: "auto" }}>
          <Sparkline data={sparkData} color={color} t={t} height={34} />
        </div>
      </div>
    </Card>
  );
}

function mapSensorKeyToBackend(key) {
  const map = {
    motorTemp: "motor_temp",
    voltage: "voltage",
    current: "current",
    power: "power",
    rpm: "rpm",
    vibration: "vibration",
    brake: "brake",
    load: "load",
    humidity: "humidity",
    door: "door",
  };
  return map[key] || key;
}

/* ============================================================
   LIVE MONITORING PAGE
   ============================================================ */
// History is kept in a module-level Map so it persists across re-renders
// and sensor-tab switches without being wiped by useEffect dependencies.
const _telemetryHistory = new Map(); // elevatorId → { sensorKey: [{t, v}] }

function _getHistory(elevatorId, sensorKey) {
  if (!_telemetryHistory.has(elevatorId)) _telemetryHistory.set(elevatorId, {});
  const byElevator = _telemetryHistory.get(elevatorId);
  if (!byElevator[sensorKey]) byElevator[sensorKey] = [];
  return byElevator[sensorKey];
}

function _appendHistory(elevatorId, sensorKey, point, maxPoints = 120) {
  const hist = _getHistory(elevatorId, sensorKey);
  hist.push(point);
  if (hist.length > maxPoints) hist.splice(0, hist.length - maxPoints);
}

function MonitoringPage({ t, elevators, selectedElevator, setSelectedElevator, tick }) {
  const [range, setRange] = useState("1H");
  const [activeSensor, setActiveSensor] = useState("motorTemp");
  const [liveSensors, setLiveSensors] = useState({});
  const [loadingHistory, setLoadingHistory] = useState(false);
  // render trigger — increment to force re-render when WS data arrives
  const [wsSeq, setWsSeq] = useState(0);
  const wsSeqRef = useRef(0);

  const elevator = elevators.find(e => e.id === selectedElevator) || elevators[0];
  const activeSensorDef = SENSOR_DEFS.find(s => s.key === activeSensor) || SENSOR_DEFS[0];

  // ─── 1. Seed default base values on mount ────────────────────────────────
  useEffect(() => {
    // Populate with base values so cards show something immediately
    const defaults = {};
    SENSOR_DEFS.forEach(def => { defaults[def.key] = def.base; });
    setLiveSensors(prev => ({ ...defaults, ...prev }));
  }, []);

  // ─── 2. Load historical readings from API when elevator or sensor changes ─
  useEffect(() => {
    let cancelled = false;
    async function loadHistory() {
      if (!selectedElevator) return;
      setLoadingHistory(true);
      try {
        const backendKey = mapSensorKeyToBackend(activeSensor);
        const rangeLimitMap = { "1H": 60, "6H": 120, "24H": 240, "7D": 500 };
        const limit = rangeLimitMap[range] || 60;
        const hist = await fetchSingleSensorHistory(selectedElevator, backendKey, limit);
        if (!cancelled && hist && Array.isArray(hist.data) && hist.data.length > 0) {
          // Clear existing history for this sensor and seed with API data
          const byElev = _telemetryHistory.get(selectedElevator) || {};
          byElev[activeSensor] = hist.data.slice().reverse().map((pt, idx) => ({
            t: idx,
            v: typeof pt.value === "number" ? Math.round(pt.value * 10) / 10 : pt.value,
          }));
          _telemetryHistory.set(selectedElevator, byElev);
          wsSeqRef.current++;
          setWsSeq(wsSeqRef.current);
        }
      } catch (_) {
        // API unavailable — WS data will populate
      } finally {
        if (!cancelled) setLoadingHistory(false);
      }
    }
    loadHistory();
    return () => { cancelled = true; };
  }, [selectedElevator, activeSensor, range]);

  // ─── 3. Load latest sensor values from API ────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    async function loadLatest() {
      try {
        const latest = await fetchLatestSensors(selectedElevator);
        if (latest && !cancelled) {
          setLiveSensors({
            motorTemp: latest.motor_temp,
            voltage: latest.voltage,
            current: latest.current,
            power: latest.power,
            rpm: latest.rpm,
            vibration: latest.vibration,
            brake: latest.brake,
            load: latest.load,
            humidity: latest.humidity,
            door: latest.door,
          });
        }
      } catch (_) {}
    }
    loadLatest();
    return () => { cancelled = true; };
  }, [selectedElevator]);

  // ─── 4. WebSocket: stream live telemetry ─────────────────────────────────
  useEffect(() => {
    const unsubscribe = connectElevatorTelemetry(selectedElevator, (msg) => {
      // Backend manager.broadcast_elevator_telemetry wraps our data arg as:
      //   { type: "telemetry", elevator_id, data: <broadcast_data> }
      // After the fix, broadcast_data = { motor_temp, voltage, ..., ai, timestamp }
      // But handle both old (nested) and new (flat) structures.
      const outer = msg.data;
      if (!outer) return;

      // Determine where sensor values actually are
      const sd = (outer.data && typeof outer.data === "object" && outer.data.motor_temp !== undefined)
        ? outer.data   // old nested structure
        : outer;       // new flat structure (after backend fix)

      const ts = outer.timestamp || sd.timestamp;
      const now = Date.now();

      // Use a monotonic sequence index for the X-axis (guarantees Recharts
      // draws a connected line regardless of timestamp format).
      const seqIdx = now;

      const incoming = {
        motorTemp: sd.motor_temp,
        voltage:   sd.voltage,
        current:   sd.current,
        power:     sd.power,
        rpm:       sd.rpm,
        vibration: sd.vibration,
        brake:     sd.brake,
        load:      sd.load,
        humidity:  sd.humidity,
        door:      sd.door,
      };

      // Filter out undefined values
      const valid = Object.fromEntries(Object.entries(incoming).filter(([, v]) => v !== undefined && v !== null));
      if (Object.keys(valid).length === 0) {
        console.warn("[WS] Received telemetry with no sensor values. msg.data =", msg.data);
        return;
      }

      console.log("[WS] telemetry received:", valid);

      // Append each sensor reading to the module-level history
      Object.entries(valid).forEach(([feKey, val]) => {
        if (typeof val === "number") {
          _appendHistory(selectedElevator, feKey, { t: seqIdx, v: Math.round(val * 10) / 10 });
        }
      });

      // Update live sensor display values
      setLiveSensors(prev => ({ ...prev, ...valid }));

      // Trigger a re-render so charts update
      wsSeqRef.current++;
      setWsSeq(wsSeqRef.current);
    });

    return () => unsubscribe();
  }, [selectedElevator]);

  // ─── Derived series for the detail chart ─────────────────────────────────
  // Read from shared module-level history; always fresh.
  const bigSeries = (() => {
    const hist = _getHistory(selectedElevator, activeSensor);
    if (hist.length === 0) {
      // Seed with current live value so chart is never empty
      const v = liveSensors[activeSensor] ?? activeSensorDef.base;
      return [{ t: 0, v }, { t: 1, v }]; // 2 identical pts = flat line not blank
    }
    if (hist.length === 1) {
      return [hist[0], { ...hist[0], t: hist[0].t + 1 }];
    }
    return hist;
  })();

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SimulatorControlsBar t={t} elevatorId={selectedElevator} />

      <Card t={t} style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
        <div style={{ display: "flex", gap: 22, flexWrap: "wrap", alignItems: "center" }}>
          <div>
            <div style={{ fontSize: 10.5, color: t.textFaint }}>ELEVATOR ID</div>
            <select value={selectedElevator} onChange={e => setSelectedElevator(e.target.value)} style={{ ...selStyle(t), fontFamily: "'IBM Plex Mono', monospace", fontSize: 14, fontWeight: 600, padding: "4px 6px", marginTop: 2 }}>
              {elevators.map(e => <option key={e.id} value={e.id}>{e.id}</option>)}
            </select>
          </div>
          <Field t={t} label="Building" value={elevator.building} />
          <Field t={t} label="Current Floor" value={elevator.floor} mono />
          <Field t={t} label="Direction" value={elevator.dir === "up" ? "Ascending" : elevator.dir === "down" ? "Descending" : "Idle"} icon={elevator.dir === "up" ? <ArrowUp size={13} color={t.info} /> : elevator.dir === "down" ? <ArrowDown size={13} color={t.info} /> : null} />
          <Field t={t} label="Speed" value={`${elevator.speed} m/s`} mono />
          <Field t={t} label="Door Status" value={elevator.door === "open" ? "Open" : "Closed"} icon={elevator.door === "open" ? <DoorOpen size={13} color={t.warning} /> : <DoorClosed size={13} color={t.success} />} />
          <Field t={t} label="Connection" value="Online" icon={<Wifi size={13} color={t.success} />} />
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
          <GaugeChart value={elevator.health} t={t} size={100} label="HEALTH" />
          <StatusBadge status={elevator.status} t={t} />
        </div>
      </Card>

      <div>
        <SectionTitle t={t} sub="Live telemetry feed — click any card to see detailed trend">Live Sensor Feed</SectionTitle>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 14, alignItems: "stretch" }}>
          {SENSOR_DEFS.filter(s => s.key !== "door").map(def => (
            <SensorMiniCard
              key={def.key}
              def={def}
              t={t}
              liveValue={liveSensors[def.key]}
              historySeries={_getHistory(selectedElevator, def.key)}
              activeSensor={activeSensor}
              setActiveSensor={setActiveSensor}
              wsSeq={wsSeq}
            />
          ))}
        </div>
      </div>

      <Card t={t}>
        <SectionTitle t={t} right={
          <div style={{ display: "flex", gap: 6 }}>
            {["1H", "6H", "24H", "7D"].map(r => (
              <button key={r} onClick={() => setRange(r)} style={{
                padding: "5px 11px", fontSize: 11.5, borderRadius: 5, cursor: "pointer",
                background: range === r ? t.primaryDim : "transparent", color: range === r ? t.primaryBright : t.textMuted,
                border: `1px solid ${range === r ? t.primaryBright : t.border}`,
                fontWeight: range === r ? 600 : 400
              }}>{r}</button>
            ))}
          </div>
        }>
          {activeSensorDef.label} — Detailed Trend ({activeSensorDef.unit || ""}) · {bigSeries.length} pts
        </SectionTitle>

        {loadingHistory ? (
          <div style={{ height: 260, display: "flex", alignItems: "center", justifyContent: "center", color: t.textMuted, fontSize: 13 }}>
            <span className="spinner" style={{ marginRight: 8 }} /> Loading sensor history…
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={bigSeries} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid stroke={t.borderSoft} vertical={false} strokeDasharray="3 3" />
              <XAxis dataKey="t" hide={true} />
              <YAxis tick={{ fill: t.textFaint, fontSize: 10, fontFamily: "'IBM Plex Mono', monospace" }} axisLine={false} tickLine={false} width={50} tickFormatter={v => `${v}${activeSensorDef.unit}`} domain={["auto", "auto"]} />
              <Tooltip content={<ChartTooltip t={t} unit={` ${activeSensorDef.unit}`} />} />
              <Line
                type="monotone"
                dataKey="v"
                stroke={t.primaryBright}
                strokeWidth={2.5}
                dot={bigSeries.length < 5 ? { r: 4, fill: t.primaryBright, strokeWidth: 0 } : false}
                activeDot={{ r: 5, fill: t.primaryBright, stroke: t.surface, strokeWidth: 2 }}
                isAnimationActive={false}
                connectNulls={true}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </Card>
    </div>
  );
}

function Field({ t, label, value, icon, mono }) {
  return (
    <div>
      <div style={{ fontSize: 10.5, color: t.textFaint }}>{label.toUpperCase()}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 13, color: t.text, fontWeight: 600, marginTop: 2, fontFamily: mono ? "'IBM Plex Mono', monospace" : "inherit" }}>
        {icon}{value}
      </div>
    </div>
  );
}

/* ============================================================
   AI FAULT DETECTION PAGE
   ============================================================ */
function DetectionPage({ t, selectedElevator }) {
  const [running, setRunning] = useState(false);
  const [detectionData, setDetectionData] = useState(null);
  const [evalMetrics, setEvalMetrics] = useState(null);
  const [showEval, setShowEval] = useState(false);

  // Phase 7 Snapdragon AI & Hardware state
  const [aiStatus, setAiStatus] = useState(null);
  const [benchmark, setBenchmark] = useState(null);
  const [benchmarking, setBenchmarking] = useState(false);
  const [devices, setDevices] = useState([]);

  const runAnalysis = async () => {
    setRunning(true);
    try {
      const data = await triggerAIDetection(selectedElevator);
      setDetectionData(data);
    } catch (e) {
      // Fallback
    } finally {
      setRunning(false);
    }
  };

  const loadAIStatusAndDevices = async () => {
    try {
      const st = await fetchAIStatus();
      setAiStatus(st);
    } catch (e) {}
    try {
      const devs = await fetchRegisteredDevices();
      setDevices(devs);
    } catch (e) {}
  };

  useEffect(() => {
    runAnalysis();
    loadAIStatusAndDevices();
  }, [selectedElevator]);

  const loadEvaluation = async () => {
    try {
      const ev = await fetchMLEvaluation();
      setEvalMetrics(ev);
      setShowEval(!showEval);
    } catch (e) {}
  };

  const handleRunBenchmark = async () => {
    setBenchmarking(true);
    try {
      const bm = await runAIBenchmark(100);
      setBenchmark(bm);
    } catch (e) {}
    finally {
      setBenchmarking(false);
    }
  };

  const confidencePct = detectionData ? Math.round(detectionData.confidence * 100) : 94;
  const isFault = detectionData ? detectionData.fault_detected : true;
  const faultName = detectionData ? detectionData.fault_type : "Bearing Degradation";
  const severity = detectionData ? detectionData.severity : "critical";
  const modelName = detectionData ? detectionData.model : "RandomForestClassifier + IsolationForest";
  const latencyMs = detectionData ? detectionData.inference_time_ms : 3.8;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Card t={t} style={{ background: `linear-gradient(120deg, ${t.surface}, ${t.primaryDim})`, display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 14, alignItems: "center" }}>
        <div>
          <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontWeight: 700, fontSize: 19, color: t.text }}>AI Fault Detection Engine</div>
          <div style={{ display: "flex", gap: 18, marginTop: 10, flexWrap: "wrap" }}>
            <Field t={t} label="Model Engine" value={modelName} icon={<CheckCircle2 size={13} color={t.success} />} />
            <Field t={t} label="Confidence" value={`${confidencePct}%`} mono />
            <Field t={t} label="Inference Latency" value={`${latencyMs} ms`} mono />
            <Field t={t} label="Status" value={isFault ? "Fault Detected" : "Nominal"} />
          </div>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button onClick={loadEvaluation} style={{
            display: "flex", alignItems: "center", gap: 6, padding: "10px 14px", borderRadius: 7,
            border: `1px solid ${t.border}`, background: t.surface2, color: t.textMuted, fontSize: 12, cursor: "pointer"
          }}>
            <FileBarChart2 size={14} /> ML Evaluation
          </button>
          <button onClick={runAnalysis} disabled={running} style={{
            display: "flex", alignItems: "center", gap: 8, padding: "11px 18px", borderRadius: 7, border: "none",
            background: running ? t.surface3 : `linear-gradient(120deg, ${t.primary}, ${t.primaryBright})`, color: "#fff",
            fontWeight: 600, fontSize: 13, cursor: running ? "default" : "pointer"
          }}>
            {running ? <><span className="spinner" /> Analysing…</> : <><Sparkles size={15} /> Run AI Analysis</>}
          </button>
        </div>
      </Card>

      {showEval && evalMetrics && (
        <Card t={t} style={{ border: `1px solid ${t.primaryBright}55` }}>
          <SectionTitle t={t} sub={`Evaluated on ${evalMetrics.dataset_name} (${evalMetrics.samples_total} samples)`}>
            True ML Benchmark Evaluation Metrics
          </SectionTitle>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 12, marginTop: 10 }}>
            <KPICard t={t} label="ACCURACY" value={(evalMetrics.accuracy * 100).toFixed(1)} suffix="%" icon={CheckCircle2} accent={t.success} />
            <KPICard t={t} label="PRECISION" value={(evalMetrics.precision * 100).toFixed(1)} suffix="%" icon={Brain} accent={t.info} />
            <KPICard t={t} label="RECALL" value={(evalMetrics.recall * 100).toFixed(1)} suffix="%" icon={Activity} accent={t.primaryBright} />
            <KPICard t={t} label="F1 SCORE" value={(evalMetrics.f1_score * 100).toFixed(1)} suffix="%" icon={Sparkles} accent={t.warning} />
            <KPICard t={t} label="RUL MAE" value={evalMetrics.rul_metrics.mae_hours} suffix=" hrs" icon={Clock} />
            <KPICard t={t} label="RUL RMSE" value={evalMetrics.rul_metrics.rmse_hours} suffix=" hrs" icon={Clock} />
          </div>
        </Card>
      )}

      {running && (
        <Card t={t} style={{ textAlign: "center", padding: 32 }}>
          <div className="spinner-lg" style={{ margin: "0 auto 14px" }} />
          <div style={{ color: t.text, fontWeight: 600 }}>Analysing sensor fusion data for {selectedElevator}…</div>
          <div style={{ color: t.textFaint, fontSize: 12, marginTop: 4 }}>Cross-referencing vibration, thermal and electrical signatures against trained fault models.</div>
        </Card>
      )}

      {!running && isFault && (
        <Card t={t} style={{ border: `1px solid ${severity === "critical" ? t.critical : t.warning}55`, background: severity === "critical" ? t.criticalDim : t.warningDim }}>
          <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 14 }}>
            <div style={{ display: "flex", gap: 12 }}>
              <div style={{ width: 42, height: 42, borderRadius: 8, background: (severity === "critical" ? t.critical : t.warning) + "22", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <AlertTriangle size={20} color={severity === "critical" ? t.critical : t.warning} />
              </div>
              <div>
                <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontWeight: 700, fontSize: 16, color: t.text }}>{faultName.toUpperCase()} DETECTED</div>
                <div style={{ fontSize: 12, color: t.textMuted, marginTop: 3 }}>Real-time ML inference identified signature in live telemetry stream.</div>
              </div>
            </div>
            <StatusBadge status={severity} t={t} label={`Confidence ${confidencePct}%`} />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12, marginTop: 16 }}>
            <Field t={t} label="Severity" value={severity.toUpperCase()} />
            <Field t={t} label="Classification Model" value={modelName} />
            <Field t={t} label="Elevator ID" value={selectedElevator} mono />
            <Field t={t} label="Inference Speed" value={`${latencyMs} ms`} mono />
          </div>
        </Card>
      )}

      <Card t={t}>
        <SectionTitle t={t} sub="Probability that each fault category explains current sensor behaviour">Fault Category Probabilities</SectionTitle>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[
            { name: "Bearing Degradation", value: faultName.includes("Bearing") ? confidencePct : 12 },
            { name: "Motor Overheating", value: faultName.includes("Motor") ? confidencePct : 8 },
            { name: "Door Alignment Drift", value: faultName.includes("Door") ? confidencePct : 4 },
            { name: "Healthy Operational State", value: !isFault ? 96 : 5 },
          ].map(f => (
            <div key={f.name}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12.5, marginBottom: 4 }}>
                <span style={{ color: t.text }}>{f.name}</span>
                <span style={{ color: t.textMuted, fontFamily: "'IBM Plex Mono', monospace" }}>{f.value}%</span>
              </div>
              <ProgressBar value={f.value} t={t} color={f.value > 70 ? t.critical : f.value > 30 ? t.warning : t.primaryBright} height={7} />
            </div>
          ))}
        </div>
      </Card>

      {/* PHASE 7: Snapdragon Local AI + Hardware Acceleration Status & Benchmark */}
      <Card t={t} style={{ border: `1px solid ${t.primaryBright}44`, background: `linear-gradient(135deg, ${t.surface}, ${t.surface2})` }}>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 12, alignItems: "center" }}>
          <div>
            <SectionTitle t={t} sub="Hardware-accelerated ONNX Runtime & Edge Execution Diagnostics">
              Snapdragon Local AI & Edge Hardware Architecture
            </SectionTitle>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginTop: 8 }}>
              <Field t={t} label="Device Target" value={aiStatus?.device || "CPU"} icon={<Cpu size={13} color={t.primaryBright} />} />
              <Field t={t} label="Execution Provider" value={aiStatus?.accelerator || "CPUExecutionProvider (Fallback)"} mono />
              <Field t={t} label="ONNX Model" value={aiStatus?.model || "fault_detector.onnx"} />
              <Field t={t} label="Acceleration" value={aiStatus?.acceleration_available ? "Active NPU/GPU" : "CPU Fallback"} />
            </div>
          </div>
          <button
            onClick={handleRunBenchmark}
            disabled={benchmarking}
            style={{
              display: "flex", alignItems: "center", gap: 8, padding: "10px 16px", borderRadius: 6,
              background: benchmarking ? t.surface3 : t.primaryBright, color: "#000", fontWeight: 700,
              fontSize: 12.5, border: "none", cursor: benchmarking ? "default" : "pointer"
            }}
          >
            {benchmarking ? <><span className="spinner" /> Running 100 Pass Micro-Benchmark…</> : <><Zap size={14} /> Run AI Hardware Benchmark</>}
          </button>
        </div>

        {aiStatus?.fallback_reason && (
          <div style={{ marginTop: 12, padding: "10px 12px", background: `${t.warning}15`, border: `1px solid ${t.warning}44`, borderRadius: 6, fontSize: 11.5, color: t.warning }}>
            <strong>Execution Status Note:</strong> {aiStatus.fallback_reason}
          </div>
        )}

        {/* Benchmark Results Display */}
        {benchmark && (
          <div style={{ marginTop: 16, paddingTop: 14, borderTop: `1px solid ${t.border}` }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: t.text, marginBottom: 10, letterSpacing: "0.5px" }}>
              LIVE HARDWARE MICRO-BENCHMARK RESULTS (100 PASSES)
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 10 }}>
              <KPICard t={t} label="CPU LATENCY" value={benchmark.cpu_latency_ms} suffix=" ms" icon={Clock} />
              <KPICard t={t} label="ACCELERATED" value={benchmark.accelerated_latency_ms !== null ? benchmark.accelerated_latency_ms : "N/A (CPU)"} suffix={benchmark.accelerated_latency_ms !== null ? " ms" : ""} icon={Zap} accent={t.primaryBright} />
              <KPICard t={t} label="THROUGHPUT" value={benchmark.throughput_ops_sec} suffix=" ops/s" icon={Activity} accent={t.success} />
              <KPICard t={t} label="MEMORY RSS" value={benchmark.memory_mb} suffix=" MB" icon={HardDrive} />
              <KPICard t={t} label="MODEL SIZE" value={benchmark.model_size_kb} suffix=" KB" icon={Layers} />
              <KPICard t={t} label="CONSISTENCY" value={benchmark.prediction_consistency_pct} suffix="%" icon={CheckCircle2} accent={t.info} />
            </div>
          </div>
        )}

        {/* Connected Edge Devices Topology */}
        <div style={{ marginTop: 16, paddingTop: 14, borderTop: `1px solid ${t.border}` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: t.text }}>CONNECTED EDGE HARDWARE NODES & GATEWAYS</div>
            <div style={{ fontSize: 11, color: t.textFaint, fontFamily: "'IBM Plex Mono', monospace" }}>{devices.length} Nodes Registered</div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
            {devices.map(d => (
              <div key={d.device_id} style={{ padding: "8px 12px", background: t.surface2, borderRadius: 6, border: `1px solid ${t.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontWeight: 700, fontSize: 12, color: t.text }}>{d.device_id}</div>
                  <div style={{ fontSize: 10.5, color: t.textMuted }}>{d.device_type} • {d.firmware_version || 'v2.1.0'}</div>
                </div>
                <StatusBadge status={d.status === "online" ? "healthy" : "warning"} t={t} label={d.status?.toUpperCase()} />
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}

/* ============================================================
   ROOT CAUSE ANALYSIS PAGE
   ============================================================ */
function RootCausePage({ t, selectedElevator }) {
  const [rcaData, setRcaData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRCA() {
      setLoading(true);
      try {
        const data = await fetchRCA(selectedElevator);
        setRcaData(data);
      } catch (e) {
        // Fallback
      } finally {
        setLoading(false);
      }
    }
    loadRCA();
  }, [selectedElevator]);

  const rootCauseText = rcaData ? rcaData.root_cause : "Sub-surface fatigue & inner-race roller bearing spalling in main drive gear assembly.";
  const componentText = rcaData ? rcaData.affected_component : "Main Drive Shaft Bearing Assembly (SKF-6208)";
  const confidence = rcaData ? Math.round(rcaData.confidence * 100) : 92;
  const factors = rcaData && rcaData.contributing_factors ? rcaData.contributing_factors : [];
  const steps = rcaData && rcaData.verification_steps ? rcaData.verification_steps : [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SectionTitle t={t} sub={`AI Root Cause investigation trace for ${selectedElevator}`}>AI Root Cause Analysis (RCA)</SectionTitle>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 14 }} className="responsive-grid-2">
        <Card t={t}>
          <SectionTitle t={t}>Root Cause Result</SectionTitle>
          <div style={{ fontSize: 11, color: t.textFaint }}>PRIMARY ROOT CAUSE</div>
          <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontSize: 18, fontWeight: 700, color: t.text, marginTop: 2 }}>{rootCauseText}</div>
          <div style={{ display: "flex", gap: 20, marginTop: 12, flexWrap: "wrap" }}>
            <div>
              <div style={{ fontSize: 10.5, color: t.textFaint }}>AFFECTED COMPONENT</div>
              <div style={{ fontSize: 13, color: t.text, fontWeight: 600 }}>{componentText}</div>
            </div>
            <div>
              <div style={{ fontSize: 10.5, color: t.textFaint }}>CONFIDENCE</div>
              <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 18, color: t.text, fontWeight: 600 }}>{confidence}%</div>
            </div>
          </div>
        </Card>
        <Card t={t}>
          <SectionTitle t={t}>Contributing Factors</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {factors.map((f, i) => (
              <div key={i} style={{ display: "flex", gap: 8 }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: f.severity === "critical" ? t.critical : t.warning, marginTop: 6, flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: 12.5, color: t.text, fontWeight: 600 }}>{f.factor}</div>
                  <div style={{ fontSize: 11.5, color: t.textMuted }}>{f.impact}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card t={t}>
        <SectionTitle t={t}>Actionable Verification & Repair Steps</SectionTitle>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {steps.map((step, idx) => (
            <div key={idx} style={{ padding: "10px 14px", background: t.surface2, borderRadius: 6, border: `1px solid ${t.border}`, fontSize: 13, color: t.text }}>
              {step}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function MiniTimeline({ t }) {
  return (
    <div style={{ display: "flex", overflowX: "auto", gap: 0, paddingBottom: 6 }}>
      {TIMELINE_EVENTS.map((e, i) => (
        <div key={i} style={{ display: "flex", alignItems: "flex-start", minWidth: 168 }}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginRight: 8 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: e.type === "critical" ? t.critical : e.type === "warning" ? t.warning : t.info, flexShrink: 0 }} />
            {i < TIMELINE_EVENTS.length - 1 && <div style={{ width: 2, flex: 1, minHeight: 40, background: t.border }} />}
          </div>
          <div style={{ paddingBottom: 16 }}>
            <div style={{ fontSize: 10.5, color: t.textFaint, fontFamily: "'IBM Plex Mono', monospace" }}>{e.time}</div>
            <div style={{ fontSize: 12, fontWeight: 600, color: t.text }}>{e.title}</div>
            <div style={{ fontSize: 10.5, color: t.textMuted, maxWidth: 150 }}>{e.sensor}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ============================================================
   PREDICTIVE MAINTENANCE PAGE
   ============================================================ */
function PredictivePage({ t, selectedElevator }) {
  const [predData, setPredData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPredictive() {
      setLoading(true);
      try {
        const data = await fetchPredictiveStatus(selectedElevator || "KONE-ELEV-001");
        setPredData(data);
      } catch (e) {
      } finally {
        setLoading(false);
      }
    }
    loadPredictive();
  }, [selectedElevator]);

  const failureRisk = predData ? predData.failure_risk : 58.0;
  const rulHours = predData ? predData.rul_hours : 144.0;
  const priority = predData ? predData.priority : "High";
  const action = predData ? predData.recommended_action : "Schedule technician intervention within 48 hours for main drive overhaul.";
  const compHealth = predData && predData.component_health ? predData.component_health : { motor: 78, bearing: 42, door: 92, brake: 88, electrical: 95 };

  const components = [
    { name: "Motor Winding", health: compHealth.motor || 78, rul: `${Math.round(rulHours * 1.5)} hrs`, risk: priority, action: action, icon: Thermometer },
    { name: "Bearing Assembly", health: compHealth.bearing || 42, rul: `${Math.round(rulHours)} hrs`, risk: priority, action: action, icon: Waves },
    { name: "Brake Mechanism", health: compHealth.brake || 88, rul: "1,200 hrs", risk: "Low", action: "Routine check during next service interval.", icon: Disc3 },
    { name: "Door Interlock", health: compHealth.door || 92, rul: "2,100 hrs", risk: "Low", action: "Clean sill track & adjust door rollers.", icon: DoorClosed },
  ];

  const sorted = [...components].sort((a, b) => a.health - b.health);
  const rulSeries = [
    { d: "Today", v: Math.round(rulHours) },
    { d: "+24h", v: Math.max(0, Math.round(rulHours * 0.85)) },
    { d: "+48h", v: Math.max(0, Math.round(rulHours * 0.65)) },
    { d: "+72h", v: Math.max(0, Math.round(rulHours * 0.40)) },
    { d: "+96h", v: Math.max(0, Math.round(rulHours * 0.10)) },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SectionTitle t={t} sub={`Component-level health forecasting and remaining useful life for ${selectedElevator || 'Fleet'}`}>Predictive Maintenance Intelligence</SectionTitle>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: 14 }}>
        {components.map(c => (
          <Card key={c.name} t={t}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ width: 30, height: 30, borderRadius: 6, background: t.primaryDim, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <c.icon size={15} color={t.primaryBright} />
                </div>
                <span style={{ fontWeight: 600, color: t.text, fontSize: 13.5 }}>{c.name}</span>
              </div>
              <RiskPill risk={c.risk} t={t} />
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginTop: 12 }}>
              <div>
                <div style={{ fontSize: 10, color: t.textFaint }}>HEALTH</div>
                <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 22, fontWeight: 600, color: healthColor(c.health, t) }}>{c.health}%</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 10, color: t.textFaint }}>RUL</div>
                <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 15, fontWeight: 600, color: t.text }}>{c.rul}</div>
              </div>
            </div>
            <ProgressBar value={c.health} t={t} color={healthColor(c.health, t)} height={6} />
            <div style={{ fontSize: 11, color: t.textMuted, marginTop: 8 }}>{c.action}</div>
          </Card>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }} className="responsive-grid-2">
        <Card t={t}>
          <SectionTitle t={t} sub="RUL Degradation Curve Projection">Remaining Useful Life (RUL) Trajectory</SectionTitle>
          <ResponsiveContainer width="100%" height={190}>
            <LineChart data={rulSeries}>
              <CartesianGrid stroke={t.borderSoft} vertical={false} />
              <XAxis dataKey="d" tick={{ fill: t.textFaint, fontSize: 10.5 }} axisLine={{ stroke: t.border }} tickLine={false} />
              <YAxis tick={{ fill: t.textFaint, fontSize: 10.5 }} axisLine={false} tickLine={false} width={32} />
              <Tooltip content={<ChartTooltip t={t} unit=" hrs" />} />
              <Line type="monotone" dataKey="v" stroke={t.critical} strokeWidth={2.2} dot={{ r: 3, fill: t.critical }} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
        <Card t={t}>
          <SectionTitle t={t} sub="Ranked by urgency across active subsystem">AI Action Recommendations</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {sorted.map((c, i) => (
              <div key={c.name} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", background: t.surface2, borderRadius: 6 }}>
                <div style={{ fontFamily: "'IBM Plex Mono', monospace", color: t.textFaint, fontSize: 11, width: 16 }}>{i + 1}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12.5, color: t.text, fontWeight: 600 }}>{c.name}</div>
                  <div style={{ fontSize: 10.5, color: t.textFaint }}>{c.action}</div>
                </div>
                <RiskPill risk={c.risk} t={t} />
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

/* ============================================================
   ELEVATOR HEALTH PAGE
   ============================================================ */
function HealthPage({ t, elevators, selectedElevator, setSelectedElevator }) {
  const [span, setSpan] = useState("7 Days");
  const [healthRecord, setHealthRecord] = useState(null);

  useEffect(() => {
    async function loadHealth() {
      try {
        const h = await fetchElevatorHealth(selectedElevator || "KONE-ELEV-001");
        setHealthRecord(h);
      } catch (e) {}
    }
    loadHealth();
  }, [selectedElevator]);

  const overall = healthRecord ? healthRecord.overall_health : 78.5;
  const status = healthRecord ? healthRecord.status : "healthy";
  const comps = healthRecord && healthRecord.components ? healthRecord.components : { motor: 85, bearing: 62, door: 94, brake: 88, electrical: 95 };

  const rows = [
    { label: "Motor Health", v: comps.motor },
    { label: "Bearing Health", v: comps.bearing },
    { label: "Brake Health", v: comps.brake },
    { label: "Door Health", v: comps.door },
    { label: "Electrical Health", v: comps.electrical },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10 }}>
        <SectionTitle t={t}>Overall Elevator Health Score</SectionTitle>
        <select value={selectedElevator} onChange={e => setSelectedElevator(e.target.value)} style={selStyle(t)}>
          {elevators.map(e => <option key={e.id} value={e.id}>{e.id}</option>)}
        </select>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.4fr", gap: 14 }} className="responsive-grid-2">
        <Card t={t} style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10 }}>
          <GaugeChart value={overall} t={t} size={200} label={status.toUpperCase()} />
          <StatusBadge status={status} t={t} />
        </Card>
        <Card t={t}>
          <SectionTitle t={t}>Explainable Component Breakdown</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {rows.map(r => (
              <div key={r.label}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12.5, marginBottom: 4 }}>
                  <span style={{ color: t.text }}>{r.label}</span>
                  <span style={{ color: t.textMuted, fontFamily: "'IBM Plex Mono', monospace" }}>{r.v}%</span>
                </div>
                <ProgressBar value={r.v} t={t} color={healthColor(r.v, t)} />
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

/* ============================================================
   ANALYTICS PAGE
   ============================================================ */
function AnalyticsPage({ t }) {
  const [buildingF, setBuildingF] = useState("ALL");
  const [summary, setSummary] = useState(null);
  const [faultDist, setFaultDist] = useState([]);
  const [faultTrends, setFaultTrends] = useState([]);
  const pieColors = [t.critical, t.warning, t.info, t.primaryBright, t.success];

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const sumData = await fetchAnalyticsSummary(buildingF);
        setSummary(sumData);
        const distData = await fetchFaultDistribution(buildingF);
        setFaultDist(distData);
        const trendData = await fetchFaultTrends();
        setFaultTrends(trendData);
      } catch (e) {
        console.error("Analytics fetch error:", e);
      }
    }
    loadAnalytics();
  }, [buildingF]);

  const availability = summary ? `${summary.fleet_availability}%` : "98.6%";
  const downtime = summary ? `${summary.downtime_hours} hrs` : "2.4 hrs";
  const avgHealth = summary ? `${summary.avg_health_score}%` : "78.5%";
  const totalElevators = summary ? summary.total_elevators : 10;

  const pieData = faultDist.length > 0
    ? faultDist.map(d => ({ name: d.fault, value: d.count }))
    : [
        { name: "Bearing Degradation", value: 4 },
        { name: "Motor Overheating", value: 3 },
        { name: "Door Alignment", value: 2 },
      ];

  const barData = faultTrends.length > 0
    ? faultTrends.map(t => ({ d: t.day, faults: (t["Bearing Degradation"] || 0) + (t["Motor Overheating"] || 0) }))
    : FAULT_TREND;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Card t={t}>
        <SectionTitle t={t}>Fleet Analytics Filters</SectionTitle>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <select style={selStyle(t)} value={buildingF} onChange={e => setBuildingF(e.target.value)}>
            <option value="ALL">All Buildings</option>
            {BUILDINGS.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
      </Card>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12 }}>
        <MetricCard t={t} label="Total Managed Fleet" value={totalElevators} mono />
        <MetricCard t={t} label="Avg Fleet Health" value={avgHealth} mono />
        <MetricCard t={t} label="Fleet Availability" value={availability} mono />
        <MetricCard t={t} label="Est. Downtime" value={downtime} mono />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: 14 }} className="responsive-grid-2">
        <Card t={t}>
          <SectionTitle t={t} sub="Daily fault count across fleet">Fault Trends</SectionTitle>
          <ResponsiveContainer width="100%" height={210}>
            <BarChart data={barData}>
              <CartesianGrid stroke={t.borderSoft} vertical={false} />
              <XAxis dataKey="d" tick={{ fill: t.textFaint, fontSize: 11 }} axisLine={{ stroke: t.border }} tickLine={false} />
              <YAxis tick={{ fill: t.textFaint, fontSize: 11 }} axisLine={false} tickLine={false} width={24} />
              <Tooltip content={<ChartTooltip t={t} />} />
              <Bar dataKey="faults" fill={t.primaryBright} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card t={t}>
          <SectionTitle t={t} sub="Share of faults by category">Fault Mix</SectionTitle>
          <ResponsiveContainer width="100%" height={170}>
            <PieChart>
              <Pie data={pieData} dataKey="value" innerRadius={38} outerRadius={62} paddingAngle={3}>
                {pieData.map((e, i) => <Cell key={i} fill={pieColors[i % pieColors.length]} />)}
              </Pie>
              <Tooltip content={<ChartTooltip t={t} unit=" faults" />} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center", marginTop: -4 }}>
            {pieData.map((e, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 10.5, color: t.textMuted }}>
                <span style={{ width: 7, height: 7, borderRadius: 2, background: pieColors[i % pieColors.length] }} />{e.name}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function MetricCard({ t, label, value, mono }) {
  return (
    <Card t={t}>
      <div style={{ fontSize: 10.5, color: t.textFaint, marginBottom: 6 }}>{label.toUpperCase()}</div>
      <div style={{ fontFamily: mono ? "'IBM Plex Mono', monospace" : "'Chakra Petch', sans-serif", fontWeight: 700, fontSize: 18, color: t.text }}>{value}</div>
    </Card>
  );
}

/* ============================================================
   FAULT TIMELINE / REPLAY PAGE
   ============================================================ */
function TimelinePage({ t, selectedElevator }) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    async function loadTimeline() {
      try {
        const evts = await fetchFaultTimeline(selectedElevator || "ALL");
        setEvents(evts);
      } catch (e) {}
    }
    loadTimeline();
  }, [selectedElevator]);

  const timelineList = events.length > 0 ? events : [
    { id: "EVT-01", time: "14:32:05", type: "critical", severity: "Critical", title: "AI Bearing Degradation Detected", desc: "Random Forest Classifier triggered with 97% confidence.", sensor: "vibration_rms: 8.17 mm/s" },
    { id: "EVT-02", time: "14:32:08", type: "warning", severity: "Warning", title: "Root Cause Evidence Formulated", desc: "SKF-6208 bearing wear identified as root cause.", sensor: "motor_temp_slope: +3.7 °C/step" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SectionTitle t={t} sub={`Event timeline sequence for ${selectedElevator || 'Fleet'}`}>Database-Backed Fault Timeline</SectionTitle>
      <Card t={t}>
        <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
          {timelineList.map((e, i) => (
            <div key={e.id || i} style={{ display: "flex", gap: 14 }}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <div style={{
                  width: 14, height: 14, borderRadius: "50%", flexShrink: 0,
                  background: e.type === "critical" ? t.critical : e.type === "warning" ? t.warning : t.info,
                }} />
                {i < timelineList.length - 1 && <div style={{ width: 2, flex: 1, minHeight: 46, background: t.border }} />}
              </div>
              <div style={{ paddingBottom: 22 }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11.5, color: t.textFaint }}>{e.time}</span>
                  <StatusBadge status={e.type || "info"} t={t} label={e.category || e.severity || "Event"} />
                </div>
                <div style={{ fontWeight: 600, fontSize: 13.5, color: t.text, marginTop: 4 }}>{e.title}</div>
                <div style={{ fontSize: 12, color: t.textMuted, marginTop: 2 }}>{e.details || e.desc}</div>
                <div style={{ fontSize: 10.5, color: t.textFaint, marginTop: 2 }}>Sensor: {e.sensor}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

/* ============================================================
   MAINTENANCE PAGE
   ============================================================ */
function MaintenancePage({ t, selectedElevator }) {
  const [tab, setTab] = useState("Scheduled");
  const [tasks, setTasks] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newFault, setNewFault] = useState("Bearing Degradation");
  const [newPriority, setNewPriority] = useState("High");
  const tabs = ["Scheduled", "In Progress", "Completed", "Overdue"];

  const loadTasks = async () => {
    try {
      const data = await fetchMaintenanceTasks("All", selectedElevator || "ALL");
      setTasks(data);
    } catch (e) {}
  };

  useEffect(() => {
    loadTasks();
  }, [selectedElevator]);

  const handleCreate = async () => {
    if (!newTitle) return;
    try {
      await createMaintenanceTask({
        elevator_id: selectedElevator || "KONE-ELEV-001",
        title: newTitle,
        fault_type: newFault,
        priority: newPriority,
      });
      setShowCreate(false);
      setNewTitle("");
      loadTasks();
    } catch (e) {}
  };

  const markComplete = async (id) => {
    try {
      await completeMaintenanceTask(id);
      loadTasks();
    } catch (e) {}
  };

  const filtered = tasks.filter(m => m.status === tab);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10 }}>
        <SectionTitle t={t}>Maintenance Command Center</SectionTitle>
        <button onClick={() => setShowCreate(true)} style={primaryBtn(t)}><Plus size={14} /> Create Task</button>
      </div>

      <div style={{ display: "flex", gap: 6, borderBottom: `1px solid ${t.border}` }}>
        {tabs.map(tb => (
          <button key={tb} onClick={() => setTab(tb)} style={{
            padding: "9px 14px", fontSize: 12.5, background: "transparent", border: "none", cursor: "pointer",
            color: tab === tb ? t.primaryBright : t.textMuted, fontWeight: tab === tb ? 600 : 500,
            borderBottom: tab === tb ? `2px solid ${t.primaryBright}` : "2px solid transparent", marginBottom: -1
          }}>{tb} ({tasks.filter(m => m.status === tb).length})</button>
        ))}
      </div>

      <Card t={t} noPad>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12.5 }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${t.borderSoft}` }}>
                {["Task ID", "Elevator", "Fault", "Priority", "Technician", "Due Date", "Status", "Action"].map(h => (
                  <th key={h} style={{ textAlign: "left", padding: "10px 16px", color: t.textFaint, fontWeight: 600, fontSize: 10.5 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 && (
                <tr><td colSpan={8} style={{ padding: 30, textAlign: "center", color: t.textFaint }}>No {tab.toLowerCase()} tasks.</td></tr>
              )}
              {filtered.map(m => (
                <tr key={m.id} style={{ borderBottom: `1px solid ${t.borderSoft}` }}>
                  <td style={{ padding: "10px 16px", fontFamily: "'IBM Plex Mono', monospace", color: t.text }}>{m.id}</td>
                  <td style={{ padding: "10px 16px", fontFamily: "'IBM Plex Mono', monospace", color: t.textMuted }}>{m.elevator_id}</td>
                  <td style={{ padding: "10px 16px", color: t.textMuted }}>{m.fault_type || m.title}</td>
                  <td style={{ padding: "10px 16px" }}><RiskPill risk={m.priority} t={t} /></td>
                  <td style={{ padding: "10px 16px", color: t.text }}>{m.technician_name || "Unassigned"}</td>
                  <td style={{ padding: "10px 16px", color: t.textMuted, fontFamily: "'IBM Plex Mono', monospace" }}>{m.due_date ? new Date(m.due_date).toLocaleDateString() : 'Pending'}</td>
                  <td style={{ padding: "10px 16px" }}>
                    <StatusBadge status={m.status === "Completed" ? "healthy" : m.status === "Overdue" ? "critical" : m.status === "In Progress" ? "info" : "warning"} t={t} label={m.status} />
                  </td>
                  <td style={{ padding: "10px 16px" }}>
                    {m.status !== "Completed" && (
                      <button onClick={() => markComplete(m.id)} style={{ fontSize: 11, padding: "5px 9px", borderRadius: 5, border: `1px solid ${t.border}`, background: t.surface2, color: t.text, cursor: "pointer" }}>Complete</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {showCreate && (
        <Modal t={t} onClose={() => setShowCreate(false)} title="Create Maintenance Task">
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div>
              <label style={{ fontSize: 11, color: t.textMuted }}>Task Title</label>
              <input value={newTitle} onChange={e => setNewTitle(e.target.value)} placeholder="e.g. SKF Bearing Unit Replacement" style={{ width: "100%", padding: "8px 10px", background: t.surface2, border: `1px solid ${t.border}`, borderRadius: 6, color: t.text, marginTop: 4 }} />
            </div>
            <div>
              <label style={{ fontSize: 11, color: t.textMuted }}>Fault Classification</label>
              <select value={newFault} onChange={e => setNewFault(e.target.value)} style={{ ...selStyle(t), width: "100%", marginTop: 4 }}>
                <option>Bearing Degradation</option>
                <option>Motor Overheating</option>
                <option>Door Alignment Drift</option>
                <option>Preventive Inspection</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: 11, color: t.textMuted }}>Priority</label>
              <select value={newPriority} onChange={e => setNewPriority(e.target.value)} style={{ ...selStyle(t), width: "100%", marginTop: 4 }}>
                <option>Low</option>
                <option>Medium</option>
                <option>High</option>
                <option>Critical</option>
              </select>
            </div>
            <button onClick={handleCreate} style={{ ...primaryBtn(t), justifyContent: "center", marginTop: 10 }}>Submit & Auto-Assign Technician</button>
          </div>
        </Modal>
      )}
    </div>
  );
}



/* ============================================================
   TECHNICIANS PAGE
   ============================================================ */
function TechniciansPage({ t, selectedElevator }) {
  const [techs, setTechs] = useState([]);
  const [recommendation, setRecommendation] = useState(null);

  useEffect(() => {
    async function loadTechs() {
      try {
        const list = await fetchTechnicians();
        setTechs(list);
        const rec = await recommendTechnician(selectedElevator || "KONE-ELEV-001", "Bearing Degradation");
        setRecommendation(rec);
      } catch (e) {}
    }
    loadTechs();
  }, [selectedElevator]);

  const techList = techs.length > 0 ? techs : [
    { name: "D. Suresh", role_title: "Senior Drive Systems Lead", specialization: "Vibration Analysis & Bearing Systems", availability: "Available", active_workload: 1, completed_count: 14 },
    { name: "A. Mohammed", role_title: "Door Mechanism Specialist", specialization: "Optical Sensors & Track Alignment", availability: "Available", active_workload: 2, completed_count: 9 },
    { name: "R. Karthik", role_title: "Motor & Inverter Specialist", specialization: "Thermal Dynamics & Stator Windings", availability: "Available", active_workload: 1, completed_count: 18 },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SectionTitle t={t}>Technician Management & Recommendation Engine</SectionTitle>

      {recommendation && (
        <Card t={t} style={{ display: "flex", gap: 14, alignItems: "flex-start", background: t.infoDim, border: `1px solid ${t.info}44` }}>
          <UserCheck size={22} color={t.info} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <div style={{ fontWeight: 600, color: t.text, fontSize: 13.5 }}>
              AI Recommended Technician: {recommendation.recommended_technician?.name || "R. Karthik"} (Score: {recommendation.match_score?.toFixed(0)}%)
            </div>
            <div style={{ fontSize: 12, color: t.textMuted, marginTop: 2 }}>
              {recommendation.explanation}
            </div>
          </div>
        </Card>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: 14 }}>
        {techList.map(tc => (
          <Card key={tc.name} t={t}>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <div style={{ width: 38, height: 38, borderRadius: "50%", background: `linear-gradient(135deg, ${t.primary}, ${t.info})`, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 700, fontSize: 13 }}>
                {tc.name.split(" ").map(w => w[0]).join("")}
              </div>
              <div>
                <div style={{ fontWeight: 600, color: t.text, fontSize: 13.5 }}>{tc.name}</div>
                <div style={{ fontSize: 11, color: t.textFaint }}>{tc.role_title || tc.role}</div>
              </div>
            </div>
            <div style={{ marginTop: 10 }}><StatusBadge status={tc.availability === "Available" ? "healthy" : "info"} t={t} label={tc.availability} /></div>
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10, fontSize: 11.5 }}>
              <span style={{ color: t.textMuted }}>Active Workload: <b style={{ color: t.text }}>{tc.active_workload || tc.current || 0} tasks</b></span>
              <span style={{ color: t.textMuted }}>Completed: <b style={{ color: t.text }}>{tc.completed_count || tc.completed || 0}</b></span>
            </div>
            <div style={{ fontSize: 11, color: t.textFaint, marginTop: 6 }}>Specialization: {tc.specialization || tc.spec}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}

/* ============================================================
   REPORTS PAGE
   ============================================================ */
function ReportsPage({ t, selectedElevator }) {
  const [reports, setReports] = useState([]);
  const [preview, setPreview] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    async function loadReportTypes() {
      try {
        const list = await fetchReportTemplates();
        setReports(list);
      } catch (e) {}
    }
    loadReportTypes();
  }, []);

  const handleGenerate = async (reportType) => {
    setGenerating(true);
    try {
      const data = await generateReport(reportType, selectedElevator || "ALL");
      setPreview(data);
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const reportList = reports.length > 0 ? reports : [
    { id: "REP-FAULT", name: "Fault Analysis Report", type: "Fault Analysis", description: "ML fault inferences & feature signatures." },
    { id: "REP-RCA", name: "Root Cause Analysis (RCA) Summary", type: "RCA Summary", description: "Multi-sensor evidence chains & repair steps." },
    { id: "REP-HEALTH", name: "Elevator Health Audit", type: "Elevator Health", description: "Subsystem health scoring audit." },
    { id: "REP-PM", name: "Predictive Maintenance & RUL Forecast", type: "Predictive Maintenance", description: "RUL projections & failure risks." },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10 }}>
        <SectionTitle t={t}>Automated Maintenance & AI Reports</SectionTitle>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: 14 }}>
        {reportList.map(r => (
          <Card key={r.id} t={t}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <FileText size={18} color={t.primaryBright} />
              <StatusBadge status="healthy" t={t} label="Data-Driven" />
            </div>
            <div style={{ fontWeight: 600, color: t.text, fontSize: 13.5, marginTop: 10 }}>{r.name || r.type}</div>
            <div style={{ fontSize: 11.5, color: t.textMuted, marginTop: 2 }}>{r.description}</div>
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
              <button disabled={generating} onClick={() => handleGenerate(r.type)} style={{ ...primaryBtn(t), flex: 1, justifyContent: "center" }}>
                <FileBarChart2 size={12} /> {generating ? "Generating..." : "Generate"}
              </button>
            </div>
          </Card>
        ))}
      </div>

      {preview && (
        <Modal t={t} onClose={() => setPreview(null)} title={preview.title} wide>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
              <Field t={t} label="Report Type" value={preview.report_type} mono />
              <Field t={t} label="Generated At" value={preview.generated_at} />
              <Field t={t} label="Report ID" value={preview.id} mono />
            </div>
            <div style={{ background: t.surface2, border: `1px solid ${t.border}`, borderRadius: 6, padding: 14, whiteSpace: "pre-wrap", fontFamily: "sans-serif", fontSize: 12.5, color: t.text, maxHeight: 350, overflowY: "auto" }}>
              {preview.content_markdown}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

function ghostBtn(t) {
  return {
    display: "flex", alignItems: "center", justifyContent: "center", gap: 6, padding: "7px 10px", borderRadius: 6,
    border: `1px solid ${t.border}`, background: t.surface2, color: t.text, fontSize: 11.5, cursor: "pointer"
  };
}

function Modal({ t, onClose, title, children, wide }) {
  return (
    <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100, padding: 20 }}>
      <div onClick={e => e.stopPropagation()} style={{ background: t.surface, border: `1px solid ${t.border}`, borderRadius: 10, width: wide ? 620 : 480, maxWidth: "100%", maxHeight: "85vh", overflowY: "auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px", borderBottom: `1px solid ${t.borderSoft}` }}>
          <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontWeight: 600, fontSize: 15, color: t.text }}>{title}</div>
          <button onClick={onClose} style={{ background: "transparent", border: "none", color: t.textMuted, cursor: "pointer" }}><X size={18} /></button>
        </div>
        <div style={{ padding: 20 }}>{children}</div>
      </div>
    </div>
  );
}

/* ============================================================
   AI ASSISTANT PAGE
   ============================================================ */
const SUGGESTIONS = [
  "Why did Elevator KONE-ELEV-001 stop?",
  "What is causing high vibration?",
  "Show critical elevators.",
  "What maintenance is due this week?",
  "Explain the bearing fault.",
  "What should the technician check first?",
];

function assistantAnswer(q) {
  const ql = q.toLowerCase();
  if (ql.includes("stop") || ql.includes("001")) {
    return { summary: "KONE-ELEV-001 was flagged for reduced operation due to a detected bearing fault, not a full stoppage.", rootCause: "Motor Bearing Wear (92% confidence) driven by rising vibration, temperature and current draw.", data: "Vibration 6.8 mm/s (limit 4.5), Motor Temp 78°C (limit 65°C), Current 19.4 A (limit 18 A).", action: "Schedule bearing inspection and replacement within 12 days.", priority: "Critical" };
  }
  if (ql.includes("vibration")) {
    return { summary: "High vibration on KONE-ELEV-001 is linked to early-stage bearing wear.", rootCause: "Bearing surface degradation increases mechanical play, raising vibration amplitude.", data: "Vibration trending from 2.1 mm/s to 6.8 mm/s over 4 hours.", action: "Inspect bearing assembly; reduce load cycles until inspected.", priority: "High" };
  }
  if (ql.includes("critical")) {
    return { summary: "2 elevators are currently in critical state: KONE-ELEV-001 and KONE-ELEV-007.", rootCause: "001 — bearing degradation. 007 — motor overheating.", data: "Fleet-wide: 5 healthy, 3 warning, 2 critical.", action: "Prioritize dispatch to KONE-ELEV-007 (higher thermal risk to motor windings).", priority: "Critical" };
  }
  if (ql.includes("maintenance") || ql.includes("due") || ql.includes("week")) {
    return { summary: "6 maintenance tasks are due this week across 3 buildings.", rootCause: "Mix of scheduled servicing and fault-driven tasks (bearing, motor, door alignment).", data: "2 Critical, 1 High, 3 Medium/Low priority tasks pending.", action: "Confirm technician availability for the 2 critical tasks first.", priority: "High" };
  }
  if (ql.includes("bearing")) {
    return { summary: "The bearing fault on KONE-ELEV-001 is a wear-pattern fault detected through sensor fusion.", rootCause: "Combined vibration, thermal and current signature matches trained bearing-wear model at 94% confidence.", data: "Health score for the bearing component has dropped to 42%, RUL estimated at 12 days.", action: "Replace bearing 6205-ZZ during next maintenance window.", priority: "Critical" };
  }
  if (ql.includes("technician") || ql.includes("check")) {
    return { summary: "For KONE-ELEV-001, the technician should begin with the motor bearing assembly.", rootCause: "AI root cause analysis points to bearing wear as the primary driver of all secondary symptoms.", data: "Check vibration at motor housing, bearing temperature, and lubrication condition first.", action: "Follow root cause checklist, then verify current draw returns to baseline after inspection.", priority: "High" };
  }
  return { summary: "Based on current fleet telemetry, most elevators are operating within normal parameters.", rootCause: "No single dominant fault pattern outside the known bearing and motor-thermal cases.", data: "Fleet average health is 84%, with 2 elevators in critical state.", action: "Review the Alerts panel for the latest prioritized items.", priority: "Info" };
}

function AssistantPage({ t, selectedElevator }) {
  const [messages, setMessages] = useState([
    { role: "ai", summaryOnly: true, text: "I'm your industrial AI copilot for elevator diagnostics. Connected directly to live database. Ask me about faults, health, or maintenance!" },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const endRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, thinking]);

  const send = async (text) => {
    const q = (text || input).trim();
    if (!q) return;
    setMessages(m => [...m, { role: "user", text: q }]);
    setInput("");
    setThinking(true);

    try {
      const res = await askAIAssistant(q, selectedElevator || "KONE-ELEV-001");
      setThinking(false);
      setMessages(m => [...m, { role: "ai", summaryOnly: true, text: res.reply }]);
    } catch (e) {
      setThinking(false);
      setMessages(m => [...m, { role: "ai", summaryOnly: true, text: "Unable to query AI Assistant API. Check backend connectivity." }]);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, height: "calc(100vh - 130px)" }}>
      <Card t={t} style={{ background: `linear-gradient(120deg, ${t.surface}, ${t.primaryDim})` }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <div style={{ width: 38, height: 38, borderRadius: 8, background: `linear-gradient(135deg, ${t.primary}, ${t.info})`, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Sparkles size={18} color="#fff" />
          </div>
          <div>
            <div style={{ fontFamily: "'Chakra Petch', sans-serif", fontWeight: 700, fontSize: 16, color: t.text }}>AI Maintenance Assistant</div>
            <div style={{ fontSize: 12, color: t.textMuted }}>Grounded AI Assistant connected to live PostgreSQL database.</div>
          </div>
        </div>
      </Card>

      <Card t={t} style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", padding: 0 }} noPad>
        <div style={{ flex: 1, overflowY: "auto", padding: 18, display: "flex", flexDirection: "column", gap: 14 }}>
          {messages.map((m, i) => (
            <div key={i} style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
              {m.role === "user" ? (
                <div style={{ maxWidth: "70%", background: t.primaryDim, color: t.text, padding: "10px 14px", borderRadius: "10px 10px 2px 10px", fontSize: 13 }}>{m.text}</div>
              ) : (
                <div style={{ maxWidth: "82%", background: t.surface2, border: `1px solid ${t.border}`, borderRadius: "10px 10px 10px 2px", padding: 14 }}>
                  <div style={{ fontSize: 13, color: t.text, whiteSpace: "pre-wrap" }}>{m.text}</div>
                </div>
              )}
            </div>
          ))}
          {thinking && (
            <div style={{ display: "flex", justifyContent: "flex-start" }}>
              <div style={{ background: t.surface2, border: `1px solid ${t.border}`, borderRadius: "10px 10px 10px 2px", padding: "10px 14px", display: "flex", gap: 6, alignItems: "center" }}>
                <span className="spinner" /><span style={{ fontSize: 12, color: t.textMuted }}>Querying PostgreSQL database & AI engine…</span>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div style={{ padding: 14, borderTop: `1px solid ${t.borderSoft}` }}>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 10 }}>
            {SUGGESTIONS.map(s => (
              <button key={s} onClick={() => send(s)} style={{ fontSize: 11, padding: "6px 10px", borderRadius: 14, border: `1px solid ${t.border}`, background: t.surface2, color: t.textMuted, cursor: "pointer" }}>{s}</button>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && send()}
              placeholder="Ask about faults, health or maintenance…"
              style={{ flex: 1, background: t.surface2, border: `1px solid ${t.border}`, borderRadius: 8, padding: "11px 14px", color: t.text, fontSize: 13, outline: "none" }} />
            <button onClick={() => send()} style={{ ...primaryBtn(t), padding: "0 16px" }}><Send size={15} /></button>
          </div>
        </div>
      </Card>
    </div>
  );
}

function AssistantBlock({ t, label, value, icon: Icon, mono }) {
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, color: t.textFaint, fontWeight: 600, marginBottom: 2 }}><Icon size={11} />{label}</div>
      <div style={{ fontSize: 12.5, color: t.text, fontFamily: mono ? "'IBM Plex Mono', monospace" : "inherit" }}>{value}</div>
    </div>
  );
}

/* ============================================================
   BUILDINGS PAGE
   ============================================================ */
function BuildingsPage({ t, elevators, setPage, setSelectedElevator }) {
  const [openBuilding, setOpenBuilding] = useState(null);
  if (openBuilding) {
    const b = BUILDINGS.find(x => x.id === openBuilding);
    const list = elevators.filter(e => e.buildingId === openBuilding);
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <button onClick={() => setOpenBuilding(null)} style={{ ...ghostBtn(t), width: 130 }}><ChevronLeft size={13} /> All Buildings</button>
        <SectionTitle t={t} sub={b.location}>{b.name}</SectionTitle>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 14 }}>
          {list.map(e => (
            <Card key={e.id} t={t} style={{ cursor: "pointer" }} className="sensor-card" >
              <div onClick={() => { setSelectedElevator(e.id); setPage("monitoring"); }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontWeight: 600, color: t.text, fontSize: 13 }}>{e.id}</span>
                  <StatusBadge status={e.status} t={t} />
                </div>
                <div style={{ display: "flex", gap: 16, marginTop: 10, fontSize: 11.5 }}>
                  <Field t={t} label="Floor" value={e.floor} mono />
                  <Field t={t} label="Direction" value={e.dir} />
                  <Field t={t} label="Health" value={`${e.health}%`} mono />
                </div>
                <div style={{ marginTop: 8 }}><RiskPill risk={e.risk} t={t} /></div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SectionTitle t={t}>Buildings & Multi-Elevator Monitoring</SectionTitle>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 14 }}>
        {BUILDINGS.map(b => {
          const list = elevators.filter(e => e.buildingId === b.id);
          const healthy = list.filter(e => e.status === "healthy").length;
          const warning = list.filter(e => e.status === "warning").length;
          const critical = list.filter(e => e.status === "critical").length;
          const avg = Math.round(list.reduce((a, e) => a + e.health, 0) / list.length);
          return (
            <Card key={b.id} t={t} style={{ cursor: "pointer" }} className="sensor-card">
              <div onClick={() => setOpenBuilding(b.id)}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 14.5, color: t.text, fontFamily: "'Chakra Petch', sans-serif" }}>{b.name}</div>
                    <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: t.textFaint, marginTop: 2 }}><MapPin size={11} />{b.location}</div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 18, fontWeight: 600, color: healthColor(avg, t) }}>{avg}%</div>
                    <div style={{ fontSize: 9.5, color: t.textFaint }}>FLEET HEALTH</div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 14, marginTop: 14 }}>
                  <MiniCount t={t} n={list.length} label="Total" color={t.textMuted} />
                  <MiniCount t={t} n={healthy} label="Healthy" color={t.success} />
                  <MiniCount t={t} n={warning} label="Warning" color={t.warning} />
                  <MiniCount t={t} n={critical} label="Critical" color={t.critical} />
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

function MiniCount({ t, n, label, color }) {
  return (
    <div>
      <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 15, fontWeight: 600, color }}>{n}</div>
      <div style={{ fontSize: 9.5, color: t.textFaint }}>{label}</div>
    </div>
  );
}

/* ============================================================
   ALERTS PAGE
   ============================================================ */
function AlertsPage({ t, alerts, setAlerts }) {
  const [filter, setFilter] = useState("All");
  const filtered = alerts.filter(a => filter === "All" || (filter === "Resolved" ? a.level === "resolved" : a.level === filter.toLowerCase()));
  const setRead = (id) => setAlerts(as => as.map(a => a.id === id ? { ...a, read: true } : a));
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SectionTitle t={t} right={
        <div style={{ display: "flex", gap: 6 }}>
          {["All", "Critical", "Warning", "Information", "Resolved"].map(f => (
            <button key={f} onClick={() => setFilter(f)} style={{
              padding: "6px 12px", fontSize: 11.5, borderRadius: 6, cursor: "pointer",
              background: filter === f ? t.primaryDim : t.surface2, color: filter === f ? t.primaryBright : t.textMuted,
              border: `1px solid ${filter === f ? t.primaryBright : t.border}`
            }}>{f}</button>
          ))}
        </div>
      }>Alert Center</SectionTitle>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {filtered.map(a => (
          <Card key={a.id} t={t} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10, opacity: a.read ? 0.72 : 1 }}>
            <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
              <div style={{ width: 34, height: 34, borderRadius: 7, flexShrink: 0, background: (a.level === "critical" ? t.critical : a.level === "warning" ? t.warning : a.level === "resolved" ? t.textFaint : t.info) + "22", display: "flex", alignItems: "center", justifyContent: "center" }}>
                {a.level === "critical" ? <AlertTriangle size={16} color={t.critical} /> : a.level === "warning" ? <AlertTriangle size={16} color={t.warning} /> : a.level === "resolved" ? <CheckCircle2 size={16} color={t.textFaint} /> : <Info size={16} color={t.info} />}
              </div>
              <div>
                <div style={{ fontSize: 13, color: t.text, fontWeight: 600 }}>{a.text}</div>
                <div style={{ fontSize: 11, color: t.textFaint, marginTop: 2 }}>{a.elevator} · {a.time}</div>
              </div>
            </div>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {!a.read && <button onClick={() => setRead(a.id)} style={ghostBtn(t)}>Mark Read</button>}
              <button style={ghostBtn(t)}>Acknowledge</button>
              <button style={ghostBtn(t)}>View Elevator</button>
              {a.level !== "resolved" && <button style={ghostBtn(t)}>Create Task</button>}
              {a.level !== "resolved" && <button style={{ ...ghostBtn(t), color: t.success, borderColor: t.success + "55" }}>Resolve</button>}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

/* ============================================================
   ADMIN PANEL
   ============================================================ */
function AdminPage({ t, elevators }) {
  const [tab, setTab] = useState("Buildings");
  const [search, setSearch] = useState("");
  const tabs = ["Buildings", "Elevators", "Users", "Technicians", "Sensors", "Alert Thresholds", "Audit Log"];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SectionTitle t={t}>Admin Management</SectionTitle>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", borderBottom: `1px solid ${t.border}` }}>
        {tabs.map(tb => (
          <button key={tb} onClick={() => setTab(tb)} style={{
            padding: "9px 12px", fontSize: 12, background: "transparent", border: "none", cursor: "pointer",
            color: tab === tb ? t.primaryBright : t.textMuted, fontWeight: tab === tb ? 600 : 500,
            borderBottom: tab === tb ? `2px solid ${t.primaryBright}` : "2px solid transparent", marginBottom: -1, whiteSpace: "nowrap"
          }}>{tb}</button>
        ))}
      </div>

      <Card t={t} noPad>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 16, flexWrap: "wrap", gap: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, background: t.surface2, border: `1px solid ${t.border}`, borderRadius: 6, padding: "7px 10px", width: 220 }}>
            <Search size={13} color={t.textFaint} />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder={`Search ${tab.toLowerCase()}…`} style={{ background: "transparent", border: "none", outline: "none", color: t.text, fontSize: 12, width: "100%" }} />
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button style={ghostBtn(t)}><Filter size={12} /> Filter</button>
            <button style={primaryBtn(t)}><Plus size={13} /> Add {tab.slice(0, -1)}</button>
          </div>
        </div>

        {tab === "Buildings" && <AdminTable t={t} cols={["ID", "Name", "Location", "Elevators"]} rows={BUILDINGS.filter(b => b.name.toLowerCase().includes(search.toLowerCase())).map(b => [b.id, b.name, b.location, b.elevators])} />}
        {tab === "Elevators" && <AdminTable t={t} cols={["ID", "Building", "Status", "Health"]} rows={elevators.filter(e => e.id.toLowerCase().includes(search.toLowerCase())).map(e => [e.id, e.building, <StatusBadge key={e.id} status={e.status} t={t} />, `${e.health}%`])} />}
        {tab === "Users" && <AdminTable t={t} cols={["Name", "Role", "Email", "Status"]} rows={[["Mohan K.", "Admin", "mohan@elevatorai.io", "Active"], ["R. Karthik", "Maintenance Engineer", "karthik@elevatorai.io", "Active"], ["S. Priya", "Maintenance Engineer", "priya@elevatorai.io", "Active"], ["Manager Desk", "Manager", "manager@elevatorai.io", "Active"]]} />}
        {tab === "Technicians" && <AdminTable t={t} cols={["Name", "Role", "Specialization", "Availability"]} rows={TECHNICIANS.map(tc => [tc.name, tc.role, tc.spec, tc.availability])} />}
        {tab === "Sensors" && <AdminTable t={t} cols={["Sensor", "Unit", "Normal Range", "Status"]} rows={SENSOR_DEFS.filter(s => s.key !== "door").map(s => [s.label, s.unit, `${s.normal[0]}–${s.normal[1]}`, "Calibrated"])} />}
        {tab === "Alert Thresholds" && <ThresholdsPanel t={t} />}
        {tab === "Audit Log" && <AdminTable t={t} cols={["Time", "User", "Action", "Elevator", "Status"]} rows={AUDIT_LOG.map(l => [l.time, l.user, l.action, l.elevator, l.status])} />}
      </Card>
    </div>
  );
}

function AdminTable({ t, cols, rows }) {
  const [data, setData] = useState(rows);
  useEffect(() => setData(rows), [JSON.stringify(rows.map(r => r[0]))]);
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12.5 }}>
        <thead>
          <tr style={{ borderTop: `1px solid ${t.borderSoft}`, borderBottom: `1px solid ${t.borderSoft}` }}>
            {cols.map(c => <th key={c} style={{ textAlign: "left", padding: "9px 16px", color: t.textFaint, fontWeight: 600, fontSize: 10.5 }}>{c}</th>)}
            <th></th>
          </tr>
        </thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={i} style={{ borderBottom: `1px solid ${t.borderSoft}` }}>
              {r.map((cell, j) => <td key={j} style={{ padding: "9px 16px", color: j === 0 ? t.text : t.textMuted, fontFamily: j === 0 ? "'IBM Plex Mono', monospace" : "inherit" }}>{cell}</td>)}
              <td style={{ padding: "9px 16px", display: "flex", gap: 6, justifyContent: "flex-end" }}>
                <button style={iconBtnSm(t)}><Pencil size={12} /></button>
                <button onClick={() => setData(d => d.filter((_, idx) => idx !== i))} style={{ ...iconBtnSm(t), color: t.critical }}><Trash2 size={12} /></button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function iconBtnSm(t) { return { width: 26, height: 26, borderRadius: 5, border: `1px solid ${t.border}`, background: t.surface2, color: t.textMuted, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }; }

function ThresholdsPanel({ t }) {
  const [th, setTh] = useState({ vibration: 4.5, motorTemp: 65, current: 18 });
  return (
    <div style={{ padding: 18, display: "flex", flexDirection: "column", gap: 16, maxWidth: 420 }}>
      {Object.entries(th).map(([k, v]) => (
        <div key={k}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12.5, marginBottom: 6 }}>
            <span style={{ color: t.text, textTransform: "capitalize" }}>{k.replace(/([A-Z])/g, " $1")}</span>
            <span style={{ color: t.primaryBright, fontFamily: "'IBM Plex Mono', monospace" }}>{v}</span>
          </div>
          <input type="range" min={k === "motorTemp" ? 40 : k === "current" ? 8 : 1} max={k === "motorTemp" ? 100 : k === "current" ? 25 : 10} step={0.1}
            value={v} onChange={e => setTh({ ...th, [k]: Number(e.target.value) })} style={{ width: "100%", accentColor: t.primaryBright }} />
        </div>
      ))}
      <button style={{ ...primaryBtn(t), justifyContent: "center" }}>Save Thresholds</button>
    </div>
  );
}

/* ============================================================
   SETTINGS PAGE
   ============================================================ */
function SettingsPage({ t, dark, setDark }) {
  const [lang, setLang] = useState("English");
  const [notifs, setNotifs] = useState({ critical: true, warning: true, info: false, email: true });
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SectionTitle t={t}>Settings</SectionTitle>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }} className="responsive-grid-2">
        <Card t={t}>
          <SectionTitle t={t}>Profile Settings</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <LabeledInput t={t} label="Full Name" value="Mohan K." />
            <LabeledInput t={t} label="Email" value="mohan@elevatorai.io" />
            <LabeledInput t={t} label="Role" value="Admin" disabled />
          </div>
        </Card>
        <Card t={t}>
          <SectionTitle t={t}>System Preferences</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <ToggleRow t={t} label="Dark Mode" value={dark} onChange={setDark} />
            <div>
              <div style={{ fontSize: 12.5, color: t.text, marginBottom: 6 }}>Language</div>
              <select value={lang} onChange={e => setLang(e.target.value)} style={{ ...selStyle(t), width: "100%" }}>
                <option>English</option><option>தமிழ் (Tamil)</option><option>हिन्दी (Hindi)</option>
              </select>
            </div>
          </div>
        </Card>
        <Card t={t}>
          <SectionTitle t={t}>Notification Preferences</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <ToggleRow t={t} label="Critical Alerts" value={notifs.critical} onChange={v => setNotifs({ ...notifs, critical: v })} />
            <ToggleRow t={t} label="Warning Alerts" value={notifs.warning} onChange={v => setNotifs({ ...notifs, warning: v })} />
            <ToggleRow t={t} label="Informational Alerts" value={notifs.info} onChange={v => setNotifs({ ...notifs, info: v })} />
            <ToggleRow t={t} label="Email Notifications" value={notifs.email} onChange={v => setNotifs({ ...notifs, email: v })} />
          </div>
        </Card>
        <Card t={t}>
          <SectionTitle t={t}>Alert Thresholds</SectionTitle>
          <ThresholdsPanel t={t} />
        </Card>
      </div>
    </div>
  );
}

function LabeledInput({ t, label, value, disabled }) {
  return (
    <div>
      <div style={{ fontSize: 11, color: t.textFaint, marginBottom: 5 }}>{label}</div>
      <input defaultValue={value} disabled={disabled} style={{ width: "100%", background: disabled ? t.surface3 : t.surface2, border: `1px solid ${t.border}`, borderRadius: 6, padding: "9px 11px", color: t.text, fontSize: 12.5, outline: "none" }} />
    </div>
  );
}

function ToggleRow({ t, label, value, onChange }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <span style={{ fontSize: 12.5, color: t.text }}>{label}</span>
      <button onClick={() => onChange(!value)} style={{
        width: 40, height: 22, borderRadius: 11, border: "none", cursor: "pointer", position: "relative",
        background: value ? t.primary : t.surface3, transition: "background 0.2s"
      }}>
        <span style={{ position: "absolute", top: 2, left: value ? 20 : 2, width: 18, height: 18, borderRadius: "50%", background: "#fff", transition: "left 0.2s" }} />
      </button>
    </div>
  );
}

/* ============================================================
   QR MODAL
   ============================================================ */
function QRModal({ t, onClose, elevators, setPage, setSelectedElevator }) {
  const [scanning, setScanning] = useState(true);
  useEffect(() => { const tm = setTimeout(() => setScanning(false), 1600); return () => clearTimeout(tm); }, []);
  const e = elevators[0];
  return (
    <Modal t={t} onClose={onClose} title="Scan Elevator QR Code">
      {scanning ? (
        <div style={{ textAlign: "center", padding: "20px 0" }}>
          <div style={{ width: 160, height: 160, margin: "0 auto", border: `2px solid ${t.primaryBright}`, borderRadius: 10, position: "relative", overflow: "hidden", background: t.surface2 }}>
            <ScanLine size={40} color={t.primaryBright} style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", opacity: 0.4 }} />
            <div className="scan-line" style={{ position: "absolute", left: 0, right: 0, height: 2, background: t.primaryBright, boxShadow: `0 0 8px ${t.primaryBright}` }} />
          </div>
          <div style={{ marginTop: 14, color: t.textMuted, fontSize: 12.5 }}>Scanning QR code on elevator control panel…</div>
        </div>
      ) : (
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontWeight: 700, fontSize: 15, color: t.text }}>{e.id}</span>
            <StatusBadge status={e.status} t={t} />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 14 }}>
            <Field t={t} label="Building" value={e.building} />
            <Field t={t} label="Floor" value={e.floor} mono />
            <Field t={t} label="Health Score" value={`${e.health}%`} mono />
            <Field t={t} label="Active Fault" value={e.fault || "None"} />
          </div>
          <button onClick={() => { setSelectedElevator(e.id); setPage("monitoring"); onClose(); }} style={{ ...primaryBtn(t), width: "100%", justifyContent: "center", marginTop: 16 }}>
            Open Full Elevator Profile
          </button>
        </div>
      )}
    </Modal>
  );
}

/* ============================================================
   ROOT APP
   ============================================================ */
export default function App() {
  const [dark, setDark] = useState(true);
  const t = useTheme(dark);
  const [page, setPage] = useState("dashboard");
  const [collapsed, setCollapsed] = useState(false);
  const [role, setRole] = useState("Admin");
  const [building, setBuilding] = useState("ALL");
  const [elevatorFilter, setElevatorFilter] = useState("ALL");
  const [selectedElevator, setSelectedElevator] = useState("KONE-ELEV-001");
  const [alerts, setAlerts] = useState(ALERTS);
  const [showAlerts, setShowAlerts] = useState(false);
  const [showQR, setShowQR] = useState(false);
  const [tick, setTick] = useState(0);
  const [now, setNow] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const iv = setInterval(() => { setTick(x => x + 1); setNow(new Date().toLocaleTimeString()); }, 3000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    if (!NAV.find(n => n.id === page)?.roles.includes(role)) setPage("dashboard");
  }, [role]);

  const filteredElevators = ELEVATORS.filter(e => (building === "ALL" || e.buildingId === building));
  const unread = alerts.filter(a => !a.read).length;

  const pageProps = { t, elevators: filteredElevators, tick, now, selectedElevator, setSelectedElevator, setPage, alerts, setAlerts, dark, setDark, role };

  return (
    <div style={{
      display: "flex", height: "100vh", width: "100%", background: t.bg, color: t.text,
      fontFamily: "'IBM Plex Sans', sans-serif", overflow: "hidden"
    }}>
      <style>{FONT_CSS}{`
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-thumb { background: ${t.border}; border-radius: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        select, input { font-family: 'IBM Plex Sans', sans-serif; }
        .sensor-card:hover { border-color: ${t.primaryBright}66 !important; }
        .spinner { width: 13px; height: 13px; border-radius: 50%; border: 2px solid ${t.textFaint}; border-top-color: ${t.primaryBright}; animation: spin 0.7s linear infinite; display: inline-block; }
        .spinner-lg { width: 40px; height: 40px; border-radius: 50%; border: 3px solid ${t.border}; border-top-color: ${t.primaryBright}; animation: spin 0.9s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .pulse-dot { animation: pulse 1.6s ease-in-out infinite; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }
        .scan-line { animation: scan 1.6s ease-in-out infinite; }
        @keyframes scan { 0% { top: 6px; } 50% { top: 150px; } 100% { top: 6px; } }
        @media (max-width: 980px) {
          .responsive-grid-3 { grid-template-columns: 1fr !important; }
          .responsive-grid-2 { grid-template-columns: 1fr !important; }
        }
      `}</style>

      <Sidebar t={t} page={page} setPage={setPage} collapsed={collapsed} setCollapsed={setCollapsed} role={role} />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, overflow: "hidden" }}>
        <Topbar
          t={t} page={page} dark={dark} setDark={setDark}
          buildings={BUILDINGS} building={building} setBuilding={setBuilding}
          elevators={ELEVATORS} elevator={elevatorFilter} setElevator={setElevatorFilter}
          role={role} setRole={setRole} alertsUnread={unread}
          onOpenAlerts={() => setShowAlerts(true)} onOpenQR={() => setShowQR(true)}
        />
        <div style={{ flex: 1, overflowY: "auto", padding: 22 }}>
          {page === "dashboard" && <DashboardPage {...pageProps} />}
          {page === "monitoring" && <MonitoringPage {...pageProps} />}
          {page === "detection" && <DetectionPage {...pageProps} />}
          {page === "rootcause" && <RootCausePage {...pageProps} />}
          {page === "predictive" && <PredictivePage {...pageProps} />}
          {page === "health" && <HealthPage {...pageProps} />}
          {page === "analytics" && <AnalyticsPage {...pageProps} />}
          {page === "timeline" && <TimelinePage {...pageProps} />}
          {page === "maintenance" && <MaintenancePage {...pageProps} />}
          {page === "technicians" && <TechniciansPage {...pageProps} />}
          {page === "reports" && <ReportsPage {...pageProps} />}
          {page === "assistant" && <AssistantPage {...pageProps} />}
          {page === "buildings" && <BuildingsPage {...pageProps} />}
          {page === "alerts" && <AlertsPage {...pageProps} />}
          {page === "admin" && <AdminPage {...pageProps} />}
          {page === "settings" && <SettingsPage {...pageProps} />}
        </div>
      </div>

      {showAlerts && (
        <Modal t={t} onClose={() => setShowAlerts(false)} title="Alerts & Notifications" wide>
          <AlertsPage t={t} alerts={alerts} setAlerts={setAlerts} />
        </Modal>
      )}
      {showQR && <QRModal t={t} onClose={() => setShowQR(false)} elevators={ELEVATORS} setPage={setPage} setSelectedElevator={setSelectedElevator} />}
    </div>
  );
}
