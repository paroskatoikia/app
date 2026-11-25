
import { useEffect, useMemo, useState } from "react";
import {
  LayoutDashboard, Building2, Users, UserRound, BriefcaseBusiness,
  ClipboardList, Sprout, FileText, ChartNoAxesCombined, Settings,
  Search, Bell, Menu, X, RefreshCw, LogOut, CircleAlert, Wallet, Truck, CreditCard, Download, ClipboardCheck, Droplets
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, Legend,
  XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell
} from "recharts";
import "./App.css";

const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api").replace(/\/$/, "");


let uiLanguage = typeof localStorage !== "undefined" && localStorage.getItem("pk_language") === "el" ? "el" : "en";
const greek = {
  "Group by": "Ομαδοποίηση κατά",
  "No grouping": "Χωρίς ομαδοποίηση",
  "Month": "Μήνας",
  "Rows per page": "Γραμμές ανά σελίδα",
  "Page": "Σελίδα",
  "of": "από",
  "records": "καταχωρίσεις",
  "DATABASE RECORDS": "ΚΑΤΑΧΩΡΙΣΕΙΣ ΒΑΣΗΣ",
  "No work entries match your search.": "Δεν βρέθηκαν εργασίες.",
  "Recorded work and charges from Django": "Καταγεγραμμένες εργασίες και χρεώσεις",

  "Overview": "Επισκόπηση",
  "Important Jobs": "Σημαντικές εργασίες",
  "Villas": "Κατοικίες",
  "House Checks": "Έλεγχοι κατοικιών",
  "Water Measurements": "Μετρήσεις νερού",
  "Customers": "Πελάτες",
  "Customer Payments": "Εισπράξεις πελατών",
  "Suppliers": "Προμηθευτές",
  "Supplier Payments": "Πληρωμές προμηθευτών",
  "Employees": "Εργαζόμενοι",
  "Company Gas": "Καύσιμα εταιρείας",
  "Departments": "Τμήματα",
  "Services": "Υπηρεσίες",
  "Work Entries": "Καταχωρίσεις εργασιών",
  "Programs": "Προγράμματα",
  "Invoices": "Τιμολόγια",
  "Add Villa": "Προσθήκη κατοικίας",
  "Add Customer": "Προσθήκη πελάτη",
  "Add Supplier": "Προσθήκη προμηθευτή",
  "Add Employee": "Προσθήκη εργαζομένου",
  "Add Department": "Προσθήκη τμήματος",
  "Add Service": "Προσθήκη υπηρεσίας",
  "Add Work Entry": "Καταχώριση εργασίας",
  "Add Program": "Προσθήκη προγράμματος",
  "Add Invoice": "Προσθήκη τιμολογίου",
  "Add Customer Payment": "Καταχώριση είσπραξης",
  "Add Supplier Payment": "Καταχώριση πληρωμής",
  "Add Fuel Expense": "Καταχώριση καυσίμων",
  "Add Job": "Προσθήκη εργασίας",
  "Add House Check": "Καταχώριση ελέγχου",
  "Add Measurement": "Καταχώριση μέτρησης",
  "Refresh data": "Ανανέωση δεδομένων",
  "Refresh": "Ανανέωση",
  "Sign out": "Αποσύνδεση",
  "Django API connected": "Σύνδεση με Django API",
  "Open menu": "Άνοιγμα μενού",
  "Data Analytics": "Ανάλυση δεδομένων",
  "Revenue": "Έσοδα",
  "Expenses": "Έξοδα",
  "Gross profit": "Μικτό κέρδος",
  "Gross margin": "Μικτό περιθώριο",
  "Reimbursable invoices": "Τιμολόγια προς αποζημίωση",
  "Employee work costs + company invoices": "Κόστος εργασίας + εταιρικά τιμολόγια",
  "Employee cost": "Κόστος εργαζομένων",
  "Date": "Ημερομηνία",
  "Amount": "Ποσό",
  "Invoice": "Τιμολόγιο",
  "Supplier": "Προμηθευτής",
  "Customer": "Πελάτης",
  "Department": "Τμήμα",
  "Villa": "Κατοικία",
  "Employee": "Εργαζόμενος",
  "Service": "Υπηρεσία",
  "Hours": "Ώρες",
  "Notes": "Σημειώσεις",
  "Description": "Περιγραφή",
  "Name": "Όνομα",
  "Area": "Περιοχή",
  "Status": "Κατάσταση",
  "Action": "Ενέργεια",
  "Reference": "Αναφορά",
  "Charges": "Χρεώσεις",
  "Paid": "Εξοφλημένα",
  "Outstanding": "Υπόλοιπο",
  "Unpaid balance": "Ανεξόφλητο υπόλοιπο",
  "Credit balance": "Πιστωτικό υπόλοιπο",
  "Unpaid / credit": "Οφειλή / πίστωση",
  "Department breakdown": "Ανάλυση ανά τμήμα",
  "Export data": "Εξαγωγή δεδομένων",
  "Export data ZIP": "Εξαγωγή δεδομένων ZIP",
  "Total invoiced": "Σύνολο τιμολογίων",
  "Total payments": "Σύνολο πληρωμών",
  "Payment records": "Καταχωρίσεις πληρωμών",
  "Average payment": "Μέση πληρωμή",
  "Supplier invoices": "Τιμολόγια προμηθευτών",
  "Customer charges": "Χρεώσεις πελατών",
  "Supplier payments": "Πληρωμές προμηθευτών",
  "Customer payments": "Εισπράξεις πελατών",
  "Customer statistics": "Στατιστικά πελατών",
  "Supplier statistics": "Στατιστικά προμηθευτών",
  "Salary": "Μισθός",
  "Salary type": "Τύπος αμοιβής",
  "Service type": "Τύπος υπηρεσίας",
  "Revenue earned": "Παραγόμενα έσοδα",
  "Gross earned": "Μικτές αποδοχές",
  "Recorded salary cost": "Καταγεγραμμένο μισθολογικό κόστος",
  "Program": "Πρόγραμμα",
  "Monthly price": "Μηνιαία τιμή",
  "Start date": "Ημερομηνία έναρξης",
  "End date": "Ημερομηνία λήξης",
  "Customer charge": "Χρέωση πελάτη",
  "Villa name": "Όνομα κατοικίας",
  "Total villas": "Σύνολο κατοικιών",
  "Registered Villas": "Καταχωρισμένες κατοικίες",
  "Need checking": "Χρειάζονται έλεγχο",
  "Already checked": "Ελεγμένες",
  "Last check": "Τελευταίος έλεγχος",
  "Next due": "Επόμενος έλεγχος",
  "Checked by": "Ελέγχθηκε από",
  "Condition": "Κατάσταση",
  "Inspection date": "Ημερομηνία ελέγχου",
  "Measurement date": "Ημερομηνία μέτρησης",
  "Source": "Πηγή",
  "Reading / level": "Ένδειξη / στάθμη",
  "Select a villa": "Επιλέξτε κατοικία",
  "Select a water tank": "Επιλέξτε δεξαμενή",
  "Select customer": "Επιλέξτε πελάτη",
  "Water Measurement Program": "Πρόγραμμα μετρήσεων νερού",
  "House Checking Program": "Πρόγραμμα ελέγχων κατοικιών",
  "water measurement": "μέτρηση νερού",
  "house check": "έλεγχος κατοικίας",
  "Record": "Καταχώριση",
  "Record saved successfully": "Η καταχώριση αποθηκεύτηκε επιτυχώς",
  "Loading inspection status...": "Φόρτωση κατάστασης ελέγχων...",
  "Pending jobs": "Εκκρεμείς εργασίες",
  "Completed": "Ολοκληρωμένες",
  "Critical / overdue": "Κρίσιμες / εκπρόθεσμες",
  "Deadline": "Προθεσμία",
  "Procedure days": "Ημέρες διαδικασίας",
  "Procedure": "Διάρκεια διαδικασίας",
  "Recommended start": "Προτεινόμενη έναρξη",
  "Latest start": "Τελευταία δυνατή έναρξη",
  "Time remaining": "Χρόνος που απομένει",
  "Spare days": "Περιθώριο ημερών",
  "Edit job": "Επεξεργασία εργασίας",
  "New job": "Νέα εργασία",
  "Save job": "Αποθήκευση εργασίας",
  "Cancel": "Ακύρωση",
  "Edit": "Επεξεργασία",
  "Reopen job": "Επαναφορά εργασίας",
  "Mark completed": "Σήμανση ως ολοκληρωμένη",
  "Pending duties": "Εκκρεμείς εργασίες",
  "Completed duties": "Ολοκληρωμένες εργασίες",
  "No matching jobs.": "Δεν βρέθηκαν εργασίες.",
  "Fuel": "Καύσιμο",
  "Fuel type": "Τύπος καυσίμου",
  "Month": "Μήνας",
  "All employees": "Όλοι οι εργαζόμενοι",
  "All fuels": "Όλα τα καύσιμα",
  "Clear filters": "Καθαρισμός φίλτρων",
  "Rows per page": "Γραμμές ανά σελίδα",
  "Open PDF ↗": "Άνοιγμα PDF ↗",
  "Invalid invoice link": "Μη έγκυρος σύνδεσμος τιμολογίου",
  "Previous": "Προηγούμενη",
  "Next": "Επόμενη",
  "Monthly": "Μηνιαία",
  "Yearly": "Ετήσια",
  "Search employee, villa, department or date...": "Αναζήτηση εργαζομένου, κατοικίας, τμήματος ή ημερομηνίας...",
  "Click to group or ungroup": "Πατήστε για ομαδοποίηση ή κατάργηση ομαδοποίησης",
  "Search work entries...": "Αναζήτηση εργασιών...",
  "Search customer or job...": "Αναζήτηση πελάτη ή εργασίας...",
  "Search employees, departments or salary type...": "Αναζήτηση εργαζομένων, τμημάτων ή τύπου αμοιβής...",
  "Search employee charts...": "Αναζήτηση γραφημάτων εργαζομένων...",
  "Search services or departments...": "Αναζήτηση υπηρεσιών ή τμημάτων...",
  "Search service charts...": "Αναζήτηση γραφημάτων υπηρεσιών...",
  "PROPERTY PERFORMANCE": "ΑΠΟΔΟΣΗ ΚΑΤΟΙΚΙΩΝ",
  "DEPARTMENT PERFORMANCE": "ΑΠΟΔΟΣΗ ΤΜΗΜΑΤΩΝ",
  "SERVICE PERFORMANCE": "ΑΠΟΔΟΣΗ ΥΠΗΡΕΣΙΩΝ",
  "EMPLOYEE PERFORMANCE": "ΑΠΟΔΟΣΗ ΕΡΓΑΖΟΜΕΝΩΝ",
  "PROPERTY OPERATIONS": "ΔΙΑΧΕΙΡΙΣΗ ΚΑΤΟΙΚΙΩΝ",
  "SUPPLIER INVOICE ANALYTICS": "ΑΝΑΛΥΣΗ ΤΙΜΟΛΟΓΙΩΝ ΠΡΟΜΗΘΕΥΤΩΝ",
  "PAYMENT STATISTICS": "ΣΤΑΤΙΣΤΙΚΑ ΠΛΗΡΩΜΩΝ",
  "SUPPLIER ACCOUNTS": "ΛΟΓΑΡΙΑΣΜΟΙ ΠΡΟΜΗΘΕΥΤΩΝ",
  "CUSTOMER ACCOUNTS": "ΛΟΓΑΡΙΑΣΜΟΙ ΠΕΛΑΤΩΝ",
  "PAYMENT STATUS": "ΚΑΤΑΣΤΑΣΗ ΠΛΗΡΩΜΩΝ",
  "VILLA FINANCIAL SUMMARY": "ΟΙΚΟΝΟΜΙΚΗ ΣΥΝΟΨΗ ΚΑΤΟΙΚΙΩΝ",
  "DEPARTMENT FINANCIAL SUMMARY": "ΟΙΚΟΝΟΜΙΚΗ ΣΥΝΟΨΗ ΤΜΗΜΑΤΩΝ",
  "SERVICE FINANCIAL SUMMARY": "ΟΙΚΟΝΟΜΙΚΗ ΣΥΝΟΨΗ ΥΠΗΡΕΣΙΩΝ",
  "EMPLOYEE EARNINGS SUMMARY": "ΣΥΝΟΨΗ ΑΠΟΔΟΧΩΝ ΕΡΓΑΖΟΜΕΝΩΝ",
  "PAROS KATOIKIA DATABASE": "ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ PAROS KATOIKIA",
  "OPERATIONS / DEADLINES": "ΕΡΓΑΣΙΕΣ / ΠΡΟΘΕΣΜΙΕΣ",
  "JOB REGISTER": "ΜΗΤΡΩΟ ΕΡΓΑΣΙΩΝ",
  "COMPANY EXPENSES / FUEL": "ΕΤΑΙΡΙΚΑ ΕΞΟΔΑ / ΚΑΥΣΙΜΑ",
  "Villa revenue & gross profit": "Έσοδα και μικτό κέρδος κατοικιών",
  "Department revenue & gross profit": "Έσοδα και μικτό κέρδος τμημάτων",
  "Service revenue & gross profit": "Έσοδα και μικτό κέρδος υπηρεσιών",
  "Salary, revenue earned & gross earned": "Μισθός, έσοδα και μικτές αποδοχές",
  "Supplier payments vs outstanding": "Πληρωμές προμηθευτών και οφειλές",
  "Fuel expenses paid by the company for employees.": "Έξοδα καυσίμων εργαζομένων που πληρώνει η εταιρεία.",
  "Plan ahead, track urgency and complete your duties.": "Προγραμματίστε και παρακολουθήστε τις εκκρεμείς εργασίες.",
  "Invoice totals, departmental costs, supplier balances and individual charts.": "Σύνολα τιμολογίων, έξοδα τμημάτων, υπόλοιπα προμηθευτών και γραφήματα.",
  "Recorded charges, payments, outstanding balances and cost distributions by department.": "Χρεώσεις, πληρωμές, υπόλοιπα και κατανομή κόστους ανά τμήμα.",
  "Recorded payments, outstanding account balances and individual payment charts.": "Καταγεγραμμένες πληρωμές, υπόλοιπα και γραφήματα πληρωμών.",
  "Total recorded": "Σύνολο καταχωρίσεων",
  "Payments recorded": "Καταγεγραμμένες πληρωμές",
  "Charges minus payments": "Χρεώσεις μείον πληρωμές",
  "Accounts": "Λογαριασμοί",
  "Transactions": "Συναλλαγές",
  "Per transaction": "Ανά συναλλαγή",
  "All recorded payments": "Όλες οι καταγεγραμμένες πληρωμές",
  "Unpaid across accounts": "Ανεξόφλητα όλων των λογαριασμών",
  "All invoice records": "Όλες οι καταχωρίσεις τιμολογίων",
  "Recorded through today": "Καταχωρίσεις έως σήμερα",
  "Positive supplier balances": "Θετικά υπόλοιπα προμηθευτών",
  "Managed properties": "Διαχειριζόμενες κατοικίες",
  "Overdue or never checked": "Εκπρόθεσμες ή χωρίς έλεγχο",
  "Within the last 7 days": "Εντός των τελευταίων 7 ημερών",
  "All open duties": "Όλες οι εκκρεμότητες",
  "Immediate attention": "Άμεση προσοχή",
  "Job history": "Ιστορικό εργασιών",
  "Sign in": "Σύνδεση",
  "Username": "Όνομα χρήστη",
  "Password": "Κωδικός πρόσβασης",
  "Villa Management": "Διαχείριση κατοικιών"
};
function tr(value) { return uiLanguage === "el" && typeof value === "string" ? (greek[value] || value) : value; }
const addModels = {
  villas: ["house", "Add Villa"], customers: ["customer", "Add Customer"],
  suppliers: ["supplier", "Add Supplier"], employees: ["employee", "Add Employee"],
  departments: ["department", "Add Department"], services: ["servicecategory", "Add Service"],
  workEntries: ["workentry", "Add Work Entry"], invoices: ["invoice", "Add Invoice"],
  customerPayments: ["customerpayment", "Add Customer Payment"], supplierPayments: ["supplierpayment", "Add Supplier Payment"],
  companyGas: ["company_gas", "Add Fuel Expense"], programs: ["house", "Add Program"]
};
function AddRecord({page}) {
  const entry = addModels[page];
  if (!entry) return null;
  const [model, label] = entry;
  // Programs are managed as inlines on existing villas, not a standalone admin model.
  const path = `/admin/core/${model}/${page === "programs" ? "" : "add/"}`;
  const href = new URL(path, new URL(API_URL, window.location.origin).origin).href;
  return <a className="refresh-button" href={href} target="_blank" rel="noopener noreferrer" style={{textDecoration:"none"}}>+ {tr(label)}</a>;
}
function InvoiceLink({record}) {
  const label = record.invoice_number || "—";
  if (!record.attachment) return label;
  try {
    const url = new URL(record.attachment, new URL(API_URL, window.location.origin).origin + "/");
    if (!["http:", "https:"].includes(url.protocol)) return label;
    return <a href={url.href} target="_blank" rel="noopener noreferrer">{label} ↗</a>;
  } catch { return label; }
}

const ENDPOINTS = {
  villas: "/villas/",
  customers: "/customers/",
  employees: "/employees/",
  departments: "/departments/",
  services: "/services/",
  workEntries: "/work-entries/",
  programs: "/programs/",
  invoices: "/invoices/",
  servicePrices: "/service-prices/",
  departmentCosts: "/department-costs/",
  suppliers: "/suppliers/",
  supplierPayments: "/supplier-payments/",
  customerPayments: "/customer-payments/",
};

const navigation = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "importantJobs", label: "Important Jobs", icon: Bell },
  { id: "villas", label: "Villas", icon: Building2 },
  { id: "houseChecks", label: "House Checks", icon: ClipboardCheck },
  { id: "waterMeasurements", label: "Water Measurements", icon: Droplets },
  { id: "customers", label: "Customers", icon: Users },
  { id: "customerPayments", label: "Customer Payments", icon: Wallet },
  { id: "suppliers", label: "Suppliers", icon: Truck },
  { id: "supplierPayments", label: "Supplier Payments", icon: CreditCard },
  { id: "employees", label: "Employees", icon: UserRound },
  { id: "companyGas", label: "Company Gas", icon: Truck },
  { id: "departments", label: "Departments", icon: BriefcaseBusiness },
  { id: "services", label: "Services", icon: Sprout },
  { id: "workEntries", label: "Work Entries", icon: ClipboardList },
  { id: "invoices", label: "Invoices", icon: FileText },
];

const emptyData = {
  villas: [], customers: [], employees: [], departments: [],
  services: [], workEntries: [], programs: [], invoices: [],
  servicePrices: [], departmentCosts: [],
  suppliers: [], supplierPayments: [], customerPayments: [],
};

function getArray(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  return [];
}

function number(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function money(value) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 2,
  }).format(number(value));
}

function dateLabel(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleDateString("en-GB", {
        day: "2-digit", month: "short", year: "numeric"
      });
}

// Uses the computer's local date rather than UTC.
function getTodayLocalDate() {
  const today = new Date();

  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function getRelatedName(value, fallback = "—") {
  if (value && typeof value === "object") {
    return value.name || value.title || value.full_name ||
      [value.first_name, value.last_name].filter(Boolean).join(" ") || fallback;
  }
  return value ?? fallback;
}

// Programs provide house_name directly in the Django API.
function getVillaName(entry, villas) {
  if (entry.house_name) return entry.house_name;

  const relation = entry.house ?? entry.villa;

  if (relation && typeof relation === "object") {
    return relation.name || "Villa";
  }

  const id = relation ?? entry.house_id ?? entry.villa_id;
  const villa = villas.find((item) => String(item.id) === String(id));

  return villa?.name || (id ? `Villa #${id}` : "—");
}

function getEmployeeName(entry) {
  // Work-entry API responses include employee_name even when employee is only an ID.
  if (entry.employee_name) return entry.employee_name;

  const employee = entry.employee;
  if (employee && typeof employee === "object") {
    return employee.full_name ||
      [employee.first_name, employee.last_name].filter(Boolean).join(" ") ||
      employee.name || "Employee";
  }
  return employee ? `Employee #${employee}` : "—";
}

function getServiceName(entry, services = []) {
  // Prefer the readable value supplied by the WorkEntry serializer.
  if (entry.service_name) return entry.service_name;

  const relation = entry.service;
  if (relation && typeof relation === "object") {
    return getRelatedName(relation);
  }

  const serviceId = relation ?? entry.service_id;
  const service = services.find((item) => String(item.id) === String(serviceId));
  return service?.name || (serviceId ? `Service #${serviceId}` : "—");
}

// Groups work-entry revenue and gross margin by service department.
function buildDepartmentChart(workEntries, services, departments) {
  const serviceMap = new Map(
    services.map((service) => [String(service.id), service])
  );

  const departmentMap = new Map(
    departments.map((department) => [String(department.id), department])
  );

  const totals = new Map();

  workEntries.forEach((entry) => {
    const serviceValue = entry.service;

    const serviceId =
      serviceValue && typeof serviceValue === "object"
        ? serviceValue.id
        : serviceValue;

    const service =
      serviceMap.get(String(serviceId)) ||
      (serviceValue && typeof serviceValue === "object"
        ? serviceValue
        : null);

    const departmentValue = service?.department;

    const departmentId =
      departmentValue && typeof departmentValue === "object"
        ? departmentValue.id
        : departmentValue;

    const department =
      (departmentId != null
        ? departmentMap.get(String(departmentId))
        : null) ||
      (departmentValue && typeof departmentValue === "object"
        ? departmentValue
        : null);

    const departmentName =
      service?.department_name ||
      department?.name ||
      (departmentId != null
        ? `Department #${departmentId}`
        : "Unassigned");

    const revenue = number(entry.customer_charge);
    const employeeCost = number(entry.employee_cost);

    const current = totals.get(departmentName) || {
      department: departmentName,
      revenue: 0,
      grossMargin: 0,
    };

    current.revenue += revenue;
    current.grossMargin += revenue - employeeCost;

    totals.set(departmentName, current);
  });

  return [...totals.values()].sort((a, b) => b.revenue - a.revenue);
}


// Builds department financial performance from work entries.
// Gross profit follows the existing department chart calculation:
// work-entry revenue minus employee work costs.
function buildDepartmentPerformance(departments, services, workEntries) {
  const serviceMap = new Map(
    services.map((service) => [String(service.id), service])
  );

  const departmentMap = new Map(
    departments.map((department) => [
      String(department.id),
      {
        id: department.id,
        department: department.name || `Department #${department.id}`,
        description: department.description || "",
        revenue: 0,
        expenses: 0,
        grossProfit: 0,
      },
    ])
  );

  const departmentNameMap = new Map(
    [...departmentMap.values()].map((item) => [
      item.department.toLowerCase(),
      item,
    ])
  );

  workEntries.forEach((entry) => {
    const serviceValue = entry.service;
    const serviceId =
      serviceValue && typeof serviceValue === "object"
        ? serviceValue.id
        : serviceValue;

    const service =
      serviceMap.get(String(serviceId)) ||
      (serviceValue && typeof serviceValue === "object" ? serviceValue : null);

    const departmentValue = service?.department;
    const departmentId =
      departmentValue && typeof departmentValue === "object"
        ? departmentValue.id
        : departmentValue;

    let current = departmentId != null
      ? departmentMap.get(String(departmentId))
      : null;

    if (!current && service?.department_name) {
      current = departmentNameMap.get(String(service.department_name).toLowerCase());
    }

    if (!current && departmentValue && typeof departmentValue === "object" && departmentValue.name) {
      current = departmentNameMap.get(String(departmentValue.name).toLowerCase());
    }

    if (!current && typeof departmentValue === "string") {
      current = departmentNameMap.get(departmentValue.toLowerCase());
    }

    if (!current) return;

    current.revenue += number(entry.customer_charge);
    current.expenses += number(entry.employee_cost);
  });

  return [...departmentMap.values()]
    .map((item) => ({
      ...item,
      grossProfit: item.revenue - item.expenses,
    }))
    .sort((a, b) => b.revenue - a.revenue);
}


// Builds service performance from the work entries assigned to each service.
// Gross profit = customer charges - recorded employee work costs.
function buildServicePerformance(services, workEntries, departments) {
  const departmentMap = new Map(
    departments.map((department) => [String(department.id), department.name])
  );

  const totals = new Map(
    services.map((service) => {
      const departmentValue = service.department;
      const departmentId =
        departmentValue && typeof departmentValue === "object"
          ? departmentValue.id
          : departmentValue;
      const departmentName =
        (departmentId != null ? departmentMap.get(String(departmentId)) : null) ||
        (departmentValue && typeof departmentValue === "object"
          ? departmentValue.name
          : null) ||
        (typeof departmentValue === "string" ? departmentValue : "—");

      return [String(service.id), {
        id: service.id,
        name: service.name || `Service #${service.id}`,
        department: departmentName,
        revenue: 0,
        expenses: 0,
        grossProfit: 0,
      }];
    })
  );

  workEntries.forEach((entry) => {
    const serviceValue = entry.service;
    const serviceId =
      serviceValue && typeof serviceValue === "object"
        ? serviceValue.id
        : serviceValue;
    const current = totals.get(String(serviceId));
    if (!current) return;

    current.revenue += number(entry.customer_charge);
    current.expenses += number(entry.employee_cost);
  });

  return [...totals.values()]
    .map((item) => ({
      ...item,
      grossProfit: item.revenue - item.expenses,
      searchText: [item.name, item.department].join(" ").toLowerCase(),
    }))
    .sort((a, b) => b.revenue - a.revenue);
}

// Builds employee performance from their recorded work entries.
// Gross earned = revenue charged to customers - recorded employee work cost.
function buildEmployeePerformance(employees, workEntries, departments) {
  const departmentMap = new Map(
    departments.map((department) => [String(department.id), department.name])
  );

  const totals = new Map(
    employees.map((employee) => {
      const departmentValue = employee.department;
      const departmentId =
        departmentValue && typeof departmentValue === "object"
          ? departmentValue.id
          : departmentValue;
      const departmentName =
        (departmentId != null ? departmentMap.get(String(departmentId)) : null) ||
        (departmentValue && typeof departmentValue === "object"
          ? departmentValue.name
          : null) ||
        (typeof departmentValue === "string" ? departmentValue : "—");

      const salaryType = employee.salary_type || "—";
      const salaryField = salaryType === "hourly"
        ? employee.hourly_rate
        : salaryType === "daily"
          ? employee.daily_rate
          : salaryType === "monthly"
            ? employee.monthly_salary
            : null;
      const salaryUnit = salaryType === "hourly"
        ? "/ hour"
        : salaryType === "daily"
          ? "/ day"
          : salaryType === "monthly"
            ? "/ month"
            : "";

      return [String(employee.id), {
        id: employee.id,
        name: [employee.first_name, employee.last_name].filter(Boolean).join(" ") ||
          employee.name || `Employee #${employee.id}`,
        department: departmentName,
        salaryType,
        salaryDisplay: salaryField === null || salaryField === undefined
          ? "—"
          : `${money(salaryField)} ${salaryUnit}`,
        revenue: 0,
        expenses: 0,
        grossProfit: 0,
      }];
    })
  );

  workEntries.forEach((entry) => {
    const employeeValue = entry.employee;
    const employeeId =
      employeeValue && typeof employeeValue === "object"
        ? employeeValue.id
        : employeeValue;
    const current = totals.get(String(employeeId));
    if (!current) return;

    current.revenue += number(entry.customer_charge);
    current.expenses += number(entry.employee_cost);
  });

  return [...totals.values()]
    .map((item) => ({
      ...item,
      grossProfit: item.revenue - item.expenses,
      searchText: [item.name, item.department, item.salaryType].join(" ").toLowerCase(),
    }))
    .sort((a, b) => b.revenue - a.revenue);
}

// Switchable financial chart used on the Villas, Employees, Departments and Services pages.
function FinancialBreakdownChart({ displayType, revenue, expenses, grossProfit }) {
  const pieData = [
    { name: "Gross profit", value: Math.max(0, number(grossProfit)), color: "#3977b8" },
    { name: "Costs", value: Math.max(0, number(expenses)), color: "#c85b55" },
  ];

  if (displayType === "pie") {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={pieData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius="48%"
            outerRadius="76%"
            paddingAngle={3}
            stroke="none"
            label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
            labelLine={false}
            labelStyle={{ fill: "#ffffff", fontSize: 11, fontWeight: 600 }}
          >
            {pieData.map((slice) => (
              <Cell key={slice.name} fill={slice.color} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => money(value)} />
          <Legend wrapperStyle={{ fontSize: "10px" }} />
        </PieChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={[
          { metric: "Revenue", amount: revenue },
          { metric: "Costs", amount: expenses },
          { metric: "Gross profit", amount: grossProfit },
        ]}
        margin={{ top: 8, right: 4, left: -18, bottom: 4 }}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee9df" />
        <XAxis dataKey="metric" tick={{ fill: "#8b887f", fontSize: 9 }} axisLine={false} tickLine={false} interval={0} />
        <YAxis
          tick={{ fill: "#8b887f", fontSize: 9 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(value) => new Intl.NumberFormat("en-GB", {
            notation: "compact",
            maximumFractionDigits: 1,
          }).format(value)}
        />
        <Tooltip formatter={(value) => money(value)} />
        <Bar dataKey="amount" name={tr("Amount")} radius={[4, 4, 0, 0]} maxBarSize={34} fill="#b99b65" />
      </BarChart>
    </ResponsiveContainer>
  );
}

// Shared searchable, paginated table and three-chart-per-row performance page.
function PerformancePage({
  eyebrow,
  title,
  subtitle,
  tableEyebrow,
  tableTitle,
  items,
  tableColumns,
  searchPlaceholder,
  chartSearchPlaceholder,
  revenueLabel = "Revenue",
  expenseLabel = "Expenses",
  grossLabel = "Gross profit",
  onRefresh,
}) {
  const [tableSearch, setTableSearch] = useState("");
  const [tablePage, setTablePage] = useState(1);
  const [chartSearch, setChartSearch] = useState("");
  const [chartPage, setChartPage] = useState(1);
  const [chartDisplay, setChartDisplay] = useState("bar");
  const tablePageSize = 10;
  const chartPageSize = 9;

  const filteredTable = useMemo(() => {
    const term = tableSearch.trim().toLowerCase();
    return term
      ? items.filter((item) => item.searchText.includes(term))
      : items;
  }, [items, tableSearch]);

  const filteredCharts = useMemo(() => {
    const term = chartSearch.trim().toLowerCase();
    return term
      ? items.filter((item) => item.searchText.includes(term))
      : items;
  }, [items, chartSearch]);

  const tableTotalPages = Math.max(1, Math.ceil(filteredTable.length / tablePageSize));
  const chartTotalPages = Math.max(1, Math.ceil(filteredCharts.length / chartPageSize));
  const paginatedTable = filteredTable.slice(
    (tablePage - 1) * tablePageSize,
    tablePage * tablePageSize
  );
  const paginatedCharts = filteredCharts.slice(
    (chartPage - 1) * chartPageSize,
    chartPage * chartPageSize
  );

  useEffect(() => {
    if (tablePage > tableTotalPages) setTablePage(tableTotalPages);
  }, [tablePage, tableTotalPages]);

  useEffect(() => {
    if (chartPage > chartTotalPages) setChartPage(chartTotalPages);
  }, [chartPage, chartTotalPages]);

  return (
    <>
      <div className="welcome-row">
        <div>
          <p className="eyebrow">{tr(eyebrow)}</p>
          <h1>{tr(title)}</h1>
          <p className="muted">{tr(subtitle)}</p>
        </div>
        {onRefresh && (
          <AddRecord page={title === "Services" ? "services" : "employees"}/>
        )}
      </div>

      <section className="panel table-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">{tr(tableEyebrow)}</p>
            <h2>{tr(tableTitle)}</h2>
          </div>
          <span className="record-count">{filteredTable.length} records</span>
        </div>

        <div className="search-box" style={{ maxWidth: "360px", marginBottom: "16px" }}>
          <Search size={17} />
          <input
            value={tableSearch}
            onChange={(event) => {
              setTableSearch(event.target.value);
              setTablePage(1);
            }}
            placeholder={searchPlaceholder}
            aria-label={`Search ${title.toLowerCase()} table`}
          />
        </div>

        {paginatedTable.length === 0 ? (
          <div className="empty-state">No records match your search.</div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>{tableColumns.map((column) => <th key={column.label}>{tr(column.label)}</th>)}</tr>
              </thead>
              <tbody>
                {paginatedTable.map((item) => (
                  <tr key={item.id}>
                    {tableColumns.map((column) => (
                      <td key={column.label}>
                        {column.render ? column.render(item) : (item[column.key] ?? "—")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <PaginationControls
          page={tablePage}
          totalPages={tableTotalPages}
          totalItems={filteredTable.length}
          onPageChange={setTablePage}
        />
      </section>

      <section className="panel" style={{ marginTop: "22px" }}>
        <div className="panel-heading">
          <div>
            <p className="eyebrow">INDIVIDUAL PERFORMANCE CHARTS</p>
            <h2>{title} performance by revenue</h2>
            <p className="muted" style={{ marginTop: "6px" }}>
              Ordered from highest revenue to lowest revenue.
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <button
              type="button"
              className="refresh-button"
              onClick={() => setChartDisplay(chartDisplay === "bar" ? "pie" : "bar")}
              style={{ padding: "7px 10px", fontSize: "11px" }}
            >
              {chartDisplay === "bar" ? "Switch to pie charts" : "Switch to bar charts"}
            </button>
            <span className="record-count">{filteredCharts.length} charts</span>
          </div>
        </div>

        <div className="search-box" style={{ maxWidth: "360px", marginBottom: "18px" }}>
          <Search size={17} />
          <input
            value={chartSearch}
            onChange={(event) => {
              setChartSearch(event.target.value);
              setChartPage(1);
            }}
            placeholder={chartSearchPlaceholder}
            aria-label={`Search ${title.toLowerCase()} charts`}
          />
        </div>

        {paginatedCharts.length === 0 ? (
          <div className="empty-state">No charts match your search.</div>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
              gap: "18px",
            }}
          >
            {paginatedCharts.map((item) => (
              <div
                key={item.id}
                style={{
                  minWidth: 0,
                  border: "1px solid #eee9df",
                  borderRadius: "12px",
                  padding: "14px 10px 8px",
                  background: "rgba(255,255,255,0.55)",
                }}
              >
                <h3 style={{ margin: "0 0 4px", fontSize: "14px", fontWeight: 600, color: "#3f493f" }}>
                  {item.name}
                </h3>
                <p className="muted" style={{ margin: "0 0 8px", fontSize: "11px" }}>
                  {revenueLabel}: {money(item.revenue)}
                </p>
                <div style={{ width: "100%", height: chartDisplay === "pie" ? "270px" : "190px" }}>
                  <FinancialBreakdownChart
                    displayType={chartDisplay}
                    revenue={item.revenue}
                    expenses={item.expenses}
                    grossProfit={item.grossProfit}
                  />
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: "6px", flexWrap: "wrap", fontSize: "10px", color: "#718477", padding: "2px 4px 4px" }}>
                  <span>{expenseLabel}: {money(item.expenses)}</span>
                  <strong>{grossLabel}: {money(item.grossProfit)}</strong>
                </div>
              </div>
            ))}
          </div>
        )}

        <PaginationControls
          page={chartPage}
          totalPages={chartTotalPages}
          totalItems={filteredCharts.length}
          onPageChange={setChartPage}
        />
      </section>
    </>
  );
}

// Match the backend invoice classification: unassigned or company-owned.
function isCompanyInvoice(invoice, villas) {
  const houseId = relationId(invoice.house ?? invoice.villa ?? invoice.house_id ?? invoice.villa_id);
  if (houseId == null) return true;
  return villas.find((villa) => String(villa.id) === String(houseId))?.is_company_property === true;
}

// Builds total income, outcome and net result for every villa.
function buildVillaChart(villas, workEntries, programs, invoices) {
  const today = getTodayLocalDate();

  const totals = new Map(
    villas.map((villa) => [
      String(villa.id),
      {
        id: villa.id,
        area: villa.area,
        villa: villa.name || `Villa #${villa.id}`,
        income: 0,
        outcome: 0,
        netResult: 0,
        reimbursableInvoices: 0,
      },
    ])
  );

  function getHouseId(item) {
    const house = item.house ?? item.villa;

    if (house && typeof house === "object") {
      return house.id;
    }

    return house ?? item.house_id ?? item.villa_id;
  }

  // Add work revenue and employee costs.
  workEntries.forEach((entry) => {
    const houseId = getHouseId(entry);
    const current = totals.get(String(houseId));

    if (!current) return;

    current.income += number(entry.customer_charge);
    current.outcome += number(entry.employee_cost);
  });

  // Add currently active program revenue.
  programs.forEach((program) => {
    const started = !program.start_date || program.start_date <= today;
    const notEnded = !program.end_date || program.end_date >= today;

    if (!started || !notEnded) return;

    const houseId = getHouseId(program);
    const current = totals.get(String(houseId));

    if (!current) return;

    current.income += number(program.price);
  });

  // Add invoices assigned to each villa.
  invoices.forEach((invoice) => {
    const houseId = getHouseId(invoice);
    const current = totals.get(String(houseId));

    if (!current) return;

    if (isCompanyInvoice(invoice, villas)) {
      current.outcome += number(invoice.amount);
    } else {
      current.reimbursableInvoices += number(invoice.amount);
    }
  });

  return [...totals.values()]
    .map((item) => ({
      ...item,
      netResult: item.income - item.outcome,
    }))
    .sort((a, b) => b.income - a.income);
}

function StatCard({ label, value, detail, icon: Icon }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{tr(label)}</span>
        <span className="stat-icon"><Icon size={19} /></span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-detail">{tr(detail)}</div>
    </div>
  );
}

function LoginScreen({ onLogin, loading, error }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  function submit(event) {
    event.preventDefault();
    onLogin(username, password);
  }

  return (
    <main className="login-page">
      <form className="login-card" onSubmit={submit}>
        <div className="brand-mark">PK</div>
        <p className="eyebrow">VILLA MANAGEMENT</p>
        <h1>PAROS KATOIKIA</h1>
        <p className="login-subtitle">
          Sign in to manage your properties and operations.
        </p>

        {error && <div className="error-message">{error}</div>}

        <label htmlFor="username">{tr("Username")}</label>
        <input
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          required
        />

        <label htmlFor="password">{tr("Password")}</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />

        <button className="primary-button login-button" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>

        <p className="login-footnote">Use your Django account credentials.</p>
      </form>
    </main>
  );
}

function DataTable({
  title,
  columns,
  rows,
  totalCount = rows.length,
  searchValue,
  onSearchChange,
  searchPlaceholder = "Search records...",
  headerActions,
  emptyMessage = "No records have been added yet."
}) {
  return (
    <section className="panel table-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">DATABASE RECORDS</p>
          <h2>{tr(title)}</h2>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          {headerActions}
          <span className="record-count">{totalCount} records</span>
        </div>
      </div>

      {onSearchChange && (
        <div className="search-box" style={{ maxWidth: "360px", marginBottom: "16px" }}>
          <Search size={17} />
          <input
            value={searchValue}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder={searchPlaceholder}
            aria-label={searchPlaceholder}
          />
        </div>
      )}

      {rows.length === 0 ? (
        <div className="empty-state">{emptyMessage}</div>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column.label}>{tr(column.label)}</th>
                ))}
              </tr>
            </thead>

            <tbody>
              {rows.map((row, index) => (
                <tr key={row.id ?? index}>
                  {columns.map((column) => (
                    <td key={column.label}>
                      {column.render
                        ? column.render(row)
                        : (row[column.key] ?? "—")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}


function WorkEntryTable({ rows, columns, search, onSearchChange, data }) {
  const [groupBy, setGroupBy] = useState("none");
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const groupColumns = { Date: "date", Villa: "villa", Employee: "employee", Department: "department", Service: "service" };
  useEffect(() => { setPage(1); }, [search]);
  const groupName = (r) => {
    switch (groupBy) {
      case "villa": return getVillaName(r, data.villas);
      case "employee": return getEmployeeName(r);
      case "service": return getServiceName(r, data.services);
      case "department": return r.department_name || "—";
      case "date": return dateLabel(r.work_date);
      case "month": return r.work_date ? String(r.work_date).slice(0, 7) : "—";
      default: return "";
    }
  };
  const groups = new Map();
  rows.forEach(r => {
    const name = groupName(r);
    if (!groups.has(name)) groups.set(name, []);
    groups.get(name).push(r);
  });
  const ordered = [...groups.entries()].sort(([a], [b]) => a.localeCompare(b, uiLanguage === "el" ? "el" : "en", { numeric: true }));
  const flattened = ordered.flatMap(([name, items]) => items.map(row => ({ name, row, count: items.length })));
  const totalPages = Math.max(1, Math.ceil(flattened.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const visible = flattened.slice((safePage - 1) * pageSize, safePage * pageSize);
  return <section className="panel table-panel">
    <div className="panel-heading"><div><p className="eyebrow">{tr("DATABASE RECORDS")}</p><h2>{tr("Work Entries")}</h2></div><span className="record-count">{rows.length} {tr("records")}</span></div>
    <div style={{display:"flex", gap:12, flexWrap:"wrap", alignItems:"center", marginBottom:16}}>
      <div className="search-box" style={{maxWidth:360}}><Search size={17}/><input value={search} onChange={e => {onSearchChange(e.target.value); setPage(1);}} placeholder={tr("Search employee, villa, department or date...")} aria-label={tr("Search employee, villa, department or date...")}/></div>
    </div>
    {visible.length ? <div className="table-scroll"><table><thead><tr>{columns.map(c => <th key={c.label} scope="col">{groupColumns[c.label] ? <button type="button" aria-pressed={groupBy === groupColumns[c.label]} title={tr("Click to group or ungroup")} onClick={() => {setGroupBy(prev => prev === groupColumns[c.label] ? "none" : groupColumns[c.label]); setPage(1);}} style={{background:"transparent",border:0,padding:0,color:"inherit",font:"inherit",cursor:"pointer",textAlign:"left"}}>{tr(c.label)} {groupBy === groupColumns[c.label] ? "▼" : "↕"}</button> : tr(c.label)}</th>)}</tr></thead><tbody>
      {visible.flatMap(({name,row,count}, i) => [
        groupBy !== "none" && (i === 0 || visible[i-1].name !== name) ? <tr key={`group-${name}`}><td colSpan={columns.length}><strong>{name} · {count} {tr("records")}</strong></td></tr> : null,
        <tr key={`work-${row.id ?? i}`}>{columns.map(c => <td key={c.label}>{c.render ? c.render(row) : (row[c.key] ?? "—")}</td>)}</tr>
      ])}
    </tbody></table></div> : <div className="empty-state">{tr("No work entries match your search.")}</div>}
    {rows.length > 0 && <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:12,flexWrap:"wrap",padding:"14px 2px 2px"}}><span className="muted">{tr("Page")} {safePage} {tr("of")} {totalPages} · {rows.length} {tr("records")}</span><div style={{display:"flex",gap:8}}><button type="button" className="refresh-button" disabled={safePage <= 1} onClick={() => setPage(safePage-1)}>{tr("Previous")}</button><button type="button" className="refresh-button" disabled={safePage >= totalPages} onClick={() => setPage(safePage+1)}>{tr("Next")}</button></div></div>}
  </section>;
}

function PaginationControls({ page, totalPages, onPageChange, totalItems }) {
  if (totalItems === 0) return null;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "12px",
        flexWrap: "wrap",
        padding: "14px 2px 2px",
      }}
    >
      <span className="muted" style={{ fontSize: "12px" }}>
        Page {page} of {totalPages} · {totalItems} records
      </span>
      <div style={{ display: "flex", gap: "8px" }}>
        <button
          type="button"
          className="refresh-button"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          style={{ opacity: page <= 1 ? 0.45 : 1 }}
        >
          {tr("Previous")}
        </button>
        <button
          type="button"
          className="refresh-button"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          style={{ opacity: page >= totalPages ? 0.45 : 1 }}
        >
          {tr("Next")}
        </button>
      </div>
    </div>
  );
}


// Payment records are linked to the party, not to an individual invoice.
// Therefore departmental costs can be grouped, but department-level paid/unpaid
// cannot be asserted from these records.
function relationId(value) {
  if (value && typeof value === "object") return value.id ?? null;
  return value ?? null;
}

function resolveName(value, records, suppliedName) {
  if (suppliedName) return suppliedName;
  if (value && typeof value === "object") return getRelatedName(value);
  const found = records.find((r) => String(r.id) === String(value));
  return found?.name || (value != null ? `#${value}` : "Unassigned");
}

function departmentName(value, departments) {
  return resolveName(value, departments);
}

function percentile(values, fraction) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const position = (sorted.length - 1) * fraction;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (position - lower);
}

function DepartmentBoxplots({ records, title }) {
  const groups = useMemo(() => {
    const byDepartment = new Map();
    records.forEach(({ department, amount }) => {
      if (!byDepartment.has(department)) byDepartment.set(department, []);
      byDepartment.get(department).push(number(amount));
    });
    return [...byDepartment.entries()]
      .map(([name, values]) => ({
        name, count: values.length,
        min: Math.min(...values), q1: percentile(values, 0.25),
        median: percentile(values, 0.5), q3: percentile(values, 0.75),
        max: Math.max(...values), total: values.reduce((a, b) => a + b, 0),
      }))
      .sort((a, b) => b.total - a.total);
  }, [records]);

  const maxValue = Math.max(1, ...groups.map((g) => g.max));
  const scale = (value) => 190 + (value / maxValue) * 550;

  return (
    <section className="panel" style={{ marginTop: 20 }}>
      <div className="panel-heading">
        <div>
          <p className="eyebrow">COST DISTRIBUTION</p>
          <h2>{tr(title)}</h2>
          <p className="muted">Each box shows the middle 50% of individual recorded amounts. Line = median; whiskers = minimum and maximum.</p>
        </div>
      </div>
      {!groups.length ? <div className="empty-state">No departmental costs available.</div> : (
        <div style={{ overflowX: "auto" }}>
          <svg viewBox={`0 0 820 ${Math.max(110, groups.length * 55 + 40)}`} style={{ width: "100%", minWidth: 570, height: Math.max(110, groups.length * 55 + 40) }} role="img" aria-label={title}>
            {groups.map((g, i) => {
              const y = 34 + i * 55;
              return (
                <g key={g.name}>
                  <text x="4" y={y + 5} fill="#526357" fontSize="12">{g.name.slice(0, 25)}</text>
                  <line x1={scale(g.min)} x2={scale(g.max)} y1={y} y2={y} stroke="#718477" strokeWidth="2"/>
                  <line x1={scale(g.min)} x2={scale(g.min)} y1={y - 9} y2={y + 9} stroke="#718477" strokeWidth="2"/>
                  <line x1={scale(g.max)} x2={scale(g.max)} y1={y - 9} y2={y + 9} stroke="#718477" strokeWidth="2"/>
                  <rect x={scale(g.q1)} y={y - 13} width={Math.max(1, scale(g.q3) - scale(g.q1))} height="26" rx="3" fill="#b99b65" fillOpacity=".55" stroke="#8a754e"/>
                  <line x1={scale(g.median)} x2={scale(g.median)} y1={y - 13} y2={y + 13} stroke="#3f493f" strokeWidth="3"/>
                  <title>{`${g.name}: ${g.count} records | min ${money(g.min)} | Q1 ${money(g.q1)} | median ${money(g.median)} | Q3 ${money(g.q3)} | max ${money(g.max)} | total ${money(g.total)}`}</title>
                  <text x="812" textAnchor="end" y={y + 5} fontSize="11" fill="#526357">{money(g.total)}</text>
                </g>
              );
            })}
          </svg>
        </div>
      )}
    </section>
  );
}

function PaymentComparisonChart({ displayType, paid, unpaid }) {
  const values = [
    { name: "Paid", amount: Math.max(0, paid), color: "#718477" },
    { name: "Unpaid", amount: Math.max(0, unpaid), color: "#b99b65" },
  ];
  if (displayType === "pie") {
    return <ResponsiveContainer width="100%" height="100%"><PieChart>
      <Pie data={values} dataKey="amount" nameKey="name" cx="50%" cy="50%" innerRadius="45%" outerRadius="75%" label={({ percent }) => `${(percent * 100).toFixed(0)}%`}>
        {values.map((v) => <Cell key={v.name} fill={v.color}/>)}
      </Pie>
      <Tooltip formatter={(v) => money(v)}/><Legend wrapperStyle={{ fontSize: 11 }}/>
    </PieChart></ResponsiveContainer>;
  }
  return <ResponsiveContainer width="100%" height="100%"><BarChart data={values} margin={{ top: 8, right: 10, left: 0, bottom: 5 }}>
    <CartesianGrid strokeDasharray="3 3" vertical={false}/>
    <XAxis dataKey="name"/><YAxis tickFormatter={(v) => new Intl.NumberFormat("en-GB", { notation: "compact" }).format(v)}/>
    <Tooltip formatter={(v) => money(v)}/>
    <Bar dataKey="amount" name={tr("Amount")} maxBarSize={55} radius={[5, 5, 0, 0]}>
      {values.map((v) => <Cell key={v.name} fill={v.color}/>)}
    </Bar>
  </BarChart></ResponsiveContainer>;
}

function DepartmentCostBars({ records, title }) {
  const grouped = useMemo(() => {
    const totals = new Map();
    records.forEach(({ department, amount }) => totals.set(department, (totals.get(department) || 0) + number(amount)));
    return [...totals.entries()].map(([department, amount]) => ({ department, amount })).sort((a, b) => b.amount - a.amount);
  }, [records]);
  return <section className="panel" style={{ marginTop: 20 }}>
    <div className="panel-heading"><div><p className="eyebrow">COST DISTRIBUTION</p><h2>{tr(title)}</h2><p className="muted">Total recorded amounts grouped by department.</p></div></div>
    {grouped.length ? <div style={{ width: "100%", height: Math.max(290, grouped.length * 52 + 55) }}>
      <ResponsiveContainer width="100%" height="100%"><BarChart data={grouped} layout="vertical" margin={{ top: 5, right: 35, left: 40, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false}/>
        <XAxis type="number" tickFormatter={(v) => new Intl.NumberFormat("en-GB", { notation: "compact" }).format(v)}/>
        <YAxis type="category" dataKey="department" width={120} tick={{ fontSize: 11 }}/>
        <Tooltip formatter={(v) => money(v)}/>
        <Bar dataKey="amount" name={tr("Amount")} fill="#b99b65" radius={[0, 5, 5, 0]} maxBarSize={26}/>
      </BarChart></ResponsiveContainer>
    </div> : <div className="empty-state">No departmental amounts available.</div>}
  </section>;
}

function AccountAnalytics({ kind, data, onRefresh, token }) {
  const [exportingId, setExportingId] = useState(null);
  const [exportError, setExportError] = useState("");
  const [exportMonth, setExportMonth] = useState(() => getTodayLocalDate().slice(0, 7));

  async function downloadCustomerStatement(customer) {
    setExportingId(customer.id);
    setExportError("");
    try {
      const response = await fetch(`${API_URL}/customers/${customer.id}/export-statement/?month=${encodeURIComponent(exportMonth)}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || `Export failed (${response.status})`);
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `Customer_${customer.id}_Statement_${exportMonth}.zip`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setExportError(err.message || "Could not export statement");
    } finally {
      setExportingId(null);
    }
  }
  const isSupplier = kind === "supplier";
  const parties = isSupplier ? data.suppliers : data.customers;
  const payments = isSupplier ? data.supplierPayments : data.customerPayments;
  const today = getTodayLocalDate();
  const [paymentDisplay, setPaymentDisplay] = useState("bar");
  const [accountDisplay, setAccountDisplay] = useState("bar");
  const [accountSearch, setAccountSearch] = useState("");
  const [accountPage, setAccountPage] = useState(1);
  const [chartSearch, setChartSearch] = useState("");
  const [chartPage, setChartPage] = useState(1);
  const PAGE_SIZE = 10;
  const CHART_PAGE_SIZE = 9;

  const { rows, costs } = useMemo(() => {
    const partyMap = new Map(parties.map((p) => [String(p.id), {
      id: p.id, name: p.name || `#${p.id}`, charged: 0, paid: 0,
      departments: new Map(),
    }]));
    const costRecords = [];
    const villaCustomer = new Map(data.villas.map((v) => [String(v.id), relationId(v.customer)]));

    function addCharge(partyId, department, amount) {
      const party = partyMap.get(String(partyId));
      if (!party || !Number.isFinite(Number(amount))) return;
      const value = number(amount);
      party.charged += value;
      party.departments.set(department, (party.departments.get(department) || 0) + value);
      costRecords.push({ department, amount: value });
    }

    if (isSupplier) {
      data.invoices.forEach((invoice) => {
        if (invoice.invoice_date && invoice.invoice_date > today) return;
        const id = relationId(invoice.supplier ?? invoice.supplier_entity);
        addCharge(id, departmentName(invoice.department, data.departments), invoice.amount);
      });
    } else {
      data.workEntries.forEach((entry) => {
        if (entry.work_date && entry.work_date > today) return;
        const houseId = relationId(entry.house ?? entry.villa ?? entry.house_id);
        const customerId = villaCustomer.get(String(houseId));
        const serviceId = relationId(entry.service);
        const service = data.services.find((s) => String(s.id) === String(serviceId));
        const dept = service?.department ?? entry.department;
        addCharge(customerId, departmentName(dept, data.departments), entry.customer_charge);
      });
      // Supplier invoices attached to villas are treated as reimbursable.
      data.invoices.forEach((invoice) => {
        if (invoice.invoice_date && invoice.invoice_date > today) return;
        const customerId = villaCustomer.get(String(relationId(invoice.house ?? invoice.house_id)));
        addCharge(customerId, departmentName(invoice.department, data.departments), invoice.amount);
      });
      // Use the same full-month overlap rule as get_monthly_program_revenue.
      // Missing start dates cannot establish a historical opening balance,
      // so these programs are excluded until a start date is supplied.
      data.programs.forEach((program) => {
        const houseId = relationId(program.house ?? program.villa ?? program.house_id);
        const customerId = villaCustomer.get(String(houseId));
        if (!program.start_date || !customerId) return;
        const first = program.start_date.slice(0, 7);
        const last = (program.end_date || today).slice(0, 7);
        const current = today.slice(0, 7);
        let [year, month] = first.split("-").map(Number);
        let count = 0;
        while (`${year}-${String(month).padStart(2, "0")}` <= last &&
               `${year}-${String(month).padStart(2, "0")}` <= current &&
               count < 2400) {
          count++;
          month++;
          if (month > 12) { year++; month = 1; }
        }
        if (count) addCharge(customerId, "Villa programs (not departmental)", number(program.price) * count);
      });
    }

    payments.forEach((payment) => {
      if (payment.payment_date && payment.payment_date > today) return;
      const id = relationId(isSupplier ? payment.supplier : payment.customer);
      const party = partyMap.get(String(id));
      if (party) party.paid += number(payment.amount);
    });

    return {
      rows: [...partyMap.values()].map((p) => ({
        ...p, balance: p.charged - p.paid,
        searchText: p.name.toLowerCase(),
      })).sort((a, b) => b.charged - a.charged),
      costs: costRecords,
    };
  }, [parties, payments, data, isSupplier, today]);

  const total = rows.reduce((a, r) => a + r.charged, 0);
  const paid = rows.reduce((a, r) => a + r.paid, 0);
  const balance = total - paid;
  const filteredAccounts = rows.filter((r) => r.searchText.includes(accountSearch.trim().toLowerCase()));
  const accountPages = Math.max(1, Math.ceil(filteredAccounts.length / PAGE_SIZE));
  const safeAccountPage = Math.min(accountPage, accountPages);
  const visibleAccounts = filteredAccounts.slice((safeAccountPage - 1) * PAGE_SIZE, safeAccountPage * PAGE_SIZE);
  const filteredCharts = rows.filter((r) => r.searchText.includes(chartSearch.trim().toLowerCase()));
  const chartPages = Math.max(1, Math.ceil(filteredCharts.length / CHART_PAGE_SIZE));
  const safeChartPage = Math.min(chartPage, chartPages);
  const visibleCharts = filteredCharts.slice((safeChartPage - 1) * CHART_PAGE_SIZE, safeChartPage * CHART_PAGE_SIZE);

  return (
    <>
      <div className="welcome-row">
        <div>
          <p className="eyebrow">{isSupplier ? tr("SUPPLIER ACCOUNTS") : tr("CUSTOMER ACCOUNTS")}</p>
          <h1>{isSupplier ? tr("Supplier statistics") : tr("Customer statistics")}</h1>
          <p className="muted">{tr("Recorded charges, payments, outstanding balances and cost distributions by department.")}</p>
        </div>
        <AddRecord page={isSupplier ? "suppliers" : "customers"}/>
      </div>
      <div className="stats-grid">
        <StatCard label={isSupplier ? tr("Supplier invoices") : tr("Customer charges")} value={money(total)} detail={tr("Total recorded")} icon={FileText}/>
        <StatCard label={tr("Paid")} value={money(paid)} detail={tr("Payments recorded")} icon={Wallet}/>
        <StatCard label={balance >= 0 ? tr("Unpaid balance") : tr("Credit balance")} value={money(Math.abs(balance))} detail={tr("Charges minus payments")} icon={CreditCard}/>
        <StatCard label={isSupplier ? tr("Suppliers") : tr("Customers")} value={rows.length} detail={tr("Accounts")} icon={Users}/>
      </div>
      <section className="panel" style={{ marginTop: 20 }}>
        <div className="panel-heading">
          <div><p className="eyebrow">{tr("PAYMENT STATUS")}</p><h2>Paid vs outstanding</h2></div>
          <button className="refresh-button" type="button" onClick={() => setPaymentDisplay((v) => v === "bar" ? "pie" : "bar")}>Switch to {paymentDisplay === "bar" ? "pie" : "bar"} chart</button>
        </div>
        <div style={{ width: "100%", height: 280 }}>
          <PaymentComparisonChart displayType={paymentDisplay} paid={paid} unpaid={Math.max(0, balance)} />
        </div>
        {balance < 0 && <p className="muted">Net account credit: {money(-balance)}. Credits are not included in the unpaid chart.</p>}
      </section>
      <DepartmentCostBars
        records={costs}
        title={isSupplier ? "Supplier invoice costs by department" : "Customer charges by department"}
      />
      <section className="panel table-panel" style={{ marginTop: 20 }}>
        <div className="panel-heading">
          <div><p className="eyebrow">ACCOUNT BALANCES</p><h2>Totals by {isSupplier ? "supplier" : "customer"}</h2></div>
          <span className="record-count">{filteredAccounts.length} records</span>
        </div>
        {!isSupplier && (
          <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
            <label htmlFor="customer-statement-month"><strong>Statement billing month</strong></label>
            <input
              id="customer-statement-month"
              type="month"
              value={exportMonth}
              max={today.slice(0, 7)}
              onChange={(event) => setExportMonth(event.target.value)}
              style={{ padding: "10px 14px", border: "1px solid #d9e2d9", borderRadius: 8 }}
            />
            <span className="muted">Select the month before exporting a customer statement.</span>
          </div>
        )}
        <div className="search-box" style={{ maxWidth: 360, marginBottom: 16 }}>
          <Search size={17}/>
          <input value={accountSearch} onChange={(e) => {setAccountSearch(e.target.value);setAccountPage(1);}} placeholder={`Search ${isSupplier ? "suppliers" : "customers"}...`} />
        </div>
        <div className="table-scroll"><table>
          <thead><tr><th>{tr("Name")}</th><th>{tr("Charges")}</th><th>{tr("Paid")}</th><th>{tr("Unpaid / credit")}</th><th>{tr("Department breakdown")}</th>{!isSupplier && <th>{tr("Export data")}</th>}</tr></thead>
          <tbody>{visibleAccounts.map((r) => <tr key={r.id}>
            <td>{r.name}</td><td>{money(r.charged)}</td><td>{money(r.paid)}</td>
            <td>{r.balance < 0 ? `${money(-r.balance)} credit` : money(r.balance)}</td>
            <td>{[...r.departments.entries()].map(([d, amount]) => `${d}: ${money(amount)}`).join(" · ") || "—"}</td>
            {!isSupplier && <td><button type="button" className="refresh-button" disabled={exportingId !== null} onClick={() => downloadCustomerStatement(r)} style={{whiteSpace:"nowrap"}}><Download size={15}/>{exportingId === r.id ? "Preparing…" : "Export ZIP"}</button></td>}
          </tr>)}</tbody>
        </table></div>
        {exportError && <p role="alert" style={{color:"#b42318",marginTop:12}}>{exportError}</p>}
        {!visibleAccounts.length && <div className="empty-state">No matching accounts.</div>}
        <PaginationControls page={safeAccountPage} totalPages={accountPages} totalItems={filteredAccounts.length} onPageChange={setAccountPage}/>
        <p className="muted" style={{ marginTop: 12 }}>Payments are recorded against the entire account, not individual invoices or departments. Department-level paid/unpaid amounts cannot be determined. {!isSupplier && "Customer programs without start dates are excluded from historical totals. "}Negative balances are credits.</p>
      </section>
      <section className="panel" style={{ marginTop: 22 }}>
        <div className="panel-heading">
          <div>
            <p className="eyebrow">INDIVIDUAL ACCOUNT CHARTS</p>
            <h2>{isSupplier ? tr("Supplier") : tr("Customer")} payment performance</h2>
            <p className="muted">Individual account charges, payments and outstanding balances.</p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <button className="refresh-button" type="button" onClick={() => setAccountDisplay((v) => v === "bar" ? "pie" : "bar")}>Switch to {accountDisplay === "bar" ? "pie" : "bar"} charts</button>
            <span className="record-count">{filteredCharts.length} charts</span>
          </div>
        </div>
        <div className="search-box" style={{ maxWidth: 360, marginBottom: 18 }}>
          <Search size={17}/>
          <input value={chartSearch} onChange={(e) => {setChartSearch(e.target.value);setChartPage(1);}} placeholder={`Search ${isSupplier ? "supplier" : "customer"} charts...`} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 18 }}>
          {visibleCharts.map((r) => <div key={r.id} style={{ minWidth: 0, border: "1px solid #eee9df", borderRadius: 12, padding: "14px 10px 8px", background: "rgba(255,255,255,0.55)" }}>
            <h3 style={{ margin: "0 0 4px", fontSize: 14, color: "#3f493f" }}>{r.name}</h3>
            <p className="muted" style={{ fontSize: 11 }}>Total charges: {money(r.charged)}</p>
            <div style={{ width: "100%", height: 210 }}>
              <PaymentComparisonChart displayType={accountDisplay} paid={r.paid} unpaid={Math.max(0, r.balance)}/>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", fontSize: 11, color: "#718477" }}>
              <span>Paid: {money(r.paid)}</span>
              <strong>{r.balance < 0 ? `Credit: ${money(-r.balance)}` : `Unpaid: ${money(r.balance)}`}</strong>
            </div>
          </div>)}
        </div>
        {!visibleCharts.length && <div className="empty-state">No matching charts.</div>}
        <PaginationControls page={safeChartPage} totalPages={chartPages} totalItems={filteredCharts.length} onPageChange={setChartPage}/>
      </section>
    </>
  );
}

function PaymentsAnalytics({ kind, data, onRefresh }) {
  const isSupplier = kind === "supplier";
  const payments = isSupplier ? data.supplierPayments : data.customerPayments;
  const parties = isSupplier ? data.suppliers : data.customers;
  const title = isSupplier ? "Supplier Payments" : "Customer Payments";
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [chartSearch, setChartSearch] = useState("");
  const [chartPage, setChartPage] = useState(1);
  const [chartDisplay, setChartDisplay] = useState("bar");
  const [totalDisplay, setTotalDisplay] = useState("bar");
  const today = getTodayLocalDate();
  const enriched = useMemo(() => payments.map((payment) => ({
    ...payment,
    partyName: resolveName(isSupplier ? payment.supplier : payment.customer, parties,
      isSupplier ? payment.supplier_name : payment.customer_name),
  })), [payments, parties, isSupplier]);
  const visiblePayments = enriched.filter((r) =>
    [r.partyName, r.reference, r.notes, r.payment_date, r.amount]
      .join(" ").toLowerCase().includes(search.trim().toLowerCase())
  );
  const paymentPages = Math.max(1, Math.ceil(visiblePayments.length / 10));
  const safePage = Math.min(page, paymentPages);
  const pageRows = visiblePayments.slice((safePage - 1) * 10, safePage * 10);
  const totals = useMemo(() => {
    const map = new Map(parties.map((p) => [String(p.id), { id: p.id, name: p.name || `#${p.id}`, paid: 0, charged: 0 }]));
    enriched.forEach((payment) => {
      if (payment.payment_date && payment.payment_date > today) return;
      const id = relationId(isSupplier ? payment.supplier : payment.customer);
      const party = map.get(String(id));
      if (party) party.paid += number(payment.amount);
    });
    if (isSupplier) {
      data.invoices.forEach((invoice) => {
        if (invoice.invoice_date && invoice.invoice_date > today) return;
        const party = map.get(String(relationId(invoice.supplier)));
        if (party) party.charged += number(invoice.amount);
      });
    } else {
      const villaCustomer = new Map(data.villas.map((v) => [String(v.id), relationId(v.customer)]));
      data.workEntries.forEach((entry) => {
        if (entry.work_date && entry.work_date > today) return;
        const customerId = villaCustomer.get(String(relationId(entry.house ?? entry.villa ?? entry.house_id)));
        const party = map.get(String(customerId));
        if (party) party.charged += number(entry.customer_charge);
      });
      data.invoices.forEach((invoice) => {
        if (invoice.invoice_date && invoice.invoice_date > today) return;
        const customerId = villaCustomer.get(String(relationId(invoice.house ?? invoice.house_id)));
        const party = map.get(String(customerId));
        if (party) party.charged += number(invoice.amount);
      });
      data.programs.forEach((program) => {
        const customerId = villaCustomer.get(String(relationId(program.house ?? program.villa ?? program.house_id)));
        const party = map.get(String(customerId));
        if (!party || !program.start_date) return;
        let [year, month] = program.start_date.slice(0, 7).split("-").map(Number);
        const last = (program.end_date || today).slice(0, 7);
        let count = 0;
        while (`${year}-${String(month).padStart(2, "0")}` <= last &&
               `${year}-${String(month).padStart(2, "0")}` <= today.slice(0, 7) && count < 2400) {
          count++; month++;
          if (month > 12) { year++; month = 1; }
        }
        party.charged += count * number(program.price);
      });
    }
    return [...map.values()].map((r) => ({ ...r, unpaid: Math.max(0, r.charged - r.paid), balance: r.charged - r.paid }))
      .sort((a, b) => b.paid - a.paid);
  }, [parties, enriched, data, isSupplier, today]);
  const totalPaid = totals.reduce((sum, r) => sum + r.paid, 0);
  const totalUnpaid = totals.reduce((sum, r) => sum + r.unpaid, 0);
  const filteredCharts = totals.filter((r) => r.name.toLowerCase().includes(chartSearch.trim().toLowerCase()));
  const chartPages = Math.max(1, Math.ceil(filteredCharts.length / 9));
  const safeChartPage = Math.min(chartPage, chartPages);
  const chartRows = filteredCharts.slice((safeChartPage - 1) * 9, safeChartPage * 9);

  return <>
    <div className="welcome-row"><div>
      <p className="eyebrow">{tr("PAYMENT STATISTICS")}</p><h1>{tr(title)}</h1>
      <p className="muted">{tr("Recorded payments, outstanding account balances and individual payment charts.")}</p>
    </div><AddRecord page={isSupplier ? "supplierPayments" : "customerPayments"}/></div>
    <div className="stats-grid">
      <StatCard label={tr("Total payments")} value={money(enriched.reduce((a, r) => a + number(r.amount), 0))} detail={tr("All recorded payments")} icon={Wallet}/>
      <StatCard label={tr("Payment records")} value={enriched.length} detail={tr("Transactions")} icon={CreditCard}/>
      <StatCard label={tr("Average payment")} value={money(enriched.length ? enriched.reduce((a, r) => a + number(r.amount), 0) / enriched.length : 0)} detail={tr("Per transaction")} icon={ChartNoAxesCombined}/>
      <StatCard label={tr("Outstanding")} value={money(totalUnpaid)} detail={tr("Unpaid across accounts")} icon={FileText}/>
    </div>
    <section className="panel" style={{ marginTop: 20 }}>
      <div className="panel-heading"><div><p className="eyebrow">{tr("PAYMENT STATUS")}</p><h2>Paid vs unpaid</h2></div>
        <button className="refresh-button" type="button" onClick={() => setTotalDisplay(v => v === "bar" ? "pie" : "bar")}>Switch to {totalDisplay === "bar" ? "pie" : "bar"} chart</button>
      </div>
      <div style={{ height: 280, width: "100%" }}><PaymentComparisonChart displayType={totalDisplay} paid={totalPaid} unpaid={totalUnpaid}/></div>
    </section>
    <section className="panel table-panel" style={{ marginTop: 20 }}>
      <div className="panel-heading"><div><p className="eyebrow">PAYMENT RECORDS</p><h2>{title} table</h2></div><span className="record-count">{visiblePayments.length} records</span></div>
      <div className="search-box" style={{ maxWidth: 360, marginBottom: 16 }}><Search size={17}/>
        <input value={search} onChange={e => {setSearch(e.target.value);setPage(1);}} placeholder="Search payments, names, references..."/>
      </div>
      <div className="table-scroll"><table><thead><tr><th>{tr("Date")}</th><th>{isSupplier ? tr("Supplier") : tr("Customer")}</th><th>{tr("Amount")}</th><th>{tr("Reference")}</th><th>{tr("Notes")}</th></tr></thead>
        <tbody>{pageRows.map((r) => <tr key={r.id}><td>{dateLabel(r.payment_date)}</td><td>{r.partyName}</td><td>{money(r.amount)}</td><td>{r.reference || "—"}</td><td>{r.notes || "—"}</td></tr>)}</tbody>
      </table></div>
      {!pageRows.length && <div className="empty-state">No matching payments.</div>}
      <PaginationControls page={safePage} totalPages={paymentPages} totalItems={visiblePayments.length} onPageChange={setPage}/>
    </section>
    <section className="panel" style={{ marginTop: 22 }}>
      <div className="panel-heading"><div><p className="eyebrow">INDIVIDUAL ACCOUNT CHARTS</p><h2>Payment performance by {isSupplier ? "supplier" : "customer"}</h2>
        <p className="muted">Account-level payments and outstanding balances, sorted by total paid.</p></div>
        <button className="refresh-button" type="button" onClick={() => setChartDisplay(v => v === "bar" ? "pie" : "bar")}>Switch to {chartDisplay === "bar" ? "pie" : "bar"} charts</button>
      </div>
      <div className="search-box" style={{ maxWidth: 360, marginBottom: 18 }}><Search size={17}/>
        <input value={chartSearch} onChange={e => {setChartSearch(e.target.value);setChartPage(1);}} placeholder={`Search ${isSupplier ? "supplier" : "customer"} charts...`}/>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 18 }}>
        {chartRows.map((r) => <div key={r.id} style={{ minWidth: 0, border: "1px solid #eee9df", borderRadius: 12, padding: 14 }}>
          <h3 style={{ fontSize: 14, margin: "0 0 5px" }}>{r.name}</h3>
          <p className="muted" style={{ fontSize: 11 }}>Paid: {money(r.paid)}</p>
          <div style={{ height: 205 }}><PaymentComparisonChart displayType={chartDisplay} paid={r.paid} unpaid={r.unpaid}/></div>
          <p className="muted" style={{ fontSize: 11 }}>Charged: {money(r.charged)} · {r.balance < 0 ? `Credit: ${money(-r.balance)}` : `Unpaid: ${money(r.unpaid)}`}</p>
        </div>)}
      </div>
      {!chartRows.length && <div className="empty-state">No matching charts.</div>}
      <PaginationControls page={safeChartPage} totalPages={chartPages} totalItems={filteredCharts.length} onPageChange={setChartPage}/>
      <p className="muted" style={{ marginTop: 12 }}>Payments are allocated at account level, not to individual invoices or departments. Customer invoices attached to villas are treated as reimbursable; programs without start dates are excluded from historical totals.</p>
    </section>
  </>;
}


// Invoices have no invoice-level settlement link. Paid/unpaid is supplier-account level.
function InvoiceAnalytics({ data, onRefresh }) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [chartSearch, setChartSearch] = useState("");
  const [chartPage, setChartPage] = useState(1);
  const [summaryDisplay, setSummaryDisplay] = useState("bar");
  const [individualDisplay, setIndividualDisplay] = useState("bar");
  const today = getTodayLocalDate();

  const invoices = useMemo(() => data.invoices.map((r) => ({
    ...r,
    supplierId: relationId(r.supplier),
    supplierName: resolveName(r.supplier, data.suppliers, r.supplier_name),
    departmentName: departmentName(r.department, data.departments),
    villaName: getVillaName(r, data.villas),
    searchText: [r.invoice_number, r.description, r.invoice_date,
      resolveName(r.supplier, data.suppliers, r.supplier_name),
      departmentName(r.department, data.departments), getVillaName(r, data.villas)]
      .join(" ").toLowerCase(),
  })), [data.invoices, data.suppliers, data.departments, data.villas]);

  const { accounts, paid, invoiced, outstanding, credit } = useMemo(() => {
    const map = new Map(data.suppliers.map((supplier) => [String(supplier.id), {
      id: supplier.id, name: supplier.name || `Supplier #${supplier.id}`,
      invoiced: 0, paid: 0, invoiceCount: 0,
    }]));
    invoices.forEach((invoice) => {
      if (invoice.invoice_date && invoice.invoice_date > today) return;
      const account = map.get(String(invoice.supplierId));
      if (!account) return;
      account.invoiced += number(invoice.amount);
      account.invoiceCount++;
    });
    data.supplierPayments.forEach((payment) => {
      if (payment.payment_date && payment.payment_date > today) return;
      const account = map.get(String(relationId(payment.supplier)));
      if (account) account.paid += number(payment.amount);
    });
    const accounts = [...map.values()].map((account) => ({
      ...account, balance: account.invoiced - account.paid,
    })).filter((account) => account.invoiceCount || account.paid)
      .sort((a, b) => b.invoiced - a.invoiced);
    return {
      accounts,
      paid: accounts.reduce((sum, account) => sum + account.paid, 0),
      invoiced: accounts.reduce((sum, account) => sum + account.invoiced, 0),
      outstanding: accounts.reduce((sum, account) => sum + Math.max(0, account.balance), 0),
      credit: accounts.reduce((sum, account) => sum + Math.max(0, -account.balance), 0),
    };
  }, [data.suppliers, data.supplierPayments, invoices, today]);

  const filtered = invoices.filter((r) => r.searchText.includes(search.trim().toLowerCase()));
  const pages = Math.max(1, Math.ceil(filtered.length / 10));
  const safePage = Math.min(page, pages);
  const visible = filtered.slice((safePage - 1) * 10, safePage * 10);
  const filteredCharts = accounts.filter((r) => r.name.toLowerCase().includes(chartSearch.trim().toLowerCase()));
  const chartPages = Math.max(1, Math.ceil(filteredCharts.length / 9));
  const safeChartPage = Math.min(chartPage, chartPages);
  const visibleCharts = filteredCharts.slice((safeChartPage - 1) * 9, safeChartPage * 9);
  const costRecords = invoices.map((r) => ({ department: r.departmentName, amount: r.amount }));

  return <>
    <div className="welcome-row">
      <div><p className="eyebrow">{tr("SUPPLIER INVOICE ANALYTICS")}</p><h1>{tr("Invoices")}</h1>
        <p className="muted">{tr("Invoice totals, departmental costs, supplier balances and individual charts.")}</p></div>
      <AddRecord page={"invoices"}/>
    </div>
    <div className="stats-grid">
      <StatCard label={tr("Total invoiced")} value={money(invoices.reduce((sum, r) => sum + number(r.amount), 0))} detail={tr("All invoice records")} icon={FileText}/>
      <StatCard label={tr("Supplier payments")} value={money(paid)} detail={tr("Recorded through today")} icon={Wallet}/>
      <StatCard label={tr("Outstanding")} value={money(outstanding)} detail={tr("Positive supplier balances")} icon={CreditCard}/>
      <StatCard label={tr("Invoices")} value={invoices.length} detail={`Average ${money(invoices.length ? invoices.reduce((sum, r) => sum + number(r.amount), 0) / invoices.length : 0)}`} icon={ChartNoAxesCombined}/>
    </div>
    <section className="panel" style={{ marginTop: 20 }}>
      <div className="panel-heading"><div><p className="eyebrow">{tr("PAYMENT STATUS")}</p><h2>{tr("Supplier payments vs outstanding")}</h2></div>
        <button className="refresh-button" type="button" onClick={() => setSummaryDisplay(v => v === "bar" ? "pie" : "bar")}>Switch to {summaryDisplay === "bar" ? "pie" : "bar"} chart</button>
      </div>
      <div style={{ width: "100%", height: 280 }}><PaymentComparisonChart displayType={summaryDisplay} paid={paid} unpaid={outstanding}/></div>
      <p className="muted">Payments are recorded per supplier, not per invoice. {credit > 0 ? `Supplier credits: ${money(credit)}. ` : ""}The chart shows account-level payments and outstanding amounts, not invoice settlement status.</p>
    </section>
    <DepartmentCostBars records={costRecords} title="Invoice costs by department"/>
    <section className="panel table-panel" style={{ marginTop: 20 }}>
      <div className="panel-heading"><div><p className="eyebrow">INVOICE RECORDS</p><h2>All invoices</h2></div><span className="record-count">{filtered.length} records</span></div>
      <div className="search-box" style={{ maxWidth: 360, marginBottom: 16 }}><Search size={17}/>
        <input value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} placeholder="Search invoices, suppliers, departments, villas..."/>
      </div>
      <div className="table-scroll"><table><thead><tr><th>{tr("Invoice")}</th><th>{tr("Date")}</th><th>{tr("Supplier")}</th><th>{tr("Department")}</th><th>{tr("Villa")}</th><th>{tr("Amount")}</th></tr></thead>
        <tbody>{visible.map((r, i) => <tr key={r.id ?? i}><td><InvoiceLink record={r}/></td><td>{dateLabel(r.invoice_date)}</td><td>{r.supplierName}</td><td>{r.departmentName}</td><td>{r.villaName}</td><td>{money(r.amount)}</td></tr>)}</tbody>
      </table></div>
      {!visible.length && <div className="empty-state">No matching invoices.</div>}
      <PaginationControls page={safePage} totalPages={pages} totalItems={filtered.length} onPageChange={setPage}/>
    </section>
    <section className="panel" style={{ marginTop: 22 }}>
      <div className="panel-heading"><div><p className="eyebrow">INDIVIDUAL SUPPLIER CHARTS</p><h2>Invoice and payment performance by supplier</h2>
        <p className="muted">Each chart shows supplier-account payments and outstanding balances.</p></div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <button className="refresh-button" type="button" onClick={() => setIndividualDisplay(v => v === "bar" ? "pie" : "bar")}>Switch to {individualDisplay === "bar" ? "pie" : "bar"} charts</button>
          <span className="record-count">{filteredCharts.length} charts</span>
        </div>
      </div>
      <div className="search-box" style={{ maxWidth: 360, marginBottom: 18 }}><Search size={17}/>
        <input value={chartSearch} onChange={e => { setChartSearch(e.target.value); setChartPage(1); }} placeholder="Search supplier charts..."/>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 18 }}>
        {visibleCharts.map((r) => <div key={r.id} style={{ minWidth: 0, border: "1px solid #eee9df", borderRadius: 12, padding: "14px 10px 8px", background: "rgba(255,255,255,0.55)" }}>
          <h3 style={{ margin: "0 0 4px", fontSize: 14, color: "#3f493f" }}>{r.name}</h3>
          <p className="muted" style={{ fontSize: 11 }}>Invoiced: {money(r.invoiced)} · {r.invoiceCount} invoices</p>
          <div style={{ height: 210 }}><PaymentComparisonChart displayType={individualDisplay} paid={r.paid} unpaid={Math.max(0, r.balance)}/></div>
          <p className="muted" style={{ fontSize: 11 }}>Paid: {money(r.paid)} · {r.balance < 0 ? `Credit: ${money(-r.balance)}` : `Outstanding: ${money(r.balance)}`}</p>
        </div>)}
      </div>
      {!visibleCharts.length && <div className="empty-state">No matching supplier charts.</div>}
      <PaginationControls page={safeChartPage} totalPages={chartPages} totalItems={filteredCharts.length} onPageChange={setChartPage}/>
    </section>
  </>;
}

// Form-only presentation styles. No changes to App.css or index.css are required.
const operationLabelStyle = { display: "flex", flexDirection: "column", gap: 8, fontSize: 13, fontWeight: 600, color: "#4b5c50", minWidth: 0 };
const operationInputStyle = { width: "100%", boxSizing: "border-box", minHeight: 44, padding: "11px 13px", border: "1px solid #d8ded5", borderRadius: 9, background: "#ffffff", color: "#36493b", fontSize: 13, fontFamily: "inherit", outlineColor: "#718477" };
const operationHelpStyle = { fontSize: 11, lineHeight: 1.5, fontWeight: 400, color: "#788279" };

// Operational pages use the same panel, search and pagination components as the dashboard.
// Printable weekly field programs. The browser's Print dialog can save these as PDFs.
function openWeeklyFieldProgram({ rows, isWater, generatedAt, printWindow }) {
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[char]));
  const dateText = (value) => {
    if (!value) return "Never checked";
    const parsed = new Date(value);
    return Number.isFinite(parsed.getTime())
      ? parsed.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })
      : "Not available";
  };
  const groups = new Map();
  rows.forEach((house) => {
    const area = String(house.area || "Unassigned area").trim() || "Unassigned area";
    if (!groups.has(area)) groups.set(area, []);
    groups.get(area).push(house);
  });
  const sortedGroups = [...groups.entries()].sort(([a], [b]) => a.localeCompare(b, undefined, { sensitivity: "base" }));
  sortedGroups.forEach(([, houses]) => houses.sort((a, b) =>
    String(a.house_name || "").localeCompare(String(b.house_name || ""), undefined, { sensitivity: "base" })));
  const title = isWater ? "Water Measurement Program" : "House Checking Program";
  const lastKey = isWater ? "last_water_check" : "last_house_check";
  const dueKey = isWater ? "next_water_due" : "next_house_due";
  const groupMarkup = sortedGroups.map(([area, houses]) => `
    <section class="area-group">
      <div class="area-heading"><h2>${escapeHtml(area)}</h2><span>${houses.length} ${houses.length === 1 ? "villa" : "villas"}</span></div>
      <table><thead><tr><th class="done">Done</th><th>Villa / Customer</th><th>Last ${isWater ? "measurement" : "check"}</th><th>Due date</th><th>{tr("Employee")}</th></tr></thead>
      <tbody>${houses.map((house) => `<tr>
        <td class="done"><span class="checkbox"></span></td>
        <td><strong>${escapeHtml(house.house_name || "Unnamed villa")}</strong><small>${escapeHtml(house.customer_name || "")}</small></td>
        <td>${escapeHtml(dateText(house[lastKey]))}</td>
        <td>${escapeHtml(house[dueKey] ? dateText(house[dueKey]) : "Due now")}</td>
        <td><div class="write-line"></div></td>
      </tr><tr class="record-row"><td colspan="5">
        ${isWater ? `<div class="record-fields">
          <div class="record-label">WATER MEASUREMENT RECORD <span class="hint">Complete municipal, tank, or both</span></div>
          <div class="record-line"><strong>Municipal meter:</strong> Reading _____________ L &nbsp;&nbsp; <strong>Tank:</strong> ______________________</div>
          <div class="record-line"><strong>Tank visual level:</strong> &#9633; Full &nbsp; &#9633; 3/4 &nbsp; &#9633; Half &nbsp; &#9633; 1/4 &nbsp; &#9633; Nearly empty &nbsp; &#9633; Empty &nbsp; &#9633; Unknown</div>
          <div class="record-line"><strong>Date / time:</strong> __________________ &nbsp;&nbsp; <strong>Checked by:</strong> __________________________</div>
          <div class="record-line"><strong>Notes:</strong> __________________________________________________________________________</div>
        </div>` : `<div class="record-fields">
          <div class="record-label">HOUSE INSPECTION RECORD</div>
          <div class="record-line"><strong>Condition:</strong> &#9633; Good &nbsp;&nbsp; &#9633; Needs attention &nbsp;&nbsp; &#9633; Urgent issue</div>
          <div class="record-line"><strong>Date / time:</strong> __________________ &nbsp;&nbsp; <strong>Checked by:</strong> __________________________</div>
          <div class="record-line"><strong>Notes / issues:</strong> ___________________________________________________________________</div>
        </div>`}
      </td></tr>`).join("")}</tbody></table>
    </section>`).join("");
  const documentHtml = `<!doctype html><html lang="en"><head><meta charset="utf-8" />
    <title>${escapeHtml(title)} - PAROS KATOIKIA</title>
    <style>
      @page { size: A4 portrait; margin: 15mm 12mm; }
      * { box-sizing: border-box; }
      body { margin: 0; font-family: Arial, Helvetica, sans-serif; color: #24332b; background: #fff; font-size: 11px; }
      .topline { border-top: 5px solid #6d816c; margin-bottom: 18px; }
      .brand { font-size: 11px; letter-spacing: 2.2px; font-weight: 700; color: #6d816c; }
      h1 { font-size: 25px; margin: 7px 0 8px; letter-spacing: -.4px; }
      .subtitle { color: #637269; font-size: 11px; line-height: 1.6; }
      .summary { display: flex; gap: 22px; padding: 13px 0; border-bottom: 1px solid #d9e0d9; margin-bottom: 17px; }
      .summary strong { font-size: 16px; display: block; margin-bottom: 3px; }
      .summary span { color: #637269; font-size: 10px; }
      .area-group { margin: 0 0 20px; break-inside: avoid-page; }
      .area-heading { background: #eef3ed; border-left: 4px solid #6d816c; padding: 9px 11px; display: flex; justify-content: space-between; align-items: center; }
      .area-heading h2 { font-size: 14px; margin: 0; }
      .area-heading span { color: #5c6c61; font-size: 10px; }
      table { width: 100%; border-collapse: collapse; table-layout: fixed; }
      thead { display: table-header-group; }
      th { text-align: left; color: #66776a; font-size: 9px; text-transform: uppercase; letter-spacing: .4px; border-bottom: 1px solid #d9e0d9; padding: 9px 6px; }
      td { border-bottom: 1px solid #e4e9e3; padding: 12px 6px; vertical-align: middle; overflow-wrap: anywhere; }
      tr { break-inside: avoid; }
      .record-row td { padding: 0 6px 14px 6px; border-bottom: 2px solid #d8e2d8; }
      .record-fields { padding: 9px 12px 11px; background: #f6f8f5; border-radius: 5px; line-height: 1.8; }
      .record-label { font-size: 9px; font-weight: 700; letter-spacing: .7px; color: #516a57; margin-bottom: 4px; }
      .record-label .hint { font-weight: 400; letter-spacing: 0; color: #67766a; margin-left: 8px; }
      .record-line { padding: 3px 0; font-size: 10px; }
      .record-line strong { font-size: 10px; }

      th.done, td.done { width: 8%; text-align: center; }
      th:nth-child(2) { width: 30%; } th:nth-child(3) { width: 23%; } th:nth-child(4) { width: 22%; } th:nth-child(5) { width: 17%; }
      td strong { font-size: 11px; } td small { display: block; color: #78837a; font-size: 9px; margin-top: 4px; }
      .checkbox { display: inline-block; width: 17px; height: 17px; border: 1.5px solid #7b8c7c; border-radius: 3px; }
      .write-line { border-bottom: 1px solid #c9d2c9; height: 15px; }
      .empty { padding: 25px 0; font-size: 13px; }
      .footer { margin-top: 25px; padding-top: 12px; border-top: 1px solid #d9e0d9; color: #6c7a6e; font-size: 10px; }
      .print-controls { padding: 12px 0 18px; }
      .print-controls button { background: #526e59; color: white; padding: 10px 16px; border: 0; border-radius: 6px; cursor: pointer; font-weight: 700; }
      @media print { .print-controls { display: none; } }
    </style></head><body>
    <div class="print-controls"><button onclick="window.print()">Print / Save as PDF</button></div>
    <div class="topline"></div><div class="brand">PAROS KATOIKIA · FIELD OPERATIONS</div>
    <h1>${escapeHtml(title)}</h1>
    <div class="subtitle">Villas requiring ${isWater ? "a water measurement" : "a house inspection"} because no check was recorded within the last 7 days. Grouped by area. Fill in the fields on paper during each visit; enter the results in the dashboard afterward.</div>
    <div class="summary"><div><strong>${rows.length}</strong><span>Villas to visit</span></div>
      <div><strong>${sortedGroups.length}</strong><span>Areas</span></div>
      <div><strong>${escapeHtml(dateText(generatedAt))}</strong><span>Generated</span></div></div>
    ${rows.length ? groupMarkup : '<p class="empty">All villas are up to date. No visits are required.</p>'}
    <div class="footer">Employee: __________________________ &nbsp;&nbsp; Visit date: __________________ &nbsp;&nbsp; Supervisor: __________________________</div>
    </body></html>`;
  printWindow.document.open();
  printWindow.document.write(documentHtml);
  printWindow.document.close();
  printWindow.focus();
  // The print window retains a visible Print / Save as PDF button if automatic printing is blocked.
  printWindow.setTimeout(() => { try { printWindow.print(); } catch (_) { /* use visible button */ } }, 400);
}

function WeeklyOperationsPage({ kind, token, villas }) {
  const isWater = kind === "water";
  const title = isWater ? "Water Measurements" : "House Checks";
  const [records, setRecords] = useState([]);
  const [tanks, setTanks] = useState([]);
  const [inspectionHistory, setInspectionHistory] = useState([]);
  const [waterHistory, setWaterHistory] = useState([]);
  const [historySearch, setHistorySearch] = useState("");
  const [historyPage, setHistoryPage] = useState(1);
  const [historyError, setHistoryError] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  useEffect(() => {
    if (!notice) return undefined;
    const timer = window.setTimeout(() => setNotice(""), 6500);
    return () => window.clearTimeout(timer);
  }, [notice]);
  const [needsSearch, setNeedsSearch] = useState("");
  const [checkedSearch, setCheckedSearch] = useState("");
  const [needsPage, setNeedsPage] = useState(1);
  const [checkedPage, setCheckedPage] = useState(1);
  const [selectedHouse, setSelectedHouse] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    checked_by: "", condition: "good", notes: "", water_notes: "",
    method: "municipal", meter_litres: "", tank: "", visual_level: "full",
  });
  const PAGE_SIZE = 10;
  const nowValue = () => {
    const d = new Date();
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  };
  const [checkedAt, setCheckedAt] = useState(nowValue);

  async function request(path, options = {}) {
    const response = await fetch(path.startsWith(`${API_URL}/`) ? path : `${API_URL}${path}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(options.body ? { "Content-Type": "application/json" } : {}),
      },
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      const message = payload.detail || Object.entries(payload).map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(", ") : val}`).join("; ");
      throw new Error(message || `API request failed (${response.status})`);
    }
    return response.status === 204 ? null : response.json();
  }

  async function loadPaginatedHistory(endpoint) {
    const all = [];
    let next = `${endpoint}?page=1`;
    let pages = 0;
    while (next && pages < 1000) {
      const result = await request(next);
      if (Array.isArray(result)) { all.push(...result); break; }
      if (!Array.isArray(result?.results)) throw new Error("Unexpected measurement history response.");
      all.push(...result.results);
      next = result.next || null;
      pages += 1;
    }
    return all;
  }

  async function loadInspectionHistory() {
    const all = [];
    let next = "/house-inspections/?page=1";
    let pages = 0;
    while (next && pages < 1000) {
      const result = await request(next);
      if (Array.isArray(result)) {
        all.push(...result);
        break;
      }
      if (!Array.isArray(result?.results)) {
        throw new Error("Unexpected inspection history response.");
      }
      all.push(...result.results);
      next = result.next || null;
      pages += 1;
    }
    return all.sort((a, b) => {
      const dateDiff = new Date(b.inspection_date).getTime() - new Date(a.inspection_date).getTime();
      return dateDiff || Number(b.id || 0) - Number(a.id || 0);
    });
  }

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [status, tankData] = await Promise.all([
        request("/weekly-checks/"),
        isWater ? request("/water-tanks/") : Promise.resolve([]),
      ]);
      setRecords(Array.isArray(status?.results) ? status.results : []);
      setTanks(Array.isArray(tankData) ? tankData : (tankData?.results || []));
      if (isWater) {
        try {
          const [meters, levels] = await Promise.all([
            loadPaginatedHistory("/water-readings/"),
            loadPaginatedHistory("/water-tank-readings/"),
          ]);
          const tankById = new Map((Array.isArray(tankData) ? tankData : (tankData?.results || [])).map((tank) => [String(tank.id), tank]));
          const combined = [
            ...meters.map((reading) => ({ ...reading, source_type: "municipal", house_id: reading.house, date: reading.reading_date })),
            ...levels.map((reading) => {
              const tank = tankById.get(String(reading.tank));
              return { ...reading, source_type: "tank", house_id: tank?.house, tank_name: tank?.name || `Tank #${reading.tank}`, date: reading.reading_date };
            }),
          ];
          combined.sort((a, b) => (new Date(b.date).getTime() - new Date(a.date).getTime()) || (Number(b.id || 0) - Number(a.id || 0)));
          setWaterHistory(combined);
          setHistoryError("");
        } catch (historyErr) {
          setHistoryError(historyErr.message || "Unable to load water measurement history.");
        }
      } else {
        try {
          setInspectionHistory(await loadInspectionHistory());
          setHistoryError("");
        } catch (historyErr) {
          setHistoryError(historyErr.message || "Unable to load inspection history.");
        }
      }
    } catch (err) {
      setError(err.message || "Unable to load weekly checks.");
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { if (token) load(); }, [token, isWater]);

  const field = isWater ? "water_missing" : "house_missing";
  const dateField = isWater ? "last_water_check" : "last_house_check";
  const dueField = isWater ? "next_water_due" : "next_house_due";
  const missing = records.filter((item) => item[field]);
  const checked = records.filter((item) => !item[field]);
  const matches = (item, search) => [item.house_name, item.customer_name, item.area]
    .join(" ").toLowerCase().includes(search.trim().toLowerCase());
  const missingFiltered = missing.filter((item) => matches(item, needsSearch));
  const checkedFiltered = checked.filter((item) => matches(item, checkedSearch));
  const missingPages = Math.max(1, Math.ceil(missingFiltered.length / PAGE_SIZE));
  const checkedPages = Math.max(1, Math.ceil(checkedFiltered.length / PAGE_SIZE));
  const missingSafePage = Math.min(needsPage, missingPages);
  const checkedSafePage = Math.min(checkedPage, checkedPages);
  const historyMatches = (isWater ? waterHistory : inspectionHistory).filter((item) => {
    if (isWater) {
      const villaName = villas.find((villa) => String(villa.id) === String(item.house_id))?.name || "";
      const sourceLabel = item.source_type === "municipal" ? "Municipal meter" : "Water tank";
      const levelLabel = (item.visual_level || "").replace(/_/g, " ");
      return [villaName, sourceLabel, item.tank_name, item.checked_by, item.notes, item.date, item.meter_litres, levelLabel]
        .join(" ").toLowerCase().includes(historySearch.trim().toLowerCase());
    }
    const villaName = item.house_name || villas.find((villa) => String(villa.id) === String(item.house))?.name || "";
    const conditionLabel = item.condition_display || ({ good: "Good", attention: "Needs attention", urgent: "Urgent issue" }[item.condition] || item.condition || "");
    return [villaName, item.checked_by, conditionLabel, item.notes, item.inspection_date]
      .join(" ").toLowerCase().includes(historySearch.trim().toLowerCase());
  });
  const historyPages = Math.max(1, Math.ceil(historyMatches.length / 15));
  const historySafePage = Math.min(historyPage, historyPages);
  const visibleHistory = historyMatches.slice((historySafePage - 1) * 15, historySafePage * 15);
  const houseTanks = tanks.filter((tank) => String(tank.house) === String(selectedHouse));
  const parsedCheckDate = checkedAt ? new Date(checkedAt) : null;
  const localIso = parsedCheckDate && Number.isFinite(parsedCheckDate.getTime()) ? parsedCheckDate.toISOString() : null;
  const nextCheckDates = checked.map((item) => new Date(item[dueField]).getTime()).filter(Number.isFinite);
  const nextCheckText = nextCheckDates.length
    ? `Next ${isWater ? "measurement" : "check"}: ${new Date(Math.min(...nextCheckDates)).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })}`
    : `No upcoming ${isWater ? "water measurements" : "house checks"} scheduled.`;

  async function printProgram() {
    // Open synchronously with the click so browser popup blockers do not prevent the PDF view.
    const printWindow = window.open("", "_blank");
    if (!printWindow) {
      setError("Allow pop-ups for this site to print or save the checking program as a PDF.");
      return;
    }
    printWindow.document.write("<html><head><title>Preparing field program...</title></head><body><p>Preparing the latest villa checking program...</p></body></html>");
    setError("");
    try {
      // Always get current statuses from Django, not the current table page or search filter.
      const status = await request("/weekly-checks/");
      if (!Array.isArray(status?.results)) throw new Error("Unexpected weekly checks response.");
      const field = isWater ? "water_missing" : "house_missing";
      const outstanding = status.results.filter((house) => house[field]);
      openWeeklyFieldProgram({ rows: outstanding, isWater, generatedAt: new Date(), printWindow });
    } catch (err) {
      printWindow.close();
      setError(err.message || "Could not prepare the field program.");
    }
  }

  async function submit(event) {
    event.preventDefault();
    setError(""); setNotice("");
    if (!selectedHouse || !localIso) { setError("Select a villa and valid date."); return; }
    if (new Date(localIso).getTime() > Date.now()) { setError("Check date cannot be in the future."); return; }
    setSaving(true);
    try {
      if (!isWater) {
        await request("/house-inspections/", { method: "POST", body: JSON.stringify({
          house: Number(selectedHouse), inspection_date: localIso,
          checked_by: form.checked_by, condition: form.condition, notes: form.notes,
        }) });
      } else {
        const municipal = form.method === "municipal" || form.method === "both";
        const tank = form.method === "tank" || form.method === "both";
        if (municipal) {
          await request("/water-readings/", { method: "POST", body: JSON.stringify({
            house: Number(selectedHouse), reading_date: localIso,
            meter_litres: form.meter_litres, checked_by: form.checked_by, notes: form.water_notes,
          }) });
        }
        if (tank) {
          await request("/water-tank-readings/", { method: "POST", body: JSON.stringify({
            tank: Number(form.tank), reading_date: localIso,
            visual_level: form.visual_level, checked_by: form.checked_by, notes: form.water_notes,
          }) });
        }
      }
      setCheckedAt(nowValue());
      setForm((prev) => ({ ...prev, notes: "", water_notes: "", meter_litres: "" }));
      await load();
      setNotice(`${title} saved successfully. The villa lists have been refreshed.`);
    } catch (err) {
      setError(err.message || "Could not save the check.");
    } finally {
      setSaving(false);
    }
  }

  function statusTable(rows, query, setQuery, page, setPage, isMissing) {
    const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
    const safePage = Math.min(page, totalPages);
    const shown = rows.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
    return <section className="panel table-panel" style={{ marginTop: 22 }}>
      <div className="panel-heading"><div>
        <p className="eyebrow">{isMissing ? "ACTION REQUIRED" : "UP TO DATE"}</p>
        <h2>{isMissing ? "Houses to be checked" : "Already checked houses"}</h2>
      </div><span className="record-count">{rows.length} villas</span></div>
      <div className="search-box" style={{ maxWidth: 360, marginBottom: 16 }}>
        <Search size={17}/><input value={query} onChange={(e) => { setQuery(e.target.value); setPage(1); }}
          placeholder="Search villa, customer or area..." aria-label={`Search ${isMissing ? "unchecked" : "checked"} houses`}/>
      </div>
      {shown.length ? <div className="table-scroll"><table><thead><tr>
        <th>{tr("Villa")}</th><th>{tr("Customer")}</th><th>{tr("Area")}</th><th>{tr("Last check")}</th><th>{tr("Next due")}</th><th>{tr("Status")}</th><th>{tr("Action")}</th>
      </tr></thead><tbody>{shown.map((item) => <tr key={item.house_id}>
        <td><strong>{item.house_name}</strong></td><td>{item.customer_name || "—"}</td><td>{item.area || "—"}</td>
        <td>{dateLabel(item[dateField])}</td><td>{dateLabel(item[dueField])}</td>
        <td><span style={{ color: isMissing ? "#b4534b" : "#527b5b", fontWeight: 600 }}>
          {isMissing ? (item[dateField] ? "Overdue" : "Never checked") : "Checked"}
        </span></td>
        <td><button type="button" className="refresh-button" onClick={() => {
          setSelectedHouse(String(item.house_id)); setCheckedAt(nowValue());
          document.getElementById("weekly-record-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
        }}>Record check</button></td>
      </tr>)}</tbody></table></div> : <div className="empty-state">{isMissing ? (!query.trim() ? nextCheckText : "No houses match your search.") : "No houses match your search."}</div>}
      <PaginationControls page={safePage} totalPages={totalPages} totalItems={rows.length} onPageChange={setPage}/>
    </section>;
  }

  return <>
    <div className="welcome-row"><div><p className="eyebrow">{tr("PROPERTY OPERATIONS")}</p><h1>{tr(title)}</h1>
      <p className="muted">Mandatory at least once every 7 days. {isWater ? "A municipal meter reading or tank level is sufficient; both can be recorded." : "Record the villa condition independently from water measurements."}</p>
    </div><div style={{display:"flex",gap:8,flexWrap:"wrap"}}><button type="button" className="refresh-button" onClick={()=>document.getElementById("weekly-record-form")?.scrollIntoView({behavior:"smooth"})}>{"+ " + tr(isWater ? "Add Measurement" : "Add House Check")}</button><button type="button" className="refresh-button" onClick={printProgram}><Download size={16}/> {isWater ? tr("Water Measurement Program") : tr("House Checking Program")}</button></div></div>
    <div className="stats-grid">
      <StatCard label={tr("Total villas")} value={records.length} detail={tr("Managed properties")} icon={Building2}/>
      <StatCard label={tr("Need checking")} value={missing.length} detail={tr("Overdue or never checked")} icon={CircleAlert}/>
      <StatCard label={tr("Already checked")} value={checked.length} detail={tr("Within the last 7 days")} icon={ClipboardCheck}/>
    </div>
    {error && <div className="warning-banner" role="alert"><CircleAlert size={18}/>{error}</div>}
    {notice && <div role="status" aria-live="polite" style={{
      position: "fixed", top: 22, right: 22, zIndex: 9999, maxWidth: 410,
      display: "flex", alignItems: "flex-start", gap: 13,
      padding: "17px 18px", borderRadius: 14,
      border: "1px solid #bfd8c5", background: "#f0f8f1",
      boxShadow: "0 14px 38px rgba(36, 66, 44, 0.17)", color: "#315b3c"
    }}>
      <ClipboardCheck size={23} style={{ flexShrink: 0, marginTop: 2 }}/>
      <div style={{ flex: 1, minWidth: 0 }}>
        <strong style={{ display: "block", fontSize: 15, marginBottom: 4 }}>{tr("Record saved successfully")}</strong>
        <span style={{ fontSize: 12, lineHeight: 1.5 }}>{notice}</span>
      </div>
      <button type="button" aria-label="Dismiss success message" onClick={() => setNotice("")}
        style={{ border: 0, background: "transparent", color: "#527b5b", cursor: "pointer", padding: 2 }}>
        <X size={18}/>
      </button>
    </div>}
    {loading && <p className="muted">{tr("Loading inspection status...")}</p>}
    {statusTable(missingFiltered, needsSearch, setNeedsSearch, missingSafePage, setNeedsPage, true)}
    {statusTable(checkedFiltered, checkedSearch, setCheckedSearch, checkedSafePage, setCheckedPage, false)}
    <section id="weekly-record-form" className="panel" style={{ marginTop: 24, overflow: "hidden" }}>
      <div style={{ padding: "4px 0 20px", borderBottom: "1px solid #e8e5db", marginBottom: 24 }}>
        <p className="eyebrow">PROPERTY OPERATIONS / NEW ENTRY</p>
        <div style={{ display: "flex", alignItems: "center", gap: 13, marginTop: 7 }}>
          <span style={{ display: "grid", placeItems: "center", width: 46, height: 46, borderRadius: 13, background: "#edf2ec", color: "#54745e" }}>
            {isWater ? <Droplets size={23} /> : <ClipboardCheck size={23} />}
          </span>
          <div>
            <h2 style={{ margin: 0, fontSize: 23, color: "#35483b" }}>Record {isWater ? tr("water measurement") : tr("house check")}</h2>
            <p className="muted" style={{ margin: "5px 0 0", fontSize: 13 }}>Complete the details below to update the villa's weekly compliance status.</p>
          </div>
        </div>
      </div>
      <form onSubmit={submit} style={{ display: "grid", gap: 24 }}>
        <div style={{ border: "1px solid #e9e8e0", borderRadius: 15, padding: "22px", background: "#fffefa" }}>
          <div style={{ marginBottom: 19 }}>
            <p className="eyebrow" style={{ marginBottom: 5 }}>01 / PROPERTY & VISIT</p>
            <h3 style={{ margin: 0, fontSize: 17, color: "#3e5143" }}>Visit information</h3>
            <p className="muted" style={{ margin: "5px 0 0", fontSize: 12 }}>Identify the villa, visit time and responsible team member.</p>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: 18 }}>
            <label style={operationLabelStyle}>{tr("Villa")} <span style={{ color: "#b55d53" }}>*</span>
              <select required value={selectedHouse} onChange={(e) => { setSelectedHouse(e.target.value); setForm((prev) => ({ ...prev, tank: "" })); }} style={operationInputStyle}>
                <option value="">{tr("Select a villa")}</option>{villas.map((v) => <option key={v.id} value={v.id}>{v.name}</option>)}
              </select>
            </label>
            <label style={operationLabelStyle}>Inspection date & time <span style={{ color: "#b55d53" }}>*</span>
              <input required type="datetime-local" value={checkedAt} max={nowValue()} onChange={(e) => setCheckedAt(e.target.value)} style={operationInputStyle}/>
            </label>
            <label style={operationLabelStyle}>{tr("Checked by")} <span style={{ color: "#b55d53" }}>*</span>
              <input required value={form.checked_by} onChange={(e) => setForm((p) => ({ ...p, checked_by: e.target.value }))} placeholder="Full name of inspector" style={operationInputStyle}/>
            </label>
          </div>
        </div>
        <div style={{ border: "1px solid #e9e8e0", borderRadius: 15, padding: 22, background: "#fffefa" }}>
          <div style={{ marginBottom: 18 }}>
            <p className="eyebrow" style={{ marginBottom: 5 }}>02 / {isWater ? "MEASUREMENT" : "PROPERTY CONDITION"}</p>
            <h3 style={{ margin: 0, fontSize: 17, color: "#3e5143" }}>{isWater ? "Water measurement details" : "Inspection assessment"}</h3>
            <p className="muted" style={{ margin: "5px 0 0", fontSize: 12 }}>{isWater ? "Choose which water sources were measured during the visit." : "Select the overall property condition observed during the visit."}</p>
          </div>
          {!isWater ? <>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12 }}>
              {[
                { value: "good", label: "Good condition", help: "No issues found", color: "#527b5b", background: "#eef5ee" },
                { value: "attention", label: "Needs attention", help: "Follow-up required", color: "#a37a35", background: "#faf4e7" },
                { value: "urgent", label: "Urgent issue", help: "Immediate action", color: "#ad5751", background: "#fcf0ee" },
              ].map((choice) => <label key={choice.value} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: 16, border: `1.5px solid ${form.condition === choice.value ? choice.color : "#e5e5df"}`, borderRadius: 12, background: form.condition === choice.value ? choice.background : "#ffffff", cursor: "pointer", minHeight: 90 }}>
                <input type="radio" name="house-condition" value={choice.value} checked={form.condition === choice.value} onChange={(e) => setForm((p) => ({ ...p, condition: e.target.value }))} style={{ accentColor: choice.color, marginTop: 3 }}/>
                <span style={{ display: "grid", gap: 6 }}><strong style={{ color: "#3d4c40", fontSize: 13 }}>{choice.label}</strong><span style={{ color: "#788279", fontSize: 12 }}>{choice.help}</span></span>
              </label>)}
            </div>
          </> : <>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12, marginBottom: 20 }}>
              {[
                { value: "municipal", label: "Municipal meter", help: "Record meter litres" },
                { value: "tank", label: "Water tank", help: "Record visual level" },
                { value: "both", label: "Both sources", help: "Complete both readings" },
              ].map((choice) => <label key={choice.value} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: 16, border: `1.5px solid ${form.method === choice.value ? "#718477" : "#e5e5df"}`, borderRadius: 12, background: form.method === choice.value ? "#eef3ed" : "#ffffff", cursor: "pointer", minHeight: 88 }}>
                <input type="radio" name="water-method" value={choice.value} checked={form.method === choice.value} onChange={(e) => setForm((p) => ({ ...p, method: e.target.value }))} style={{ accentColor: "#54745e", marginTop: 3 }}/>
                <span style={{ display: "grid", gap: 6 }}><strong style={{ color: "#3d4c40", fontSize: 13 }}>{choice.label}</strong><span style={{ color: "#788279", fontSize: 12 }}>{choice.help}</span></span>
              </label>)}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: 18 }}>
              {(form.method === "municipal" || form.method === "both") && <label style={operationLabelStyle}>Municipal meter reading (litres) <span style={{ color: "#b55d53" }}>*</span>
                <input type="number" required min="0" step="0.01" value={form.meter_litres} onChange={(e) => setForm((p) => ({ ...p, meter_litres: e.target.value }))} placeholder="e.g. 12500" style={operationInputStyle}/>
                <span style={operationHelpStyle}>Enter the cumulative meter value, not consumption since last visit.</span>
              </label>}
              {(form.method === "tank" || form.method === "both") && <>
                <label style={operationLabelStyle}>Water tank <span style={{ color: "#b55d53" }}>*</span>
                  <select required value={form.tank} onChange={(e) => setForm((p) => ({ ...p, tank: e.target.value }))} style={operationInputStyle}>
                    <option value="">{tr("Select a water tank")}</option>{houseTanks.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                  </select>
                  {!houseTanks.length && <span style={{ ...operationHelpStyle, color: "#ad5751" }}>No tank is configured for this villa. Add one in Django Admin.</span>}
                </label>
                <label style={operationLabelStyle}>Visual tank level <span style={{ color: "#b55d53" }}>*</span>
                  <select value={form.visual_level} onChange={(e) => setForm((p) => ({ ...p, visual_level: e.target.value }))} style={operationInputStyle}>
                    <option value="full">Full (100%)</option><option value="three_quarters">Three quarters (75%)</option><option value="half">Half (50%)</option><option value="quarter">Quarter (25%)</option><option value="nearly_empty">Nearly empty</option><option value="empty">Empty (0%)</option><option value="unknown">Unable to determine</option>
                  </select>
                </label>
              </>}
            </div>
          </>}
        </div>
        <div style={{ border: "1px solid #e9e8e0", borderRadius: 15, padding: 22, background: "#fffefa" }}>
          <p className="eyebrow" style={{ marginBottom: 5 }}>03 / ADDITIONAL INFORMATION</p>
          <h3 style={{ margin: "0 0 16px", fontSize: 17, color: "#3e5143" }}>Notes & observations</h3>
          <label style={operationLabelStyle}>{isWater ? "Water measurement notes" : "Inspection notes"} <span style={{ color: "#8b938c", fontWeight: 400 }}>(optional)</span>
            <textarea value={isWater ? form.water_notes : form.notes} onChange={(e) => setForm((p) => ({ ...p, [isWater ? "water_notes" : "notes"]: e.target.value }))} rows={4} placeholder={isWater ? "Water supply observations, leaks, pressure concerns, or follow-up actions..." : "Describe the condition of the villa, maintenance issues, or recommended follow-up actions..."} style={{ ...operationInputStyle, resize: "vertical", minHeight: 112 }}/>
          </label>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16, flexWrap: "wrap", padding: "18px 20px", background: "#f5f6f0", border: "1px solid #e6e9df", borderRadius: 14 }}>
          <span className="muted" style={{ fontSize: 12 }}>Fields marked <strong style={{ color: "#b55d53" }}>*</strong> are required. Records are saved to your Django database.</span>
          <button type="submit" className="primary-button" disabled={saving} style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 9, minWidth: 175, padding: "12px 20px", borderRadius: 10 }}>
            {saving ? <RefreshCw size={17}/> : <ClipboardCheck size={17}/>} {saving ? "Saving record..." : isWater ? "Save measurement" : "Save house check"}
          </button>
        </div>
      </form>
    </section>
    {isWater && <section className="panel table-panel" style={{ marginTop: 24 }}>
      <div className="panel-heading">
        <div>
          <p className="eyebrow">MEASUREMENT HISTORY</p>
          <h2>Last Water Measurements</h2>
          <p className="muted" style={{ marginTop: 6, fontSize: 13 }}>Municipal meter and tank checks · newest first · 15 per page</p>
        </div>
        <span className="record-count">{historyMatches.length} measurements</span>
      </div>
      <div className="search-box" style={{ maxWidth: 420, marginBottom: 16 }}>
        <Search size={17}/>
        <input value={historySearch} onChange={(e) => { setHistorySearch(e.target.value); setHistoryPage(1); }}
          placeholder="Search villa, source, inspector, reading or notes..." aria-label="Search water measurement history"/>
      </div>
      {historyError && <div className="warning-banner" role="alert"><CircleAlert size={18}/>{historyError}</div>}
      {!historyError && (visibleHistory.length ? <div className="table-scroll"><table>
        <thead><tr><th>{tr("Measurement date")}</th><th>{tr("Villa")}</th><th>{tr("Source")}</th><th>{tr("Reading / level")}</th><th>{tr("Checked by")}</th><th>{tr("Notes")}</th></tr></thead>
        <tbody>{visibleHistory.map((item) => {
          const villaName = villas.find((villa) => String(villa.id) === String(item.house_id))?.name || (item.house_id ? `Villa #${item.house_id}` : "—");
          const dt = new Date(item.date);
          const displayDate = Number.isFinite(dt.getTime()) ? dt.toLocaleString("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : dateLabel(item.date);
          const source = item.source_type === "municipal" ? "Municipal meter" : `Tank · ${item.tank_name}`;
          const reading = item.source_type === "municipal"
            ? `${item.meter_litres ?? "—"} L`
            : ({ full: "Full (100%)", three_quarters: "Three quarters (75%)", half: "Half (50%)", quarter: "Quarter (25%)", nearly_empty: "Nearly empty", empty: "Empty (0%)", unknown: "Unknown" }[item.visual_level] || item.visual_level || "—");
          return <tr key={`${item.source_type}-${item.id}`}>
            <td>{displayDate}</td><td><strong>{villaName}</strong></td><td>{source}</td><td>{reading}</td>
            <td>{item.checked_by || "—"}</td>
            <td style={{ maxWidth: 380, whiteSpace: "normal", overflowWrap: "anywhere" }}>{item.notes || "—"}</td>
          </tr>;
        })}</tbody>
      </table></div> : <div className="empty-state">{loading ? "Loading measurement history..." : historySearch ? "No measurements match your search." : "No water measurements have been recorded yet."}</div>)}
      <PaginationControls page={historySafePage} totalPages={historyPages} totalItems={historyMatches.length} onPageChange={setHistoryPage}/>
    </section>}
    {!isWater && <section className="panel table-panel" style={{ marginTop: 24 }}>
      <div className="panel-heading">
        <div>
          <p className="eyebrow">INSPECTION HISTORY</p>
          <h2>Last House Checks</h2>
          <p className="muted" style={{ marginTop: 6, fontSize: 13 }}>All recorded inspections, newest first · 15 per page</p>
        </div>
        <span className="record-count">{historyMatches.length} checks</span>
      </div>
      <div className="search-box" style={{ maxWidth: 420, marginBottom: 16 }}>
        <Search size={17} />
        <input
          value={historySearch}
          onChange={(e) => { setHistorySearch(e.target.value); setHistoryPage(1); }}
          placeholder="Search villa, inspector, condition or notes..."
          aria-label="Search house check history"
        />
      </div>
      {historyError && <div className="warning-banner" role="alert"><CircleAlert size={18}/>{historyError}</div>}
      {!historyError && (visibleHistory.length ? (
        <div className="table-scroll">
          <table>
            <thead><tr>
              <th>{tr("Inspection date")}</th><th>{tr("Villa")}</th><th>{tr("Checked by")}</th><th>{tr("Condition")}</th><th>{tr("Notes")}</th>
            </tr></thead>
            <tbody>{visibleHistory.map((item) => {
              const villaName = item.house_name || villas.find((villa) => String(villa.id) === String(item.house))?.name || `Villa #${item.house}`;
              const conditionLabel = item.condition_display || ({ good: "Good", attention: "Needs attention", urgent: "Urgent issue" }[item.condition] || item.condition || "—");
              const conditionColor = item.condition === "urgent" ? "#ad5751" : item.condition === "attention" ? "#a37a35" : "#527b5b";
              const inspectionDate = item.inspection_date ? new Date(item.inspection_date) : null;
              const displayDate = inspectionDate && !Number.isNaN(inspectionDate.getTime())
                ? inspectionDate.toLocaleString("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })
                : dateLabel(item.inspection_date);
              return <tr key={item.id}>
                <td>{displayDate}</td>
                <td><strong>{villaName}</strong></td>
                <td>{item.checked_by || "—"}</td>
                <td><span style={{ color: conditionColor, fontWeight: 600 }}>{conditionLabel}</span></td>
                <td style={{ maxWidth: 380, whiteSpace: "normal", overflowWrap: "anywhere" }}>{item.notes || "—"}</td>
              </tr>;
            })}</tbody>
          </table>
        </div>
      ) : <div className="empty-state">{loading ? "Loading inspection history..." : historySearch ? "No inspections match your search." : "No house inspections have been recorded yet."}</div>)}
      <PaginationControls page={historySafePage} totalPages={historyPages} totalItems={historyMatches.length} onPageChange={setHistoryPage}/>
    </section>}
  </>;
}

const JOB_LEVELS = [
  { key: 'overdue', label: 'Overdue', color: '#991b1b', score: 5 },
  { key: 'critical', label: 'Critical', color: '#dc2626', score: 4 },
  { key: 'urgent', label: 'Urgent', color: '#ea580c', score: 3 },
  { key: 'important', label: 'Important', color: '#a16207', score: 2 },
  { key: 'normal', label: 'Normal', color: '#52765b', score: 1 },
];

function ImportantJobsPage({ token, customers }) {
  const [jobs, setJobs] = useState([]);
  const [tab, setTab] = useState('pending');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState(null);
  const [revision, setRevision] = useState(0);
  const endpoint = '/important-job-reminders/';
  const levelFor = (job) => JOB_LEVELS.find(l => l.key === job.importance) || JOB_LEVELS[4];
  async function request(path, options = {}) {
    const url = new URL(path.startsWith('http') ? path : `${API_URL}${path}`);
    if (url.origin !== new URL(API_URL).origin) throw new Error('Unexpected API origin');
    const response = await fetch(url, { ...options, headers: { Authorization: `Bearer ${token}`, ...(options.body ? {'Content-Type':'application/json'} : {}) } });
    const body = await response.json().catch(() => null);
    if (!response.ok) throw new Error(body?.detail || JSON.stringify(body) || `Request failed (${response.status})`);
    return body;
  }
  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true); setError('');
      try {
        let next = `${endpoint}?completed=all`;
        const records = [];
        while (next) {
          const body = await request(next);
          records.push(...getArray(body));
          next = body?.next;
        }
        if (!cancelled) setJobs(records);
      } catch (err) { if (!cancelled) setError(err.message); }
      finally { if (!cancelled) setLoading(false); }
    }
    load();
    const timer = setInterval(() => setRevision(v => v + 1), 300000);
    return () => { cancelled = true; clearInterval(timer); };
  }, [token, revision]);
  const pending = jobs.filter(j => !j.completed);
  const completed = jobs.filter(j => j.completed);
  const chart = JOB_LEVELS.map(l => ({ ...l, value: pending.filter(j => j.importance === l.key).length }));
  const visible = (tab === 'pending' ? pending : completed).filter(j => `${j.customer_name} ${j.description}`.toLowerCase().includes(search.toLowerCase())).sort((a,b) => tab === 'pending' ? levelFor(b).score - levelFor(a).score || a.deadline.localeCompare(b.deadline) || a.id-b.id : String(b.completed_at || '').localeCompare(String(a.completed_at || '')));
  async function mutate(path, body, method='POST') {
    setBusy(true); setError('');
    try {
      const saved = await request(path, { method, ...(body ? {body:JSON.stringify(body)} : {}) });
      setJobs(old => [...old.filter(j => j.id !== saved.id), saved]);
      setEditing(null); setRevision(v => v+1);
    } catch(err) { setError(err.message); }
    finally { setBusy(false); }
  }
  const field = {padding:'10px', border:'1px solid #d9e2d9', borderRadius:8, width:'100%', boxSizing:'border-box'};
  const blank = {customer:'', description:'', deadline:getTodayLocalDate(), procedure_days:1};
  return <>
    <div className="welcome-row"><div><p className="eyebrow">{tr("OPERATIONS / DEADLINES")}</p><h1>{tr("Important Jobs")}</h1><p className="muted">{tr("Plan ahead, track urgency and complete your duties.")}</p></div><div style={{display:'flex',gap:8,flexWrap:'wrap'}}><button className="refresh-button" disabled={loading || busy} onClick={()=>setRevision(v=>v+1)}><RefreshCw size={16}/> {tr("Refresh")}</button><button className="primary-button" disabled={busy} onClick={()=>setEditing({...blank})}>{"+ " + tr("Add Job")}</button></div></div>
    {error && <div className="error-banner" role="alert">{error}</div>}
    <div className="stats-grid"><StatCard label={tr("Pending jobs")} value={pending.length} detail={tr("All open duties")} icon={ClipboardList}/><StatCard label={tr("Critical / overdue")} value={pending.filter(j=>['critical','overdue'].includes(j.importance)).length} detail={tr("Immediate attention")} icon={CircleAlert}/><StatCard label="Email threshold reached" value={pending.filter(j=>j.email_required).length} detail="Within 1.5 × procedure days" icon={Bell}/><StatCard label={tr("Completed")} value={completed.length} detail={tr("Job history")} icon={ClipboardCheck}/></div>
    <section className="panel" style={{marginTop:20}}><div className="panel-heading"><div><p className="eyebrow">PRIORITY DISTRIBUTION</p><h2>Pending workload</h2></div></div>{pending.length ? <div style={{height:240}}><ResponsiveContainer width="100%" height="100%"><BarChart data={chart}><CartesianGrid vertical={false} strokeDasharray="3 3"/><XAxis dataKey="label" tick={{fontSize:11}}/><YAxis allowDecimals={false}/><Tooltip/><Bar dataKey="value" name="Jobs" radius={[6,6,0,0]} maxBarSize={55}>{chart.map(l=><Cell key={l.key} fill={l.color}/>)}</Bar></BarChart></ResponsiveContainer></div> : <p className="muted">No pending jobs to chart.</p>}</section>
    {editing && <form className="panel" style={{marginTop:20}} onSubmit={e=>{e.preventDefault();mutate(editing.id?`${endpoint}${editing.id}/`:endpoint,{customer:editing.customer,description:editing.description,deadline:editing.deadline,procedure_days:Number(editing.procedure_days)},editing.id?'PATCH':'POST');}}><h2>{editing.id?tr("Edit job"):tr("New job")}</h2><div style={{display:'grid',gap:12,gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))'}}><label>{tr("Customer")}<select required style={field} value={editing.customer} onChange={e=>setEditing({...editing,customer:e.target.value})}><option value="">{tr("Select customer")}</option>{customers.map(c=><option key={c.id} value={c.id}>{c.name || c.full_name || `Customer #${c.id}`}</option>)}</select></label><label>{tr("Deadline")}<input required type="date" style={field} value={editing.deadline} onChange={e=>setEditing({...editing,deadline:e.target.value})}/></label><label>{tr("Procedure days")}<input required type="number" min="1" step="1" style={field} value={editing.procedure_days} onChange={e=>setEditing({...editing,procedure_days:e.target.value})}/></label></div><label style={{display:'block',marginTop:12}}>{tr("Description")}<textarea required rows={3} style={field} value={editing.description} onChange={e=>setEditing({...editing,description:e.target.value})}/></label><div style={{display:'flex',gap:8,marginTop:12}}><button className="primary-button" disabled={busy}>{tr("Save job")}</button><button type="button" className="refresh-button" disabled={busy} onClick={()=>setEditing(null)}>{tr("Cancel")}</button></div></form>}
    <section className="panel" style={{marginTop:20}}><div className="panel-heading" style={{flexWrap:'wrap'}}><div><p className="eyebrow">{tr("JOB REGISTER")}</p><h2>{tab==='pending'?tr("Pending duties"):tr("Completed duties")}</h2></div><div style={{display:'flex',gap:8}}>{['pending','completed'].map(t=><button key={t} className={tab===t?'primary-button':'refresh-button'} aria-pressed={tab===t} onClick={()=>setTab(t)}>{t==='pending'?`Pending (${pending.length})`:`Completed (${completed.length})`}</button>)}</div></div><div className="search-box" style={{maxWidth:360,marginBottom:16}}><Search size={17}/><input aria-label="Search jobs" placeholder={tr("Search customer or job...")} value={search} onChange={e=>setSearch(e.target.value)}/></div>
    {loading && <p className="muted">Loading reminders…</p>}{!loading && !error && !visible.length && <div className="empty-state">{tr("No matching jobs.")}</div>}
    <div style={{display:'grid',gap:14}}>{visible.map(j=>{const l=j.completed?{label:'Completed',color:'#64748b'}:levelFor(j); const remaining=Number(j.days_remaining); const duration=Number(j.procedure_days); const pct=Math.max(0,Math.min(100,remaining/(duration*1.5)*100)); return <article key={j.id} style={{border:'1px solid #e4e7df',borderLeft:`5px solid ${l.color}`,borderRadius:12,padding:18,background:'rgba(255,255,255,.65)'}}><div style={{display:'flex',justifyContent:'space-between',gap:12,flexWrap:'wrap'}}><strong style={{fontSize:17,color:'#3f493f'}}>{j.customer_name}</strong><strong style={{color:l.color,fontSize:13}}>{tr(l.label.toUpperCase())}</strong></div><p style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',margin:'10px 0 16px'}}>{j.description}</p><div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(130px,1fr))',gap:12}}>{[['Deadline',dateLabel(j.deadline)],['Procedure',`${duration} days`],['Recommended start',dateLabel(j.recommended_start_date)],['Latest start',dateLabel(j.latest_start_date)],...(j.completed?[['Completed',dateLabel(j.completed_at)]]:[['Time remaining',remaining<0?`${-remaining} days overdue`:`${remaining} days`],['Spare days',j.spare_days]])].map(([label,value])=><div key={label}><div className="muted" style={{fontSize:12}}>{tr(label)}</div><strong>{value}</strong></div>)}</div>{!j.completed && <div style={{marginTop:16}}><div className="muted" style={{fontSize:12,marginBottom:6}}>Time remaining relative to notification window ({duration*1.5} days)</div><div role="progressbar" aria-label="Remaining notification window" aria-valuenow={Math.round(pct)} style={{height:8,background:'#e6e9e2',borderRadius:8,overflow:'hidden'}}><div style={{width:`${pct}%`,height:'100%',background:l.color}}/></div><p className="muted" style={{fontSize:12}}>{j.last_notification_at?`Last email: ${dateLabel(j.last_notification_at)} (${j.last_notification_level})`:j.email_required?'Email threshold reached — awaiting scheduled check':'Email threshold not reached'}</p></div>}<div style={{display:'flex',gap:8,flexWrap:'wrap',marginTop:12}}><button className="refresh-button" disabled={busy} onClick={()=>setEditing({...j})}>{tr("Edit")}</button><button className="primary-button" disabled={busy} onClick={()=>mutate(`${endpoint}${j.id}/${j.completed?'reopen':'complete'}/`)}><ClipboardCheck size={16}/>{j.completed?tr("Reopen job"):tr("Mark completed")}</button></div></article>})}</div></section>
  </>;
}

function CompanyGasPage({ token, employees }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [revision, setRevision] = useState(0);
  const [month, setMonth] = useState('');
  const [employee, setEmployee] = useState('');
  const [fuel, setFuel] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const types = {petrol:'Petrol (Unleaded)', diesel:'Diesel', lpg:'LPG', other:'Other'};
  const colors = ['#718477','#b99b65','#3977b8','#a18b9e'];
  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      setLoading(true); setError(''); setRecords([]);
      try {
        let next = `${API_URL}/company-gas/`;
        const all = [], visited = new Set();
        while (next) {
          const url = new URL(next, `${API_URL}/`);
          if (url.origin !== new URL(API_URL).origin || visited.has(url.href)) throw new Error('Invalid pagination link');
          visited.add(url.href);
          const response = await fetch(url, {headers:{Authorization:`Bearer ${token}`}, signal:controller.signal});
          if (!response.ok) throw new Error(`Company Gas API request failed (${response.status}). Check /api/company-gas/ and your permissions.`);
          const body = await response.json();
          all.push(...getArray(body)); next = body?.next;
        }
        if (!controller.signal.aborted) setRecords(all);
      } catch (err) { if (!controller.signal.aborted) setError(err.message); }
      finally { if (!controller.signal.aborted) setLoading(false); }
    }
    load(); return () => controller.abort();
  }, [token, revision]);
  const rows = records.map(r => {
    const id = relationId(r.employee);
    const e = employees.find(x => String(x.id) === String(id));
    return {...r, employeeId:String(id), employeeLabel:r.employee_name || (e ? [e.first_name,e.last_name].filter(Boolean).join(' ') || e.name : '') || `Employee #${id}`, fuelLabel:types[r.gas_type] || r.gas_type, amount:number(r.price_total)};
  });
  const filtered = rows.filter(r => (!month || r.date?.startsWith(month)) && (!employee || r.employeeId===employee) && (!fuel || r.gas_type===fuel) && [r.employeeLabel,r.department_name,r.notes,r.fuelLabel,r.gas_type,r.date,dateLabel(r.date),r.price_total,money(r.amount)].join(' ').toLowerCase().includes(search.trim().toLowerCase())).sort((a,b)=>String(b.date).localeCompare(String(a.date)) || b.id-a.id);
  const group = (items, key) => {const m = new Map(); items.forEach(r=>m.set(key(r),(m.get(key(r))||0)+r.amount)); return [...m].map(([name,amount])=>({name,amount}));};
  const monthly = group(filtered,r=>r.date?.slice(0,7)||'Unknown').sort((a,b)=>a.name.localeCompare(b.name));
  const byEmployee = group(filtered,r=>`${r.employeeLabel} (#${r.employeeId})`).sort((a,b)=>b.amount-a.amount);
  const byFuel = group(filtered,r=>r.fuelLabel).sort((a,b)=>b.amount-a.amount);
  const total = filtered.reduce((s,r)=>s+r.amount,0);
  const pages = Math.max(1,Math.ceil(filtered.length/pageSize)), safePage=Math.min(page,pages);
  const field={padding:'10px 12px',border:'1px solid #d9e2d9',borderRadius:8,maxWidth:'100%'};
  const chart = (items, horizontal=false) => items.length ? <div style={{height:horizontal?Math.max(220,items.length*42+45):270,width:'100%'}}><ResponsiveContainer width="100%" height="100%"><BarChart data={items} layout={horizontal?'vertical':'horizontal'} margin={{top:10,right:20,left:horizontal?12:0,bottom:12}}><CartesianGrid strokeDasharray="3 3" vertical={horizontal} horizontal={!horizontal}/>{horizontal?<><XAxis type="number" tickFormatter={v=>`€${v}`}/><YAxis type="category" dataKey="name" width={145} tick={{fontSize:11}}/></>:<><XAxis dataKey="name" tick={{fontSize:11}}/><YAxis tickFormatter={v=>`€${v}`}/></>}<Tooltip formatter={v=>money(v)}/><Bar dataKey="amount" name="Fuel expense" fill={horizontal?'#718477':'#b99b65'} maxBarSize={45} radius={horizontal?[0,5,5,0]:[5,5,0,0]}/></BarChart></ResponsiveContainer></div>:<div className="empty-state">No fuel expenses to chart.</div>;
  return <>
    <div className="welcome-row"><div><p className="eyebrow">{tr("COMPANY EXPENSES / FUEL")}</p><h1>{tr("Company Gas")}</h1><p className="muted">{tr("Fuel expenses paid by the company for employees.")}</p></div><AddRecord page="companyGas"/></div>
    {error && <div className="error-message" role="alert">{error}</div>}
    {loading && <p className="muted">Loading fuel records…</p>}
    {!loading && !error && <>
    <section className="panel" style={{marginBottom:20}}><div style={{display:'flex',gap:12,flexWrap:'wrap',alignItems:'end'}}><label>{tr("Month")}<br/><input type="month" style={field} value={month} onChange={e=>{setMonth(e.target.value);setPage(1);}}/></label><label>{tr("Employee")}<br/><select style={field} value={employee} onChange={e=>{setEmployee(e.target.value);setPage(1);}}><option value="">{tr("All employees")}</option>{[...new Map(rows.map(r=>[r.employeeId,r.employeeLabel]))].sort((a,b)=>a[1].localeCompare(b[1])).map(([id,name])=><option key={id} value={id}>{name}</option>)}</select></label><label>{tr("Fuel type")}<br/><select style={field} value={fuel} onChange={e=>{setFuel(e.target.value);setPage(1);}}><option value="">{tr("All fuels")}</option>{Object.entries(types).map(([k,v])=><option key={k} value={k}>{v}</option>)}</select></label><button className="refresh-button" onClick={()=>{setMonth('');setEmployee('');setFuel('');setSearch('');setPage(1);}}>{tr("Clear filters")}</button></div></section>
    <div className="stats-grid"><StatCard label="Total fuel cost" value={money(total)} detail="Selected records" icon={Wallet}/><StatCard label="Fuel purchases" value={filtered.length} detail="Recorded transactions" icon={Truck}/><StatCard label={tr("Employees")} value={new Set(filtered.map(r=>r.employeeId)).size} detail="With fuel expenses" icon={Users}/><StatCard label="Average purchase" value={money(filtered.length?total/filtered.length:0)} detail="Cost per transaction" icon={CreditCard}/></div>
    <section className="panel" style={{marginTop:20}}><div className="panel-heading"><div><p className="eyebrow">MONTHLY TREND</p><h2>Fuel expenses by month</h2></div></div>{chart(monthly)}</section>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(min(100%,340px),1fr))',gap:18,marginTop:20}}><section className="panel" style={{minWidth:0}}><h2>Cost by employee</h2>{chart(byEmployee,true)}</section><section className="panel" style={{minWidth:0}}><h2>Fuel type distribution</h2>{total>0?<div style={{height:300}}><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={byFuel} dataKey="amount" nameKey="name" innerRadius="45%" outerRadius="75%" label={({percent})=>`${Math.round(percent*100)}%`}>{byFuel.map((r,i)=><Cell key={r.name} fill={colors[i%colors.length]}/>)}</Pie><Tooltip formatter={v=>money(v)}/><Legend/></PieChart></ResponsiveContainer></div>:<div className="empty-state">No positive expenses to chart.</div>}</section></div>
    <div style={{marginTop:20}}>
      <DataTable title="Fuel expense records"
        rows={filtered.slice((safePage-1)*pageSize,safePage*pageSize)}
        totalCount={filtered.length}
        searchValue={search}
        onSearchChange={v=>{setSearch(v);setPage(1);}}
        searchPlaceholder="Search employee, department, fuel, amount, date..."
        emptyMessage="No matching fuel expenses."
        headerActions={<label style={{display:'flex',alignItems:'center',gap:8}}>{tr("Rows per page")} <select style={field} value={pageSize} onChange={e=>{setPageSize(Number(e.target.value));setPage(1);}}>{[10,25,50,100].map(n=><option key={n} value={n}>{n}</option>)}</select></label>}
        columns={[
          {label:'Date',render:r=>dateLabel(r.date)},
          {label:'Employee',key:'employeeLabel'},
          {label:'Department',key:'department_name'},
          {label:'Fuel',key:'fuelLabel'},
          {label:'Amount',render:r=>money(r.amount)},
          {label:'Notes',key:'notes'},
          {label:'Invoice',render:r=>{
            if (!r.invoice_pdf) return '—';
            let url;
            try { url = new URL(r.invoice_pdf, new URL(API_URL, window.location.origin).origin + '/'); }
            catch { return 'Invalid invoice link'; }
            if (!['http:','https:'].includes(url.protocol)) return 'Invalid invoice link';
            return <a className="refresh-button" style={{display:'inline-flex',alignItems:'center',gap:6,textDecoration:'none',whiteSpace:'nowrap'}} href={url.href} target="_blank" rel="noopener noreferrer">{tr("Open PDF ↗")}</a>;
          }}
        ]}/>
      <div style={{padding:'12px 4px',display:'flex',justifyContent:'space-between',flexWrap:'wrap',gap:8}}>
        <span className="muted">Showing {filtered.length ? (safePage-1)*pageSize+1 : 0}–{Math.min(safePage*pageSize,filtered.length)} of {filtered.length} records</span>
        <strong>Matching expenses: {money(total)}</strong>
      </div>
      <PaginationControls page={safePage} totalPages={pages} totalItems={filtered.length} onPageChange={setPage}/>
    </div>
    </>}
  </>;
}

export default function App() {
  const [language, setLanguage] = useState(() => localStorage.getItem("pk_language") === "el" ? "el" : "en");
  uiLanguage = language;
  useEffect(() => { document.documentElement.lang = language; localStorage.setItem("pk_language", language); }, [language]);
  const [token, setToken] = useState(
    () => localStorage.getItem("pk_access_token")
  );

  const [activePage, setActivePage] = useState("overview");
  const [data, setData] = useState(emptyData);
  const [loading, setLoading] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [error, setError] = useState("");
  const [endpointErrors, setEndpointErrors] = useState([]);
  const [search, setSearch] = useState("");
  const [recentWorkSearch, setRecentWorkSearch] = useState("");
  const [recentWorkPage, setRecentWorkPage] = useState(1);
  const [recentWorkSort, setRecentWorkSort] = useState("created_at");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [overviewExporting, setOverviewExporting] = useState(false);

  // Controls which chart is displayed.
  const [chartView, setChartView] = useState("monthly");

  // Independent search and pagination for the Villas page.
  const [villaTableSearch, setVillaTableSearch] = useState("");
  const [villaTablePage, setVillaTablePage] = useState(1);
  const [villaChartSearch, setVillaChartSearch] = useState("");
  const [villaChartPage, setVillaChartPage] = useState(1);

  // Independent search and pagination for the Departments page.
  const [departmentTableSearch, setDepartmentTableSearch] = useState("");
  const [departmentTablePage, setDepartmentTablePage] = useState(1);
  const [departmentChartSearch, setDepartmentChartSearch] = useState("");
  const [departmentChartPage, setDepartmentChartPage] = useState(1);
  const [villaChartDisplay, setVillaChartDisplay] = useState("bar");
  const [departmentChartDisplay, setDepartmentChartDisplay] = useState("bar");

  const VILLA_TABLE_PAGE_SIZE = 10;
  const VILLA_CHART_PAGE_SIZE = 9;
  const DEPARTMENT_TABLE_PAGE_SIZE = 10;
  const DEPARTMENT_CHART_PAGE_SIZE = 9;
  const RECENT_WORK_PAGE_SIZE = 10;

  async function apiRequest(path, options = {}, accessToken = token) {
    const requestUrl = /^https?:\/\//i.test(path) ? path : `${API_URL}${path}`;
    const response = await fetch(requestUrl, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(accessToken
          ? { Authorization: `Bearer ${accessToken}` }
          : {}),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));

      const detail = body.detail || body.message ||
        Object.values(body).flat().filter(Boolean).join(" ") ||
        `Request failed (${response.status})`;

      throw new Error(detail);
    }

    if (response.status === 204) return null;

    return response.json();
  }

  // Django REST Framework may return only 25 work entries per page.
  // Follow every `next` link so dashboard totals and tables use all records.
  async function apiRequestAllPages(path) {
    let payload = await apiRequest(path);

    if (Array.isArray(payload)) return payload;

    const allRecords = [...getArray(payload)];
    let nextPage = payload?.next;

    while (nextPage) {
      payload = await apiRequest(nextPage);
      allRecords.push(...getArray(payload));
      nextPage = payload?.next;
    }

    return allRecords;
  }

  async function login(username, password) {
    setLoginLoading(true);
    setError("");

    try {
      const result = await apiRequest(
        "/auth/login/",
        {
          method: "POST",
          body: JSON.stringify({ username, password }),
        },
        null
      );

      const access = result.access || result.access_token;

      if (!access) {
        throw new Error(
          "Login succeeded, but the API did not return an access token. Check your JWT login response."
        );
      }

      localStorage.setItem("pk_access_token", access);

      if (result.refresh) {
        localStorage.setItem("pk_refresh_token", result.refresh);
      }

      setToken(access);
    } catch (err) {
      setError(
        err.message || "Could not sign in. Check your Django login endpoint."
      );
    } finally {
      setLoginLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem("pk_access_token");
    localStorage.removeItem("pk_refresh_token");

    setToken(null);
    setData(emptyData);
    setEndpointErrors([]);
  }

  async function exportBusinessOverview() {
    if (!token || overviewExporting) return;
    setOverviewExporting(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/business-export/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || body.message || `Export failed (${response.status})`);
      }
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = `Business_Overview_${getTodayLocalDate()}.zip`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(objectUrl), 30000);
    } catch (err) {
      setError(err.message || "Unable to export business overview.");
    } finally {
      setOverviewExporting(false);
    }
  }

  async function loadDashboard() {
    if (!token) return;

    setLoading(true);
    setError("");

    const keys = Object.keys(ENDPOINTS);

    const results = await Promise.allSettled(
      keys.map((key) =>
        apiRequestAllPages(ENDPOINTS[key])
      )
    );

    const nextData = { ...emptyData };
    const failures = [];

    results.forEach((result, index) => {
      const key = keys[index];

      if (result.status === "fulfilled") {
        nextData[key] = getArray(result.value);
      } else {
        failures.push({
          key,
          message: result.reason?.message || "Could not load this section",
        });
      }
    });

    const unauthorized = failures.some((item) =>
      /401|403|token|authentication|credentials/i.test(item.message)
    );

    if (unauthorized) {
      setLoading(false);
      setError("Your session may have expired. Please sign in again.");
      logout();
      return;
    }

    setData(nextData);
    setEndpointErrors(failures);
    setLoading(false);
  }

  useEffect(() => {
    if (token) loadDashboard();

    // loadDashboard is intentionally triggered when the login token changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  // Financial calculations.
  const totals = useMemo(() => {
    const workRevenue = data.workEntries.reduce(
      (sum, item) => sum + number(item.customer_charge),
      0
    );

    // Count only programs active on the current local date.
    // The Django API field is "price", not "monthly_price".
    const today = getTodayLocalDate();

    const activePrograms = data.programs.filter((item) => {
      const started = !item.start_date || item.start_date <= today;
      const notEnded = !item.end_date || item.end_date >= today;

      return started && notEnded;
    });

    const programRevenue = activePrograms.reduce(
      (sum, item) => sum + number(item.price),
      0
    );

    const employeeCosts = data.workEntries.reduce(
      (sum, item) => sum + number(item.employee_cost),
      0
    );

    const invoiceCosts = data.invoices.filter((invoice) => isCompanyInvoice(invoice, data.villas)).reduce(
      (sum, item) => sum + number(item.amount),
      0
    );

    return {
      workRevenue,
      programRevenue,
      revenue: workRevenue + programRevenue,
      employeeCosts,
      grossProfit: workRevenue + programRevenue - employeeCosts - invoiceCosts,
      costs: employeeCosts + invoiceCosts,
      margin: workRevenue + programRevenue - employeeCosts - invoiceCosts,
    };
  }, [data]);

  const departmentChartData = useMemo(
    () =>
      buildDepartmentChart(
        data.workEntries,
        data.services,
        data.departments
      ),
    [data.workEntries, data.services, data.departments]
  );

  // Villa financial chart data.
  const villaChartData = useMemo(
    () =>
      buildVillaChart(
        data.villas,
        data.workEntries,
        data.programs,
        data.invoices
      ),
    [data.villas, data.workEntries, data.programs, data.invoices]
  );

  const villaPerformanceData = useMemo(
    () => villaChartData,
    [villaChartData]
  );

  const departmentPerformanceData = useMemo(
    () => buildDepartmentPerformance(data.departments, data.services, data.workEntries),
    [data.departments, data.services, data.workEntries]
  );

  const filteredVillaTable = useMemo(() => {
    const term = villaTableSearch.trim().toLowerCase();
    if (!term) return villaPerformanceData;

    return villaPerformanceData.filter((villa) =>
      [villa.villa, villa.area].join(" ").toLowerCase().includes(term)
    );
  }, [villaPerformanceData, villaTableSearch]);

  const filteredVillaCharts = useMemo(() => {
    const term = villaChartSearch.trim().toLowerCase();
    if (!term) return villaPerformanceData;

    return villaPerformanceData.filter((villa) =>
      villa.villa.toLowerCase().includes(term)
    );
  }, [villaPerformanceData, villaChartSearch]);

  const villaTableTotalPages = Math.max(
    1,
    Math.ceil(filteredVillaTable.length / VILLA_TABLE_PAGE_SIZE)
  );
  const villaChartTotalPages = Math.max(
    1,
    Math.ceil(filteredVillaCharts.length / VILLA_CHART_PAGE_SIZE)
  );

  const paginatedVillaTable = filteredVillaTable.slice(
    (villaTablePage - 1) * VILLA_TABLE_PAGE_SIZE,
    villaTablePage * VILLA_TABLE_PAGE_SIZE
  );

  const paginatedVillaCharts = filteredVillaCharts.slice(
    (villaChartPage - 1) * VILLA_CHART_PAGE_SIZE,
    villaChartPage * VILLA_CHART_PAGE_SIZE
  );

  const filteredDepartmentTable = useMemo(() => {
    const term = departmentTableSearch.trim().toLowerCase();
    if (!term) return departmentPerformanceData;

    return departmentPerformanceData.filter((department) =>
      [department.department, department.description]
        .join(" ")
        .toLowerCase()
        .includes(term)
    );
  }, [departmentPerformanceData, departmentTableSearch]);

  const filteredDepartmentCharts = useMemo(() => {
    const term = departmentChartSearch.trim().toLowerCase();
    if (!term) return departmentPerformanceData;

    return departmentPerformanceData.filter((department) =>
      department.department.toLowerCase().includes(term)
    );
  }, [departmentPerformanceData, departmentChartSearch]);

  const departmentTableTotalPages = Math.max(
    1,
    Math.ceil(filteredDepartmentTable.length / DEPARTMENT_TABLE_PAGE_SIZE)
  );
  const departmentChartTotalPages = Math.max(
    1,
    Math.ceil(filteredDepartmentCharts.length / DEPARTMENT_CHART_PAGE_SIZE)
  );

  const paginatedDepartmentTable = filteredDepartmentTable.slice(
    (departmentTablePage - 1) * DEPARTMENT_TABLE_PAGE_SIZE,
    departmentTablePage * DEPARTMENT_TABLE_PAGE_SIZE
  );
  const paginatedDepartmentCharts = filteredDepartmentCharts.slice(
    (departmentChartPage - 1) * DEPARTMENT_CHART_PAGE_SIZE,
    departmentChartPage * DEPARTMENT_CHART_PAGE_SIZE
  );


  const servicePerformanceData = useMemo(
    () => buildServicePerformance(data.services, data.workEntries, data.departments),
    [data.services, data.workEntries, data.departments]
  );

  const employeePerformanceData = useMemo(
    () => buildEmployeePerformance(data.employees, data.workEntries, data.departments),
    [data.employees, data.workEntries, data.departments]
  );

  const filteredWork = useMemo(() => {
    const term = search.trim().toLowerCase();

    if (!term) return data.workEntries;

    return data.workEntries.filter((entry) =>
      [
        getVillaName(entry, data.villas),
        getEmployeeName(entry),
        entry.department_name,
        dateLabel(entry.work_date),
        entry.work_date,
      ].join(" ").toLowerCase().includes(term)
    );
  }, [data.workEntries, data.villas, data.services, search]);

  const filteredRecentWork = useMemo(() => {
    const term = recentWorkSearch.trim().toLowerCase();
    const matching = data.workEntries.filter((entry) => {
      if (!term) return true;
      return [
        getVillaName(entry, data.villas),
        getEmployeeName(entry),
        getServiceName(entry, data.services),
        entry.description,
        entry.work_date,
        entry.created_at,
      ].join(" ").toLowerCase().includes(term);
    });

    return matching.sort((a, b) => {
      if (recentWorkSort === "work_date") {
        const workDateDifference =
          new Date(b.work_date || 0).getTime() - new Date(a.work_date || 0).getTime();
        if (workDateDifference !== 0) return workDateDifference;
      }
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    });
  }, [data.workEntries, data.villas, data.services, recentWorkSearch, recentWorkSort]);

  const recentWorkTotalPages = Math.max(
    1,
    Math.ceil(filteredRecentWork.length / RECENT_WORK_PAGE_SIZE)
  );
  const safeRecentWorkPage = Math.min(recentWorkPage, recentWorkTotalPages);
  const paginatedRecentWork = filteredRecentWork.slice(
    (safeRecentWorkPage - 1) * RECENT_WORK_PAGE_SIZE,
    safeRecentWorkPage * RECENT_WORK_PAGE_SIZE
  );

  const pageInfo = {
    villas: {
      title: "Villas",
      subtitle: "Properties registered in your database",
      rows: data.villas,
      columns: [
        { label: "Villa", key: "name" },
        { label: "Customer", render: (r) => getRelatedName(r.customer) },
        { label: "Area", key: "area" },
        { label: "Created", render: (r) => dateLabel(r.created_at) },
      ],
    },

    customers: {
      title: "Customers",
      subtitle: "Customer details from Django",
      rows: data.customers,
      columns: [
        { label: "Name", key: "name" },
        { label: "Company", key: "company_name" },
        { label: "Email", key: "email" },
        { label: "Phone", key: "phone" },
      ],
    },

    customerPayments: {
      title: "Customer Payments",
      subtitle: "Read-only payments recorded in Django Admin",
      rows: data.customerPayments,
      columns: [
        { label: "Date", render: (r) => dateLabel(r.payment_date) },
        { label: "Customer", render: (r) => resolveName(r.customer, data.customers, r.customer_name) },
        { label: "Amount", render: (r) => money(r.amount) },
        { label: "Reference", key: "reference" },
        { label: "Notes", key: "notes" },
      ],
    },
    suppliers: {
      title: "Suppliers",
      subtitle: "Supplier invoice costs, payments and outstanding balances",
      rows: data.suppliers,
      columns: [
        { label: "Supplier", key: "name" },
        { label: "Tax number", key: "tax_number" },
        { label: "Phone", key: "phone" },
        { label: "Email", key: "email" },
      ],
    },
    supplierPayments: {
      title: "Supplier Payments",
      subtitle: "Read-only supplier payments recorded in Django Admin",
      rows: data.supplierPayments,
      columns: [
        { label: "Date", render: (r) => dateLabel(r.payment_date) },
        { label: "Supplier", render: (r) => resolveName(r.supplier, data.suppliers, r.supplier_name) },
        { label: "Amount", render: (r) => money(r.amount) },
        { label: "Reference", key: "reference" },
        { label: "Notes", key: "notes" },
      ],
    },
    employees: {
      title: "Employees",
      subtitle: "Your employee records",
      rows: data.employees,
      columns: [
        {
          label: "Employee",
          render: (r) =>
            [r.first_name, r.last_name].filter(Boolean).join(" ") ||
            r.name || "—"
        },
        { label: "Department", render: (r) => getRelatedName(r.department) },
        { label: "Salary type", key: "salary_type" },
        {
          label: "Status",
          render: (r) => r.is_active ? "Active" : "Inactive"
        },
      ],
    },

    departments: {
      title: "Departments",
      subtitle: "Departments registered in your database",
      rows: data.departments,
      columns: [
        { label: "Department", key: "name" },
        { label: "Description", key: "description" },
      ],
    },

    services: {
      title: "Services",
      subtitle: "Services registered in your database",
      rows: data.services,
      columns: [
        { label: "Service", key: "name" },
        { label: "Department", render: (r) => getRelatedName(r.department) },
        { label: "Description", key: "description" },
      ],
    },

    workEntries: {
      title: "Work Entries",
      subtitle: "Recorded work and charges from Django",
      rows: filteredWork,
      columns: [
        { label: "Date", render: (r) => dateLabel(r.work_date) },
        { label: "Villa", render: (r) => getVillaName(r, data.villas) },
        { label: "Employee", render: (r) => getEmployeeName(r) },
        { label: "Department", render: (r) => r.department_name || "—" },
        { label: "Service", render: (r) => getServiceName(r, data.services) },
        { label: "Hours", key: "hours" },
        {
          label: "Customer charge",
          render: (r) => money(r.customer_charge)
        },
      ],
    },

    programs: {
      title: "Programs",
      subtitle: "Villa programs and their monthly prices",
      rows: data.programs,
      columns: [
        { label: "Villa", render: (r) => getVillaName(r, data.villas) },
        { label: "Program", key: "program_type" },
        { label: "Monthly price", render: (r) => money(r.price) },
        { label: "Start date", render: (r) => dateLabel(r.start_date) },
        { label: "End date", render: (r) => dateLabel(r.end_date) },
      ],
    },

    invoices: {
      title: "Invoices",
      subtitle: "Supplier invoices from your database",
      rows: data.invoices,
      columns: [
        { label: "Invoice", key: "invoice_number" },
        { label: "Supplier", key: "supplier" },
        { label: "Department", render: (r) => getRelatedName(r.department) },
        { label: "Date", render: (r) => dateLabel(r.invoice_date) },
        { label: "Amount", render: (r) => money(r.amount) },
      ],
    },
  };

  if (!token) {
    return (
      <LoginScreen
        onLogin={login}
        loading={loginLoading}
        error={error}
      />
    );
  }

  const currentPage = activePage === "companyGas" ? { title: "Company Gas" } : activePage === "houseChecks"
    ? { title: "House Checks" }
    : activePage === "waterMeasurements"
      ? { title: "Water Measurements" }
      : pageInfo[activePage];

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          className="mobile-overlay"
          aria-label="Close menu"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">PK</div>

          <div>
            <div className="brand-name">PAROS KATOIKIA</div>
            <div className="brand-caption">VILLA MANAGEMENT</div>
          </div>

          <button
            className="close-sidebar"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        <div className="nav-caption">WORKSPACE</div>

        <nav className="side-nav">
          {navigation.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`nav-item ${activePage === id ? "active" : ""}`}
              onClick={() => {
                setActivePage(id);
                setSidebarOpen(false);
              }}
            >
              <Icon size={18} strokeWidth={1.7} />
              <span>{tr(label)}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="connection-status">
            <span className="status-dot" />
            {tr("Django API connected")}
          </div>

          <button className="nav-item" onClick={logout}>
            <LogOut size={18} />
            <span>{tr("Sign out")}</span>
          </button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setSidebarOpen(true)}
            aria-label={tr("Open menu")}
          >
            <Menu />
          </button>

          <div className="topbar-title">
            Paros <span>/</span>{" "}
            {tr(navigation.find(item => item.id === activePage)?.label || "Overview")}
          </div>

          <div className="topbar-actions">
            <button type="button" className="icon-button" title={language === "el" ? "English" : "Ελληνικά"} aria-label={language === "el" ? "English" : "Ελληνικά"} onClick={() => setLanguage(v => v === "el" ? "en" : "el")}>{language === "el" ? "🇬🇧 EN" : "🇬🇷 EL"}</button>
            {activePage !== "workEntries" && <div className="search-box">
              <Search size={17} />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={tr("Search work entries...")}
              />
            </div>}

            <button
              className="icon-button"
              onClick={loadDashboard}
              title="Refresh data"
            >
              <RefreshCw size={18} />
            </button>

            <div className="date-label">
              {new Date().toLocaleDateString("en-GB", {
                day: "2-digit",
                month: "short",
                year: "numeric"
              })}
            </div>
          </div>
        </header>

        <div className="page-content">
          {error && (
            <div className="error-banner">
              <CircleAlert size={18} />
              {error}
            </div>
          )}

          {endpointErrors.length > 0 && (
            <div className="warning-banner">
              <CircleAlert size={18} />

              <div>
                <strong>Some API sections could not be loaded.</strong>

                {endpointErrors.map((item) => (
                  <div key={item.key}>
                    {ENDPOINTS[item.key]} — {item.message}
                  </div>
                ))}
              </div>
            </div>
          )}

          {loading && (
            <div className="loading-line">
              <RefreshCw size={16} className="spin" />
              Loading records from Django...
            </div>
          )}

          {activePage === "companyGas" ? (
            <CompanyGasPage token={token} employees={data.employees} />
          ) : activePage === "importantJobs" ? (
            <ImportantJobsPage token={token} customers={data.customers} />
          ) : activePage === "houseChecks" || activePage === "waterMeasurements" ? (
            <WeeklyOperationsPage
              kind={activePage === "waterMeasurements" ? "water" : "house"}
              token={token}
              villas={data.villas}
            />
          ) : activePage === "invoices" ? (
            <InvoiceAnalytics data={data} onRefresh={loadDashboard} />
          ) : activePage === "customerPayments" || activePage === "supplierPayments" ? (
            <PaymentsAnalytics
              kind={activePage === "supplierPayments" ? "supplier" : "customer"}
              data={data}
              onRefresh={loadDashboard}
            />
          ) : activePage === "suppliers" || activePage === "customers" ? (
            <AccountAnalytics
              token={token}
              kind={activePage === "suppliers" ? "supplier" : "customer"}
              data={data}
              onRefresh={loadDashboard}
            />
          ) : activePage === "overview" ? (
            <>
              <div className="welcome-row">
                <div>
                  <p className="eyebrow">{tr("PROPERTY OPERATIONS")}</p>
                  <h1>{tr("Data Analytics")} </h1>
                  <p className="muted">
                    Your villa management overview, bringing together operations, services and financial performance — all powered by your business data.
                  </p>
                </div>

                <button className="refresh-button" type="button" onClick={exportBusinessOverview} disabled={overviewExporting}>
                  <Download size={16} />
                  {overviewExporting ? "Preparing business ZIP…" : "Export data ZIP"}
                </button>
              </div>

              <div className="stats-grid">
                <StatCard
                  label={tr("Registered Villas")}
                  value={data.villas.length}
                  detail="Villas in your database"
                  icon={Building2}
                />

                <StatCard
                  label={tr("Customers")}
                  value={data.customers.length}
                  detail="Registered customers"
                  icon={Users}
                />

                <StatCard
                  label={tr("Employees")}
                  value={data.employees.length}
                  detail="Employee records"
                  icon={UserRound}
                />

                <StatCard
                  label={tr("Work Entries")}
                  value={data.workEntries.length}
                  detail="Recorded work entries"
                  icon={ClipboardList}
                />
              </div>

              <div className="stats-grid financial-stats">
                <StatCard
                  label="Work Revenue"
                  value={money(totals.workRevenue)}
                  detail="Sum of recorded customer charges"
                  icon={ChartNoAxesCombined}
                />

                <StatCard
                  label="Program Revenue"
                  value={money(totals.programRevenue)}
                  detail="Monthly prices of currently active programs"
                  icon={Sprout}
                />

                <StatCard
                  label="Recorded Costs"
                  value={money(totals.costs)}
                  detail="Employee work costs + company invoices"
                  icon={FileText}
                />

                <StatCard
                  label="Calculated Margin"
                  value={money(totals.margin)}
                  detail="Revenue minus recorded costs"
                  icon={BriefcaseBusiness}
                />
              </div>

              <div className="content-grid">
                <section className="panel chart-panel">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">
                        {chartView === "monthly"
                          ? "TOTAL FINANCIAL PERFORMANCE"
                          : chartView === "department"
                            ? "DEPARTMENT PERFORMANCE"
                            : "VILLA FINANCIAL PERFORMANCE"}
                      </p>

                      <h2>
                        {chartView === "monthly"
                          ? "Total revenue & gross profit"
                          : chartView === "department"
                            ? "Revenue & gross margin by department"
                            : "Income, expenses & net profit by villa"}
                      </h2>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        flexWrap: "wrap",
                      }}
                    >
<button
                        type="button"
                        onClick={() => setChartView("monthly")}
                        style={{
                          padding: "7px 10px",
                          borderRadius: "7px",
                          border: chartView === "monthly"
                            ? "1px solid #718477"
                            : "1px solid #e5dfd4",
                          background: chartView === "monthly"
                            ? "#718477"
                            : "transparent",
                          color: chartView === "monthly"
                            ? "#ffffff"
                            : "inherit",
                          cursor: "pointer",
                          fontSize: "11px",
                          whiteSpace: "nowrap",
                        }}
                      >
                        Totals
                      </button>

                      <button
                        type="button"
                        onClick={() => setChartView("department")}
                        style={{
                          padding: "7px 10px",
                          borderRadius: "7px",
                          border: chartView === "department"
                            ? "1px solid #718477"
                            : "1px solid #e5dfd4",
                          background: chartView === "department"
                            ? "#718477"
                            : "transparent",
                          color: chartView === "department"
                            ? "#ffffff"
                            : "inherit",
                          cursor: "pointer",
                          fontSize: "11px",
                          whiteSpace: "nowrap",
                        }}
                      >
                        By department
                      </button>

                      <button
                        type="button"
                        onClick={() => setChartView("villa")}
                        style={{
                          padding: "7px 10px",
                          borderRadius: "7px",
                          border: chartView === "villa"
                            ? "1px solid #718477"
                            : "1px solid #e5dfd4",
                          background: chartView === "villa"
                            ? "#718477"
                            : "transparent",
                          color: chartView === "villa"
                            ? "#ffffff"
                            : "inherit",
                          cursor: "pointer",
                          fontSize: "11px",
                          whiteSpace: "nowrap",
                        }}
                      >
                        By villas
                      </button>
                    </div>
                  </div>

                  {chartView === "monthly" ? (
                    <div className="chart-wrap" style={{ position: "relative" }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={[
                              { name: "Gross profit", value: Math.max(0, totals.grossProfit) },
                              { name: "Company costs", value: Math.max(0, totals.costs) },
                            ]}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            innerRadius="58%"
                            outerRadius="82%"
                            paddingAngle={3}
                            stroke="none"
                          >
                            <Cell fill="#3977b8" />
                            <Cell fill="#c85b55" />
                          </Pie>
                          <Tooltip formatter={(value) => money(value)} />
                          <Legend
                            verticalAlign="bottom"
                            height={30}
                            formatter={(value) => (
                              <span style={{ color: "#77736b", fontSize: 12 }}>{value}</span>
                            )}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                      <div
                        style={{
                          position: "absolute",
                          top: "43%",
                          left: "50%",
                          transform: "translate(-50%, -50%)",
                          textAlign: "center",
                          pointerEvents: "none",
                          width: "42%",
                        }}
                      >
                        <div style={{ color: "#8b887f", fontSize: 11, marginBottom: 4 }}>
                          Total revenue
                        </div>
                        <div style={{ color: "#343b35", fontSize: 19, fontWeight: 600 }}>
                          {money(totals.revenue)}
                        </div>
                      </div>
                    </div>
                  ) : chartView === "department" ? (
                    departmentChartData.length === 0 ? (
                      <div className="empty-state chart-empty">
                        No department work entries are available to chart yet.
                      </div>
                    ) : (
                      <div className="chart-wrap">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={departmentChartData}
                            margin={{ top: 12, right: 12, left: 0, bottom: 0 }}
                            barGap={6}
                          >
                            <CartesianGrid
                              strokeDasharray="3 3"
                              vertical={false}
                              stroke="#eee9df"
                            />

                            <XAxis
                              dataKey="department"
                              tick={{ fill: "#8b887f", fontSize: 11 }}
                              axisLine={false}
                              tickLine={false}
                            />

                            <YAxis
                              tick={{ fill: "#8b887f", fontSize: 11 }}
                              axisLine={false}
                              tickLine={false}
                            />

                            <Tooltip formatter={(value) => money(value)} />
                            <Legend />

                            <Bar
                              dataKey="revenue"
                              name="Total revenue"
                              fill="#b99b65"
                              radius={[4, 4, 0, 0]}
                              maxBarSize={36}
                            />

                            <Bar
                              dataKey="grossMargin"
                              name={tr("Gross margin")}
                              fill="#718477"
                              radius={[4, 4, 0, 0]}
                              maxBarSize={36}
                            />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )
                  ) : villaChartData.length === 0 ? (
                    <div className="empty-state chart-empty">
                      No villas are available to chart yet.
                    </div>
                  ) : (
                    <div className="chart-wrap">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={villaChartData}
                          margin={{ top: 12, right: 12, left: 0, bottom: 0 }}
                          barGap={5}
                        >
                          <CartesianGrid
                            strokeDasharray="3 3"
                            vertical={false}
                            stroke="#eee9df"
                          />

                          <XAxis
                            dataKey="villa"
                            tick={{ fill: "#8b887f", fontSize: 11 }}
                            axisLine={false}
                            tickLine={false}
                          />

                          <YAxis
                            tick={{ fill: "#8b887f", fontSize: 11 }}
                            axisLine={false}
                            tickLine={false}
                          />

                          <Tooltip formatter={(value) => money(value)} />
                          <Legend />

                          <Bar
                            dataKey="income"
                            name={tr("Revenue")}
                            fill="#b99b65"
                            radius={[4, 4, 0, 0]}
                            maxBarSize={36}
                          />

                          <Bar
                            dataKey="outcome"
                            name={tr("Expenses")}
                            fill="#718477"
                            radius={[4, 4, 0, 0]}
                            maxBarSize={36}
                          />

                          <Bar
                            dataKey="reimbursableInvoices"
                            name={tr("Reimbursable invoices")}
                            fill="#b0a5c2"
                            radius={[4, 4, 0, 0]}
                            maxBarSize={36}
                          />

                          <Bar
                            dataKey="netResult"
                            name={tr("Gross margin")}
                            fill="#9b8a78"
                            radius={[4, 4, 0, 0]}
                            maxBarSize={36}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </section>

                <section className="panel breakdown-panel">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">DATABASE SUMMARY</p>
                      <h2>Business records</h2>
                    </div>
                  </div>

                  {[
                    ["Departments", data.departments.length],
                    ["Services", data.services.length],
                    ["Villa programs", data.programs.length],
                    ["Invoices", data.invoices.length],
                  ].map(([label, value]) => (
                    <div className="breakdown-row" key={label}>
                      <span>{tr(label)}</span>
                      <strong>{value}</strong>
                    </div>
                  ))}

                  <div className="breakdown-note">
                    Figures above are loaded from your Django API.
                  </div>
                </section>
              </div>

              <DataTable
                title="Recent work entries"
                rows={paginatedRecentWork}
                totalCount={filteredRecentWork.length}
                searchValue={recentWorkSearch}
                searchPlaceholder={tr("Search work entries...")}
                onSearchChange={(value) => {
                  setRecentWorkSearch(value);
                  setRecentWorkPage(1);
                }}
                headerActions={(
                  <button
                    type="button"
                    className="refresh-button"
                    onClick={() => {
                      setRecentWorkSort((current) =>
                        current === "created_at" ? "work_date" : "created_at"
                      );
                      setRecentWorkPage(1);
                    }}
                    title="Switch the date used to sort work entries"
                    style={{ padding: "8px 11px", fontSize: "12px" }}
                  >
                    Sort: {recentWorkSort === "created_at" ? "Created time" : "Work date"}
                  </button>
                )}
                columns={[
                  { label: "Date", render: (r) => dateLabel(r.work_date) },
                  { label: "Villa", render: (r) => getVillaName(r, data.villas) },
                  { label: "Employee", render: getEmployeeName },
                  { label: "Service", render: (r) => getServiceName(r, data.services) },
                  {
                    label: "Customer charge",
                    render: (r) => money(r.customer_charge)
                  },
                ]}
              />
              <PaginationControls
                page={safeRecentWorkPage}
                totalPages={recentWorkTotalPages}
                totalItems={filteredRecentWork.length}
                onPageChange={setRecentWorkPage}
              />
            </>
          ) : activePage === "villas" ? (
            <>
              <div className="welcome-row">
                <div>
                  <p className="eyebrow">{tr("PROPERTY PERFORMANCE")}</p>
                  <h1>{tr("Villas")}</h1>
                  <p className="muted">
                    Compare villa revenue and gross profit, with the highest-revenue properties first.
                  </p>
                </div>

                <AddRecord page={activePage}/>
              </div>

              <section className="panel table-panel">
                <div className="panel-heading">
                  <div>
                    <p className="eyebrow">{tr("VILLA FINANCIAL SUMMARY")}</p>
                    <h2>{tr("Villa revenue & gross profit")}</h2>
                  </div>
                  <span className="record-count">
                    {filteredVillaTable.length} villas
                  </span>
                </div>

                <div
                  className="search-box"
                  style={{ maxWidth: "360px", marginBottom: "16px" }}
                >
                  <Search size={17} />
                  <input
                    value={villaTableSearch}
                    onChange={(event) => {
                      setVillaTableSearch(event.target.value);
                      setVillaTablePage(1);
                    }}
                    placeholder="Search villas by name or area..."
                    aria-label="Search villas table"
                  />
                </div>

                {paginatedVillaTable.length === 0 ? (
                  <div className="empty-state">
                    No villas match your search.
                  </div>
                ) : (
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>{tr("Villa name")}</th>
                          <th>{tr("Area")}</th>
                          <th>{tr("Revenue")}</th>
                          <th>{tr("Gross profit")}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {paginatedVillaTable.map((villa) => (
                          <tr key={villa.id}>
                            <td>{villa.villa}</td>
                            <td>{villa.area ? `${villa.area} m²` : "—"}</td>
                            <td>{money(villa.income)}</td>
                            <td>{money(villa.netResult)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                <PaginationControls
                  page={villaTablePage}
                  totalPages={villaTableTotalPages}
                  totalItems={filteredVillaTable.length}
                  onPageChange={setVillaTablePage}
                />
              </section>

              <section className="panel" style={{ marginTop: "22px" }}>
                <div className="panel-heading">
                  <div>
                    <p className="eyebrow">INDIVIDUAL VILLA CHARTS</p>
                    <h2>Villa performance by revenue</h2>
                    <p className="muted" style={{ marginTop: "6px" }}>
                      Ordered from highest revenue to lowest revenue.
                    </p>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                    <button
                      type="button"
                      className="refresh-button"
                      onClick={() => setVillaChartDisplay(villaChartDisplay === "bar" ? "pie" : "bar")}
                      style={{ padding: "7px 10px", fontSize: "11px" }}
                    >
                      {villaChartDisplay === "bar" ? "Switch to pie charts" : "Switch to bar charts"}
                    </button>
                    <span className="record-count">{filteredVillaCharts.length} villas</span>
                  </div>
                </div>

                <div
                  className="search-box"
                  style={{ maxWidth: "360px", marginBottom: "18px" }}
                >
                  <Search size={17} />
                  <input
                    value={villaChartSearch}
                    onChange={(event) => {
                      setVillaChartSearch(event.target.value);
                      setVillaChartPage(1);
                    }}
                    placeholder="Search villa charts by name..."
                    aria-label="Search villa charts"
                  />
                </div>

                {paginatedVillaCharts.length === 0 ? (
                  <div className="empty-state">
                    No villa charts match your search.
                  </div>
                ) : (
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                      gap: "18px",
                    }}
                  >
                    {paginatedVillaCharts.map((villa) => (
                      <div
                        key={villa.id}
                        style={{
                          minWidth: 0,
                          border: "1px solid #eee9df",
                          borderRadius: "12px",
                          padding: "14px 10px 8px",
                          background: "rgba(255,255,255,0.55)",
                        }}
                      >
                        <h3
                          style={{
                            margin: "0 0 4px",
                            fontSize: "14px",
                            fontWeight: 600,
                            color: "#3f493f",
                          }}
                        >
                          {villa.villa}
                        </h3>
                        <p
                          className="muted"
                          style={{ margin: "0 0 8px", fontSize: "11px" }}
                        >
                          Revenue: {money(villa.income)}
                        </p>
                        <div style={{ width: "100%", height: villaChartDisplay === "pie" ? "270px" : "190px" }}>
                          <FinancialBreakdownChart
                            displayType={villaChartDisplay}
                            revenue={villa.income}
                            expenses={villa.outcome}
                            grossProfit={villa.netResult}
                          />
                        </div>
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            gap: "6px",
                            flexWrap: "wrap",
                            fontSize: "10px",
                            color: "#718477",
                            padding: "2px 4px 4px",
                          }}
                        >
                          <span>Expenses: {money(villa.outcome)}</span>
                          <strong>Gross profit: {money(villa.netResult)}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <PaginationControls
                  page={villaChartPage}
                  totalPages={villaChartTotalPages}
                  totalItems={filteredVillaCharts.length}
                  onPageChange={setVillaChartPage}
                />
              </section>
            </>
          ) : activePage === "departments" ? (
            <>
              <div className="welcome-row">
                <div>
                  <p className="eyebrow">{tr("DEPARTMENT PERFORMANCE")}</p>
                  <h1>{tr("Departments")}</h1>
                  <p className="muted">
                    Compare department revenue and gross profit, with the highest-revenue departments first.
                  </p>
                </div>

                <AddRecord page={activePage}/>
              </div>

              <section className="panel table-panel">
                <div className="panel-heading">
                  <div>
                    <p className="eyebrow">{tr("DEPARTMENT FINANCIAL SUMMARY")}</p>
                    <h2>{tr("Department revenue & gross profit")}</h2>
                  </div>
                  <span className="record-count">
                    {filteredDepartmentTable.length} departments
                  </span>
                </div>

                <div
                  className="search-box"
                  style={{ maxWidth: "360px", marginBottom: "16px" }}
                >
                  <Search size={17} />
                  <input
                    value={departmentTableSearch}
                    onChange={(event) => {
                      setDepartmentTableSearch(event.target.value);
                      setDepartmentTablePage(1);
                    }}
                    placeholder="Search departments..."
                    aria-label="Search departments table"
                  />
                </div>

                {paginatedDepartmentTable.length === 0 ? (
                  <div className="empty-state">
                    No departments match your search.
                  </div>
                ) : (
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>{tr("Department")}</th>
                          <th>{tr("Revenue")}</th>
                          <th>{tr("Gross profit")}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {paginatedDepartmentTable.map((department) => (
                          <tr key={department.id}>
                            <td>{department.department}</td>
                            <td>{money(department.revenue)}</td>
                            <td>{money(department.grossProfit)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                <PaginationControls
                  page={departmentTablePage}
                  totalPages={departmentTableTotalPages}
                  totalItems={filteredDepartmentTable.length}
                  onPageChange={setDepartmentTablePage}
                />
              </section>

              <section className="panel" style={{ marginTop: "22px" }}>
                <div className="panel-heading">
                  <div>
                    <p className="eyebrow">INDIVIDUAL DEPARTMENT CHARTS</p>
                    <h2>Department performance by revenue</h2>
                    <p className="muted" style={{ marginTop: "6px" }}>
                      Ordered from highest revenue to lowest revenue.
                    </p>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                    <button
                      type="button"
                      className="refresh-button"
                      onClick={() => setDepartmentChartDisplay(departmentChartDisplay === "bar" ? "pie" : "bar")}
                      style={{ padding: "7px 10px", fontSize: "11px" }}
                    >
                      {departmentChartDisplay === "bar" ? "Switch to pie charts" : "Switch to bar charts"}
                    </button>
                    <span className="record-count">{filteredDepartmentCharts.length} departments</span>
                  </div>
                </div>

                <div
                  className="search-box"
                  style={{ maxWidth: "360px", marginBottom: "18px" }}
                >
                  <Search size={17} />
                  <input
                    value={departmentChartSearch}
                    onChange={(event) => {
                      setDepartmentChartSearch(event.target.value);
                      setDepartmentChartPage(1);
                    }}
                    placeholder="Search department charts..."
                    aria-label="Search department charts"
                  />
                </div>

                {paginatedDepartmentCharts.length === 0 ? (
                  <div className="empty-state">
                    No department charts match your search.
                  </div>
                ) : (
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                      gap: "18px",
                    }}
                  >
                    {paginatedDepartmentCharts.map((department) => (
                      <div
                        key={department.id}
                        style={{
                          minWidth: 0,
                          border: "1px solid #eee9df",
                          borderRadius: "12px",
                          padding: "14px 10px 8px",
                          background: "rgba(255,255,255,0.55)",
                        }}
                      >
                        <h3
                          style={{
                            margin: "0 0 4px",
                            fontSize: "14px",
                            fontWeight: 600,
                            color: "#3f493f",
                          }}
                        >
                          {department.department}
                        </h3>
                        <p
                          className="muted"
                          style={{ margin: "0 0 8px", fontSize: "11px" }}
                        >
                          Revenue: {money(department.revenue)}
                        </p>
                        <div style={{ width: "100%", height: departmentChartDisplay === "pie" ? "270px" : "190px" }}>
                          <FinancialBreakdownChart
                            displayType={departmentChartDisplay}
                            revenue={department.revenue}
                            expenses={department.expenses}
                            grossProfit={department.grossProfit}
                          />
                        </div>
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            gap: "6px",
                            flexWrap: "wrap",
                            fontSize: "10px",
                            color: "#718477",
                            padding: "2px 4px 4px",
                          }}
                        >
                          <span>Expenses: {money(department.expenses)}</span>
                          <strong>Gross profit: {money(department.grossProfit)}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <PaginationControls
                  page={departmentChartPage}
                  totalPages={departmentChartTotalPages}
                  totalItems={filteredDepartmentCharts.length}
                  onPageChange={setDepartmentChartPage}
                />
              </section>
            </>
          ) : activePage === "services" ? (
            <PerformancePage
              eyebrow={tr("SERVICE PERFORMANCE")}
              title="Services"
              subtitle="Compare revenue and gross profit generated by each service, with the highest-revenue services first."
              tableEyebrow={tr("SERVICE FINANCIAL SUMMARY")}
              tableTitle={tr("Service revenue & gross profit")}
              items={servicePerformanceData.map((item) => ({ ...item, name: item.name }))}
              tableColumns={[
                { label: "Service type", key: "name" },
                { label: "Department", key: "department" },
                { label: "Revenue", render: (item) => money(item.revenue) },
                { label: "Gross profit", render: (item) => money(item.grossProfit) },
              ]}
              searchPlaceholder={tr("Search services or departments...")}
              chartSearchPlaceholder={tr("Search service charts...")}
              revenueLabel={tr("Revenue")}
              expenseLabel={tr("Employee cost")}
              grossLabel={tr("Gross profit")}
              onRefresh={loadDashboard}
            />
          ) : activePage === "employees" ? (
            <PerformancePage
              eyebrow={tr("EMPLOYEE PERFORMANCE")}
              title="Employees"
              subtitle="Review each employee's salary arrangement, customer revenue generated and gross earnings."
              tableEyebrow={tr("EMPLOYEE EARNINGS SUMMARY")}
              tableTitle={tr("Salary, revenue earned & gross earned")}
              items={employeePerformanceData.map((item) => ({ ...item, name: item.name }))}
              tableColumns={[
                { label: "Employee", key: "name" },
                { label: "Department", key: "department" },
                { label: "Salary type", key: "salaryType" },
                { label: "Salary", key: "salaryDisplay" },
                { label: "Revenue earned", render: (item) => money(item.revenue) },
                { label: "Gross earned", render: (item) => money(item.grossProfit) },
              ]}
              searchPlaceholder={tr("Search employees, departments or salary type...")}
              chartSearchPlaceholder={tr("Search employee charts...")}
              revenueLabel={tr("Revenue earned")}
              expenseLabel={tr("Recorded salary cost")}
              grossLabel={tr("Gross earned")}
              onRefresh={loadDashboard}
            />
          ) : currentPage ? (
            <>
              <div className="welcome-row">
                <div>
                  <p className="eyebrow">{tr("PAROS KATOIKIA DATABASE")}</p>
                  <h1>{tr(currentPage.title)}</h1>
                  <p className="muted">{tr(currentPage.subtitle)}</p>
                </div>

                <AddRecord page={activePage}/>
              </div>

              {activePage === "workEntries" ? (
                <WorkEntryTable rows={currentPage.rows} columns={currentPage.columns} search={search} onSearchChange={setSearch} data={data}/>
              ) : (
                <DataTable title={currentPage.title} rows={currentPage.rows} columns={currentPage.columns}/>
              )}
            </>
          ) : (
            <section className="panel">
              <h2>Settings</h2>
              <p className="muted">
                Your dashboard is connected to the Django API.
              </p>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
