# Payroll-System


## Core Modules of the System

### 1. Employee Management Module
* **Data:** Employee ID, Name, Role, Assigned Shift (1, 2, or 3).
* **Functions:** Add a new employee, edit details, or remove an employee.

### 2. Time and Attendance Tracking
* **Data:** Days worked, standard hours logged, overtime hours logged.
* **Functions:** A way to input (or read from a file) how many hours an employee worked in a given cutoff period.

### 3. Earnings Calculator (Gross Pay)
* **Standard Pay:** Calculating days/hours worked multiplied by the base rate (600 PhP).
* **Overtime Pay:** Adding the 75 PhP/hour rate for any OT hours.
* **Night Differential:** Applying the extra 60 PhP bonus for employees assigned to Shift 3 (10 PM - 6 AM).

### 4. Deductions Calculator
* **Mandatory Deductions:** Standard statutory deductions (e.g., SSS, PhilHealth, and Pag-IBIG) or a flat tax rate depending on syllabus requirements.
* **Penalties:** Deductions for being late or taking unpaid absences.

### 5. Payslip Generation (Output)
* **Net Pay:** Gross Pay minus Deductions.
* **Functions:** Displaying a clear summary screen for the employee, or exporting the final payslip to a text file or PDF.
