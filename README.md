# DORIAN-RCT-Dashboard

Web-based clinical dashboard (Django) to manage the workflow of a Randomized Controlled Trial (RCT) for the **DORIAN GRAY** project: participant registration, visit management, questionnaires, and wearable data.

---

## Contents
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Set Up the Database](#4-set-up-the-database)
  - [5. Create a Superuser Account](#5-create-a-superuser-account)
  - [6. Run the Development Server](#6-run-the-development-server)
- [How to Test the Application](#how-to-test-the-application)
  - [Step 1: Admin Setup](#step-1-admin-setup)
  - [Step 2: Clinician Dashboard](#step-2-clinician-dashboard)
  - [Step 3: Manage a Visit](#step-3-manage-a-visit)
  - [Step 4: Complete an Assessment](#step-4-complete-an-assessment)
  - [Step 5: Test Wearable Data](#step-5-test-wearable-data)

---

## Prerequisites
- Python **3.8+**
- `pip`
- `git`

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/vtsakan/dorian-rct-dashboard.git
cd dorian-rct-dashboard
```

### 2. Create and Activate a Virtual Environment
**macOS/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up the Database
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 5. Create a Superuser Account
```bash
python3 manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python3 manage.py runserver
```

App runs at: <http://127.0.0.1:8000/>

---

## How to Test the Application

### Step 1: Admin Setup
1. Open <http://127.0.0.1:8000/admin/> and log in with the superuser.
2. **Create a Study:** *Studies → Add study* (e.g., “DORIAN GRAY Pilot”), set start date, save.
3. **Create a Questionnaire Template:** *Questionnaire templates → Add* (e.g., “HADS”), save.
4. **Add Questions:** Open the “HADS” template → **Questions** → add:
   - Text: `I feel tense or 'wound up'`
   - Order: `1`
   - Save.
5. **Add Choices:** From **Questions**, open the question → **Choices** → add:
   - `Not at all` → Value `0`
   - `Sometimes` → Value `1`
   - Save.

### Step 2: Clinician Dashboard
1. Go to <http://127.0.0.1:8000/> (you’ll be redirected to login).
2. **Patient List** → **Add New Participant**.
3. Fill details, select the study, **Save**.
4. The **Baseline Visit** is auto-created.

### Step 3: Manage a Visit
1. On the participant page, click **Manage Visit** (Baseline).
2. In the tile dashboard, choose **Manage Questionnaires**.
3. On **Assessments for this Visit**, select **HADS** → **Assign**.
4. **HADS** appears with a **Start Assessment** button.

### Step 4: Complete an Assessment
1. Click **Start Assessment** for **HADS**.
2. Fill the questionnaire → **Submit Answers**.
3. Status becomes **Complete**.
4. **Back to Visit Dashboard** → tile shows recent completion.
5. Open **Clinical & Functional Assessments**, enter sample data, **Save Data**.

### Step 5: Test Wearable Data
1. Stop the server (Ctrl+C).
2. Generate sample wearable data for participant ID `1`:
```bash
python3 manage.py add_wearable_data 1
```
3. Restart:
```bash
python3 manage.py runserver
```
4. On the participant page, open **Wearable Data** (left sidebar) to see summary tiles and time-series charts.
