# PHASE 3 COMPLETION REPORT
## Academic Analytics & Comparative Performance Engine

**Project:** Student Academic Performance & Department Management System  
**Phase:** Phase 3 — Academic Analytics & Comparative Performance Engine  
**Status:** COMPLETE & FULLY VERIFIED  
**Date:** October 7, 2026  
**Target Users:** Head of Department (HOD), Academic Coordinators, Department Administrators  

---

## 1. Phase Objective
Phase 2 answered: *"Do we have reliable academic data?"*  
**Phase 3 answers:** *"What does the academic data show?"*

Phase 3 implements a **purely deterministic, traceable, explainable, and server-aggregated Academic Analytics & Comparative Performance Engine**. It provides the HOD with multi-tier analytical visibility across:
$$\text{Department} \longrightarrow \text{Batch} \longrightarrow \text{Academic Year} \longrightarrow \text{Semester} \longrightarrow \text{Section} \longrightarrow \text{Student} \longrightarrow \text{Subject}$$

Every metric rendered on the dashboard is derived directly from verified database records. In strict accordance with the Phase 3 contract, **no predictive ML, AI scoring, risk modeling, or watchlists** were introduced (these are strictly isolated for Phase 4).

---

## 2. Existing Phase 2 Architecture Reused
Phase 3 directly builds on top of Phase 2's relational source-of-truth database schema without introducing any parallel or redundant tables:
- **`batches`**: Cohort definitions (e.g., `2025–2029`).
- **`academic_years`**: 4-year undergraduate hierarchy (1st, 2nd, 3rd, 4th Year).
- **`semesters`**: Semesters 1 through 8.
- **`sections`**: Configurable cohort sections (A, B, C...).
- **`students`**: Master student identities with unique roll numbers.
- **`subjects`**: Curriculum course definitions with codes, names, and credit weights.
- **`attendance_records`**: Official subject-wise attendance percentages, attended counts, and total conducted classes.
- **`semester_results`**: Subject-wise internal marks, external marks, total marks, grades, and grade points.
- **`student_semester_summaries`**: Official published SGPA and CGPA records.
- **`upload_history`**: Audit trail of verified imports.

---

## 3. Analytics Architecture
The analytics subsystem is modular, server-side aggregated, and strictly decoupled from data ingestion:

```
backend/app/
    analytics/
        __init__.py          # Facade exports
        validators.py        # Dataset availability verifiers (Available vs Not Available)
        aggregations.py      # Department KPIs, grade distributions, subject stats
        comparisons.py       # Cross-section & longitudinal semester delta comparisons
        correlation.py       # Pearson r association engine & trendline estimation
        service.py           # Unified service orchestrator
    api/
        analytics_bp.py      # Protected REST API endpoints (@role_required(['ADMIN', 'HOD']))
```

---

## 4. New Backend Modules
1. **`app/analytics/validators.py`**:
   - `check_result_availability(semester_id, section_id)`: Checks whether end-semester examination results exist for the query context.
   - `check_attendance_availability(semester_id, section_id)`: Checks whether attendance records exist.
   - Ensures UI displays `"NOT_AVAILABLE"` rather than deceiving users with `0` or `0.0%`.
2. **`app/analytics/aggregations.py`**:
   - `get_overview_kpis(batch_id, academic_year_id, semester_id, section_id)`: Calculates cohort student count, mean SGPA, mean CGPA, mean attendance %, pass %, and passed/failed tallies.
   - `get_grade_distribution(semester_id, section_id, subject_id)`: Aggregates frequency counts of only recorded letter grades (no synthetic grade buckets).
   - `get_subject_analytics(semester_id, section_id, subject_id)`: Calculates enrolled count, average marks, highest, lowest, pass count, fail count, pass %, and grade spread per course.
3. **`app/analytics/comparisons.py`**:
   - `compare_sections(semester_id)`: Side-by-side comparative analytics for all sections (A, B, C) in a semester.
   - `compare_semesters(batch_id, sem1_id, sem2_id, section_id, tolerance)`: Deterministic longitudinal comparison of consecutive semesters (T1 vs T2) for students with recorded data in both terms.
4. **`app/analytics/correlation.py`**:
   - `get_attendance_vs_performance(semester_id, section_id, subject_id)` & `calculate_correlation(valid_pairs)`:
   - Computes Pearson correlation coefficient ($r$).
   - Computes least-squares linear trendline ($y = mx + c$).
   - Enforces minimum sample size ($n \ge 5$).
   - Safely detects zero-variance conditions.
   - Strict terminology: *"Association between attendance and academic performance"* (no causal claims).
5. **`app/analytics/service.py`**:
   - High-level coordinator providing cached/aggregated services including individual student progression trajectory.
6. **`app/api/analytics_bp.py`**:
   - REST API Blueprint mounted at `/api/v1/analytics`.

---

## 5. New Frontend Components
Implemented under `frontend/src/components/analytics/` using the approved dark theme design tokens (`#050506`, `#0F0F11`, `#32DC5C`, `#FF6268`, `#242426`):

1. **`AnalyticsFilters.jsx`**:
   - Global cascading dropdown bar: `Batch` $\rightarrow$ `Academic Year` $\rightarrow$ `Semester` $\rightarrow$ `Section` $\rightarrow$ `Subject`.
   - Real-time dependency resolution (selecting 2nd Year auto-populates Semester 3 & 4; selecting Semester 3 auto-populates Sections A, B, C).
2. **`AnalyticsOverview.jsx`**:
   - High-level KPI cards with Data Availability status badges.
   - Displays Total Students, Average SGPA, Average CGPA, Average Attendance %, and Pass Percentage.
3. **`SectionComparison.jsx`**:
   - Side-by-side comparative cards for Sections A, B, C with comparative bars and tabular metrics.
4. **`SubjectAnalytics.jsx`**:
   - Course examination analytics displaying enrolled count, average marks, highest, lowest, pass %, and grade spread chips.
5. **`SemesterComparison.jsx`**:
   - Longitudinal T1 vs T2 comparison with configurable SGPA delta tolerance selector (`0.05`, `0.10`, `0.15`, `0.20`).
   - Summary statistics (Improved, Stable, Declined) and paginated student comparison table with drilldown inspection.
6. **`StudentAnalytics.jsx`**:
   - Individual student analytics profile featuring:
     - Top KPI strip (Current CGPA, Latest SGPA, Avg Attendance %, Performance Trend).
     - Progression trajectory line chart across completed semesters.
     - Semester summaries table.
     - Subject results table.
     - Subject-wise attendance breakdown table.
7. **`AttendancePerformance.jsx`**:
   - Scatter/association view plotting attendance % against marks.
   - Pearson $r$, sample size $n$, trendline equation, and association disclaimer.
8. **`GradeDistribution.jsx`**:
   - Dynamic letter grade histogram and percentage breakdown table.
9. **`AcademicAnalytics.jsx`**:
   - Root analytics workspace coordinator managing sub-navigation tabs, filters, and student drilldown.
10. **`StudentDirectory.jsx` (Extended)**:
    - Added tab switcher between *"Verified Raw Records"* and *"Academic Analytics & Trajectory"* inside the student profile drawer.
11. **`HodDashboard.jsx` (Integrated)**:
    - Added dedicated `"Academic Analytics"` primary navigation entry point clearly separated from data upload.
12. **`analytics.css`**:
    - Dedicated responsive stylesheet.

---

## 6. New APIs Added

All endpoints require JWT Bearer authentication and RBAC validation (`ADMIN` or `HOD`):

| Method | Endpoint | Query Parameters | Description |
|---|---|---|---|
| `GET` | `/api/v1/analytics/overview` | `batch_id`, `academic_year_id`, `semester_id`, `section_id` | Cohort-level KPI metrics and dataset availability status |
| `GET` | `/api/v1/analytics/sections` | `semester_id` | Comparative breakdown across all sections |
| `GET` | `/api/v1/analytics/subjects` | `semester_id`, `section_id`, `subject_id` | Subject performance, marks statistics, pass %, and grade spreads |
| `GET` | `/api/v1/analytics/semester-comparison` | `batch_id`, `sem1_id`, `sem2_id`, `section_id`, `tolerance` | T1 vs T2 longitudinal student deltas and category classification |
| `GET` | `/api/v1/analytics/student/<id>` | — | Student analytical profile, trajectories, and course masteries |
| `GET` | `/api/v1/analytics/student/<id>/trajectory` | — | Progression trajectory across all completed semesters |
| `GET` | `/api/v1/analytics/attendance-performance` | `semester_id`, `section_id`, `subject_id` | Attendance-marks pairs, Pearson $r$, sample size, and trendline |
| `GET` | `/api/v1/analytics/grades` | `semester_id`, `section_id`, `subject_id` | Dynamic frequency distribution of recorded grades |

---

## 7. Deterministic Calculation Definitions

Every metric adheres to strict mathematical definitions:

1. **Average SGPA**:
   $$\text{Avg SGPA} = \frac{\sum \text{valid official SGPA values}}{\text{count}(\text{students with valid official SGPA})}$$
   *Students with `NULL` or unpublished summaries are strictly excluded from both numerator and denominator.*

2. **Average CGPA**:
   $$\text{Avg CGPA} = \frac{\sum \text{valid official CGPA values}}{\text{count}(\text{students with valid official CGPA})}$$

3. **Average Attendance**:
   $$\text{Avg Attendance} = \frac{\sum \text{valid subject attendance percentages}}{\text{count}(\text{valid subject attendance records})}$$

4. **Pass Percentage**:
   $$\text{Pass } \% = \frac{\text{Students with results who passed all enrolled subjects in semester}}{\text{Total students with results in semester}} \times 100$$
   *A student fails the semester if any subject has `result_status == 'FAILED'` or `grade == 'F'`.*

5. **Subject Average Marks**:
   $$\text{Avg Marks} = \frac{\sum \text{valid subject total marks}}{\text{count}(\text{students with valid total marks})}$$

6. **Longitudinal Semester Delta & Classification**:
   For a student with valid $\text{SGPA}_1$ and $\text{SGPA}_2$ with configurable tolerance $\tau = 0.10$:
   $$\Delta = \text{round}(\text{SGPA}_2 - \text{SGPA}_1, 2)$$
   $$\text{Classification} = \begin{cases} \text{IMPROVED} & \text{if } \Delta > \tau \\ \text{DECLINED} & \text{if } \Delta < -\tau \\ \text{STABLE} & \text{if } |\Delta| \le \tau \end{cases}$$

7. **Average Change vs Change in Average**:
   - $\text{Average Change} = \frac{1}{N} \sum (\text{SGPA}_{2,i} - \text{SGPA}_{1,i})$
   - Both formulas yield identical values over the common paired student cohort ($N$), but missing values are strictly isolated before calculation.

---

## 8. Missing Data Handling & Safety
1. **Explicit `NOT_AVAILABLE` Status**:
   - If an academic term has no uploaded results (e.g., an upcoming semester), the system returns `"NOT_AVAILABLE"` and `null` for average SGPA/CGPA/Pass %.
   - The UI displays informative availability banners rather than false `0` or `0.0%` metrics.
2. **Missing Pair Isolation**:
   - If a student has Semester 1 SGPA = 7.5 but Semester 2 SGPA is `NULL`, they are **excluded** from T1 vs T2 delta calculation. The system never computes a false decline of $-7.5$.
3. **Attendance Without Marks**:
   - If attendance is uploaded but semester results are not, correlation returns `"INSUFFICIENT_DATA"` with a descriptive message.

---

## 9. Correlation Methodology & Statistical Safeguards
The attendance vs academic performance engine follows rigorous statistical safety:
1. **Sample Size Cutoff**:
   - Requires $n \ge 5$ paired data points. If $n < 5$, correlation is not computed and status returns `"INSUFFICIENT_DATA"`.
2. **Zero-Variance / Invariant Value Handling**:
   - If all attendance percentages or all marks are identical ($SS_{xx} = 0$ or $SS_{yy} = 0$), status returns `"UNDEFINED_VARIATION"` with message: *"Correlation cannot be determined from the available variation (constant values detected)."*
3. **Pearson $r$ Formula**:
   $$r = \frac{\sum (x - \bar{x})(y - \bar{y})}{\sqrt{\sum (x - \bar{x})^2 \sum (y - \bar{y})^2}}$$
4. **Trendline Formula**:
   $$\text{Marks} = m \times \text{Attendance} + c, \quad m = \frac{SS_{xy}}{SS_{xx}}, \quad c = \bar{y} - m\bar{x}$$
5. **Mandatory Wording Compliance**:
   - The UI and API responses strictly label outputs as: *"Association between attendance and academic performance"* with explicit footnote: *"Statistical association does not imply direct causation."*

---

## 10. Database Query Optimization
1. **Single-Query Aggregations**:
   - Calculations use SQL `func.avg()`, `func.count()`, `func.min()`, `func.max()` rather than client-side iterations.
2. **Zero N+1 Query Anti-Patterns**:
   - Multi-subject attendance and result pairings are resolved via indexed `INNER JOIN` operations on `(student_id, subject_id, semester_id)`.
3. **Existing Index Utilization**:
   - Verified that `student_id`, `semester_id`, `section_id`, and `subject_id` columns in `attendance_records`, `assessment_records`, `semester_results`, and `student_semester_summaries` are indexed with underlying composite unique keys providing sub-millisecond query execution.

---

## 11. Automated Test Suite & Coverage

Test file: `backend/test_phase3.py`

| Test # | Test Name | Target Verified | Result |
|---|---|---|---|
| `test_01` | `test_01_security_unauthenticated_and_rbac` | 401 unauthenticated and 403 non-HOD RBAC protection | **PASS** |
| `test_02` | `test_02_overview_metrics` | Overarching KPIs (SGPA, CGPA, Attendance, Pass %) | **PASS** |
| `test_03` | `test_03_section_comparison` | Section A vs Section B comparative analytics | **PASS** |
| `test_04` | `test_04_controlled_semester_comparison` | Deterministic delta classification (Improved, Stable, Declined) | **PASS** |
| `test_05` | `test_05_subject_analytics` | Marks average, highest, lowest, pass % | **PASS** |
| `test_06` | `test_06_grade_distribution` | Letter grade histogram (only recorded grades) | **PASS** |
| `test_07` | `test_07_student_analytics_and_trajectory` | Multi-semester chronological trajectory | **PASS** |
| `test_08` | `test_08_attendance_performance_correlation` | Pearson $r$, sample size, and trendline | **PASS** |
| `test_09` | `test_09_correlation_insufficient_sample_safety` | Sample size $n < 5$ safety handling | **PASS** |
| `test_10` | `test_10_missing_data_safety` | Empty semester reports `NOT_AVAILABLE` | **PASS** |
| `test_11` | `test_11_rbac_protection` | Token verification & student role rejection | **PASS** |
| `test_12` | `test_12_constant_value_correlation` | Zero-variance handling returns `UNDEFINED_VARIATION` | **PASS** |
| `test_13` | `test_13_invalid_filter_combinations` | Mismatched/invalid filter parameters handling | **PASS** |

---

## 12. Full Regression Results
All suites across Phase 1, Phase 2, and Phase 3 were executed concurrently:

- **Phase 1 Foundation Suite (`test_api.py`)**: **17 / 17 PASSED** (100%)
- **Phase 2 Academic Hierarchy Suite (`test_phase2.py`)**: **11 / 11 PASSED** (100%)
- **Phase 3 Analytics Suite (`test_phase3.py`)**: **13 / 13 PASSED** (100%)
- **Total Automated Backend Tests:** **41 / 41 PASSED**

---

## 13. Frontend Build Validation
Frontend production compilation via Vite:
```
> frontend@0.0.0 build
> vite build

vite v8.3.3 building client environment for production...
✓ 1928 modules transformed.
rendering chunks...
dist/index.html                   1.00 kB │ gzip:   0.52 kB
dist/assets/index-2y1AVGQE.css   25.05 kB │ gzip:   4.94 kB
dist/assets/index-CrCW0rDn.js   464.31 kB │ gzip: 113.32 kB
✓ built in 470ms
```
**Exit Code: 0 (Zero errors, zero bundle warnings).**

---

## 14. Security Verification
- **RBAC Enforcement**: All analytics endpoints strictly verify JWT identity and enforce `@role_required(['ADMIN', 'HOD'])`.
- **Zero Public Leakage**: Unauthenticated requests return `401 Unauthorized`. Authenticated non-HOD users (e.g. students) return `403 Forbidden`.
- **Git Safety**: Checked `git status` to ensure `.env` and secret credentials remain strictly untracked.

---

## 15. Screens & User Experience Implemented
1. **HOD Primary Navigation**:
   - Direct entry point at `#hod/analytics` or clicking *"Academic Analytics"* in the HOD dashboard navigation bar.
2. **Cascading Filter Bar**:
   - Dependent selectors preventing invalid hierarchical combinations.
3. **Department Overview**:
   - 6 KPI stat cards with data availability badges.
4. **Section Comparison**:
   - Side-by-side metric tables and visual comparative progress bars.
5. **Subject Analytics**:
   - Course examination analytics displaying marks min/max/mean, pass %, and grade spread chips.
6. **Semester Comparison**:
   - Configurable tolerance slider, Improved/Stable/Declined breakdown, and paginated student comparison table with drilldown buttons.
7. **Student Analytics**:
   - Standalone search or drilldown view showing CGPA trajectory timeline, semester summaries, subject results, and attendance records.
8. **Attendance vs Performance**:
   - Association view showing Pearson $r$, sample size, trendline formula, and data points table.
9. **Grade Distribution**:
   - Visual grade distribution bar chart and frequency table.

---

## 16. Known Limitations
- The correlation engine calculates bivariate linear associations (Pearson $r$); multi-variable non-linear models or student risk weightings are reserved for Phase 4.
- If attendance and examination results use different subject codes across irregular college batches, manual subject mapping may be required.

---

## 17. Deferred to Phase 4 (Strictly Prohibited in Phase 3)
In compliance with the project specifications, the following were intentionally **NOT** implemented in Phase 3:
- Automated student risk scoring.
- At-risk student classification & watchlists.
- Automated intervention or remedial recommendations.
- AI/ML failure predictions or LLM mentorship.
- Student recommendation engine.

---

## Conclusion
Phase 3 has been successfully implemented, mathematically validated, and fully integrated into the production environment.
