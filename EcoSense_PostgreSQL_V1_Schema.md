# EcoSense — PostgreSQL V1 Schema

## Project Context

**Project:** AI-Based Zero Waste Campus Management Platform  
**Institution:** Don Bosco Institute of Technology (DBIT), Mumbai

This document records the agreed **PostgreSQL V1 database schema** for the EcoSense project so it can be reused as implementation and context reference in later conversations.

---

## 1. Current Project Scope

The V1 database supports:

1. Web/App Platform
2. Role-Based User Management
3. QR-Based Bin Management
4. Digital Waste Reporting
5. AI Waste Classification
6. Waste Generation/Accumulation Prediction
7. Collection & Bin History
8. Recycling/Composting Management
9. Gamification & Rewards
10. Administrative Analytics

### Explicitly excluded for V1

- **Route optimization:** Removed because waste is collected from campus bins at the end of the day and vehicle route optimization inside the campus is unnecessary.
- **Green Index:** Removed for now. It may be added later as an optional module. The V1 schema should therefore preserve useful waste, collection, recycling, and composting data without making Green Index a dependency.

---

# 2. Database Choice

**Database:** PostgreSQL

PostgreSQL was selected instead of NoSQL because the project contains many related entities and historical records requiring:

- Foreign-key relationships
- Referential integrity
- Structured transactional data
- Historical records
- Aggregation and analytics
- Future extensibility
- Potential future support for geospatial data

---

# 3. Important Design Decisions

## 3.1 One Waste Type Per Physical Bin

A physical bin has exactly **one designated waste type**.

Example:

```text
B-001 → Canteen → WET_ORGANIC
B-002 → Canteen → DRY_RECYCLABLE
B-003 → Admin Office → PAPER
B-004 → Workshop → E_WASTE
```

Therefore, `bins.waste_type_id` is a direct foreign key to `waste_types`.

A many-to-many `bin_waste_types` table is not required in V1.

---

## 3.2 QR Code Design

Every physical bin receives a unique QR code.

The QR code should identify the bin using an opaque `qr_token`, rather than encoding mutable bin information.

Conceptually:

```text
https://<domain>/bin/<qr_token>
```

The same QR can be scanned by:

- Student
- Staff
- Collector
- Admin

The backend determines available actions based on the authenticated user's role.

A dedicated in-app QR scanner is optional because the QR can also open a web/deep link.

---

## 3.3 Locations vs Buildings

`locations` represents actual waste-generating or waste-management areas, not simply buildings.

A building may contain multiple locations/departments/areas.

Example:

```text
Building
 ├── Canteen
 ├── Computer Lab
 ├── Admin Office
 └── Classroom Area
```

Each location can contain multiple bins.

---

## 3.4 Current Fill vs Historical Fill

`bins.current_fill_percentage` stores only the **current state**.

Historical measurements belong in:

```text
bin_fill_readings
```

This allows the system to analyze how quickly individual bins fill and provides historical data for prediction.

---

## 3.5 Student Disposal Quantity

Students will generally not know the exact weight of waste they dispose of.

Therefore, `quantity_kg` in `disposal_records` is optional.

A normal student disposal can simply be recorded as an event:

```text
Student → scanned bin → disposal recorded
```

No artificial weight should be forced into the database.

---

## 3.6 Waste Processing

Waste is modeled as a lifecycle:

```text
Disposal
   ↓
Collection
   ↓
Processing
   ├── Recycling
   └── Composting
```

Separate tables are used for disposal, collection, recycling, and composting rather than creating one generic waste transaction table.

---

## 3.7 Images

Images should not be stored directly inside PostgreSQL in V1.

Store the image in appropriate file/object storage and save its URL/path in fields such as:

```text
image_url
```

This applies to AI classification images and waste-report images.

---

# 4. Database Extension

UUID generation uses PostgreSQL's `pgcrypto` extension.

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

---

# 5. Core Schema

## 5.1 roles

Stores the application's user roles.

```sql
CREATE TABLE roles (
    role_id SMALLSERIAL PRIMARY KEY,
    role_name VARCHAR(30) NOT NULL UNIQUE
);
```

Initial roles:

```sql
INSERT INTO roles (role_name)
VALUES
    ('STUDENT'),
    ('STAFF'),
    ('COLLECTOR'),
    ('ADMIN');
```

---

## 5.2 users

Stores application users.

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id SMALLINT NOT NULL REFERENCES roles(role_id),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Notes

- Passwords must be stored as hashes, never plaintext.
- A user has one role in V1.
- Role permissions are primarily enforced by the backend/application layer.

---

## 5.3 locations

Stores physical campus locations.

```sql
CREATE TABLE locations (
    location_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location_type VARCHAR(50) NOT NULL,
    building VARCHAR(100),
    floor VARCHAR(30),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Examples

```text
Canteen
Computer Lab
Admin Office
Classroom Area
Workshop
Garden Area
```

Latitude/longitude are optional and are not related to route optimization.

---

## 5.4 waste_types

Defines waste categories used by bins and waste-processing records.

```sql
CREATE TABLE waste_types (
    waste_type_id SMALLSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```

Initial reference data:

```sql
INSERT INTO waste_types (name, description)
VALUES
    ('WET_ORGANIC', 'Organic and wet waste'),
    ('DRY_RECYCLABLE', 'Dry recyclable waste'),
    ('PAPER', 'Paper waste'),
    ('METAL', 'Metal waste'),
    ('E_WASTE', 'Electronic waste'),
    ('GARDEN', 'Garden and landscaping waste');
```

---

# 6. Bin and QR Management

## 6.1 bins

Represents each physical waste bin.

```sql
CREATE TABLE bins (
    bin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bin_code VARCHAR(50) NOT NULL UNIQUE,
    location_id BIGINT NOT NULL REFERENCES locations(location_id),
    waste_type_id SMALLINT NOT NULL REFERENCES waste_types(waste_type_id),
    capacity_litres DECIMAL(8,2),
    qr_token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    current_fill_percentage DECIMAL(5,2),
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    installed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_fill_percentage
        CHECK (
            current_fill_percentage IS NULL
            OR current_fill_percentage BETWEEN 0 AND 100
        )
);
```

### Bin status values

V1 uses:

```text
ACTIVE
FULL
DAMAGED
MISSING
INACTIVE
```

Constraint:

```sql
ALTER TABLE bins
ADD CONSTRAINT valid_bin_status
CHECK (
    status IN (
        'ACTIVE',
        'FULL',
        'DAMAGED',
        'MISSING',
        'INACTIVE'
    )
);
```

### QR principle

`qr_token` is independent from `bin_code` and other mutable bin information.

---

# 7. Digital Waste Activity

## 7.1 disposal_records

Records that a user disposed of waste into a particular bin.

```sql
CREATE TABLE disposal_records (
    disposal_id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id),
    bin_id UUID NOT NULL REFERENCES bins(bin_id),
    quantity_kg DECIMAL(8,3),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    CONSTRAINT positive_disposal_quantity
        CHECK (
            quantity_kg IS NULL
            OR quantity_kg > 0
        )
);
```

### Important design choice

`waste_type_id` is intentionally not duplicated here.

The bin already has its designated waste type:

```text
disposal_records.bin_id
        ↓
bins.waste_type_id
        ↓
waste_types
```

This prevents redundant storage of the same fact.

---

## 7.2 waste_reports

Records problems reported by users.

Examples:

- Overflowing bin
- Damaged bin
- Missing bin
- Wrong segregation
- Other issue

```sql
CREATE TABLE waste_reports (
    report_id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id),
    bin_id UUID REFERENCES bins(bin_id),
    report_type VARCHAR(50) NOT NULL,
    description TEXT,
    image_url TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(user_id)
);
```

### Report statuses

```sql
ALTER TABLE waste_reports
ADD CONSTRAINT valid_report_status
CHECK (
    status IN (
        'PENDING',
        'IN_PROGRESS',
        'RESOLVED',
        'REJECTED'
    )
);
```

### Proposed report types

```text
OVERFLOWING
DAMAGED_BIN
MISSING_BIN
WRONG_SEGREGATION
OTHER
```

These can be constrained in a later schema-hardening step.

---

# 8. Bin Monitoring and Collection

## 8.1 bin_fill_readings

Stores historical fill-level measurements.

```sql
CREATE TABLE bin_fill_readings (
    reading_id BIGSERIAL PRIMARY KEY,
    bin_id UUID NOT NULL REFERENCES bins(bin_id),
    fill_percentage DECIMAL(5,2) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(30) NOT NULL DEFAULT 'MANUAL',
    notes TEXT,

    CONSTRAINT valid_fill_percentage
        CHECK (fill_percentage BETWEEN 0 AND 100)
);
```

### `source`

Possible values:

```text
MANUAL
IOT
ESTIMATED
```

This allows the project to support smart-bin sensors later without redesigning the table.

---

## 8.2 collection_records

Records collection of waste from a physical bin.

```sql
CREATE TABLE collection_records (
    collection_id BIGSERIAL PRIMARY KEY,
    bin_id UUID NOT NULL REFERENCES bins(bin_id),
    collector_id UUID NOT NULL REFERENCES users(user_id),
    fill_level_before DECIMAL(5,2),
    collected_quantity_kg DECIMAL(8,3),
    fill_level_after DECIMAL(5,2),
    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    CONSTRAINT valid_fill_before
        CHECK (
            fill_level_before IS NULL
            OR fill_level_before BETWEEN 0 AND 100
        ),

    CONSTRAINT valid_fill_after
        CHECK (
            fill_level_after IS NULL
            OR fill_level_after BETWEEN 0 AND 100
        ),

    CONSTRAINT positive_collected_quantity
        CHECK (
            collected_quantity_kg IS NULL
            OR collected_quantity_kg > 0
        )
);
```

### Collection workflow

```text
Collector
   ↓
Scan Bin QR
   ↓
View bin status
   ↓
Record fill level
   ↓
Collect waste
   ↓
Record quantity
   ↓
Record resulting fill level
```

Route optimization is deliberately not part of this workflow.

---

# 9. AI Waste Classification

## 9.1 waste_classifications

Stores AI-based image classification results.

```sql
CREATE TABLE waste_classifications (
    classification_id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    disposal_id BIGINT REFERENCES disposal_records(disposal_id),
    image_url TEXT NOT NULL,
    predicted_waste_type_id SMALLINT REFERENCES waste_types(waste_type_id),
    confidence_score DECIMAL(5,4),
    model_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_confidence_score
        CHECK (
            confidence_score IS NULL
            OR confidence_score BETWEEN 0 AND 1
        )
);
```

### Example

```text
Image
  ↓
AI Model
  ↓
DRY_RECYCLABLE
  ↓
Confidence = 0.942
  ↓
Model Version = v1.0
```

The optional `disposal_id` allows a classification to be associated with an actual disposal event.

---

# 10. Waste Generation / Fill Prediction

## 10.1 fill_predictions

Stores historical AI predictions for bin fill levels.

```sql
CREATE TABLE fill_predictions (
    prediction_id BIGSERIAL PRIMARY KEY,
    bin_id UUID NOT NULL REFERENCES bins(bin_id),
    predicted_fill_percentage DECIMAL(5,2) NOT NULL,
    prediction_horizon_hours DECIMAL(6,2) NOT NULL,
    predicted_for TIMESTAMPTZ NOT NULL,
    model_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_predicted_fill
        CHECK (
            predicted_fill_percentage BETWEEN 0 AND 100
        ),

    CONSTRAINT positive_prediction_horizon
        CHECK (
            prediction_horizon_hours > 0
        )
);
```

### Example

```text
Bin B-001
Current fill: 60%

Prediction:
Predicted fill: 85%
Horizon: 6 hours
Predicted for: 18:00
Model: v1.0
```

Historical predictions are retained so model performance can later be evaluated against actual fill readings.

---

# 11. Recycling and Composting

## 11.1 recycling_records

Records waste sent for recycling.

```sql
CREATE TABLE recycling_records (
    recycling_id BIGSERIAL PRIMARY KEY,
    waste_type_id SMALLINT NOT NULL REFERENCES waste_types(waste_type_id),
    quantity_kg DECIMAL(10,3) NOT NULL,
    recycling_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recycler_name VARCHAR(150),
    reference_number VARCHAR(100),
    notes TEXT,
    recorded_by UUID NOT NULL REFERENCES users(user_id),

    CONSTRAINT positive_recycling_quantity
        CHECK (quantity_kg > 0)
);
```

The record is tied to the waste type rather than an individual bin because waste may be aggregated after collection.

Example:

```text
Multiple paper bins
      ↓
Collection
      ↓
Paper aggregated
      ↓
Recycling agency
      ↓
Recycling record
```

---

## 11.2 composting_records

Records organic waste entering and leaving the composting process.

```sql
CREATE TABLE composting_records (
    composting_id BIGSERIAL PRIMARY KEY,
    waste_type_id SMALLINT NOT NULL REFERENCES waste_types(waste_type_id),
    input_quantity_kg DECIMAL(10,3) NOT NULL,
    output_quantity_kg DECIMAL(10,3),
    composting_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    composting_method VARCHAR(100),
    notes TEXT,
    recorded_by UUID NOT NULL REFERENCES users(user_id),

    CONSTRAINT positive_input_quantity
        CHECK (input_quantity_kg > 0),

    CONSTRAINT valid_output_quantity
        CHECK (
            output_quantity_kg IS NULL
            OR output_quantity_kg >= 0
        )
);
```

`output_quantity_kg` is optional because compost output may not be measured during every operation.

---

# 12. Gamification

The gamification design uses **point transactions** rather than storing a single mutable total on `users`.

This keeps a history of how every point was earned.

---

## 12.1 gamification_actions

Defines activities that can earn points.

```sql
CREATE TABLE gamification_actions (
    action_id SMALLSERIAL PRIMARY KEY,
    action_code VARCHAR(50) NOT NULL UNIQUE,
    action_name VARCHAR(100) NOT NULL,
    description TEXT,
    default_points INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT valid_default_points
        CHECK (default_points >= 0)
);
```

Initial examples:

```sql
INSERT INTO gamification_actions
    (action_code, action_name, description, default_points)
VALUES
    ('DISPOSAL_RECORDED',
     'Record Waste Disposal',
     'Record a waste disposal using a bin QR code',
     5),

    ('WASTE_REPORT',
     'Report Waste Issue',
     'Report an overflowing, damaged, or missing bin',
     10),

    ('CORRECT_SEGREGATION',
     'Correct Waste Segregation',
     'Successfully dispose waste into the appropriate bin',
     10),

    ('CAMPAIGN_PARTICIPATION',
     'Campaign Participation',
     'Participate in a campus sustainability campaign',
     20);
```

These point values are examples and can be changed by the project/admin design.

---

## 12.2 user_points

Stores individual point-earning transactions.

```sql
CREATE TABLE user_points (
    points_id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id),
    action_id SMALLINT NOT NULL REFERENCES gamification_actions(action_id),
    points INTEGER NOT NULL,
    reference_id BIGINT,
    description TEXT,
    earned_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_points
        CHECK (points > 0)
);
```

Example:

```text
Student
 ├── Disposal recorded       +5
 ├── Waste issue reported   +10
 ├── Correct segregation    +10
 └── Campaign participation +20
```

The total can be calculated:

```sql
SELECT
    user_id,
    SUM(points) AS total_points
FROM user_points
GROUP BY user_id;
```

A `total_points` column is intentionally not stored in `users` in V1.

---

## 12.3 rewards

Defines rewards available for point redemption.

```sql
CREATE TABLE rewards (
    reward_id BIGSERIAL PRIMARY KEY,
    reward_name VARCHAR(150) NOT NULL,
    description TEXT,
    points_required INTEGER NOT NULL,
    stock_quantity INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_points_required
        CHECK (points_required > 0),

    CONSTRAINT valid_stock_quantity
        CHECK (
            stock_quantity IS NULL
            OR stock_quantity >= 0
        )
);
```

Possible examples:

```text
Sustainability Certificate
Campus Merchandise
Special Recognition
```

Actual rewards are determined by DBIT/project requirements.

---

## 12.4 reward_redemptions

Records students redeeming rewards.

```sql
CREATE TABLE reward_redemptions (
    redemption_id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id),
    reward_id BIGINT NOT NULL REFERENCES rewards(reward_id),
    points_spent INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    redeemed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ,
    processed_by UUID REFERENCES users(user_id),

    CONSTRAINT positive_points_spent
        CHECK (points_spent > 0),

    CONSTRAINT valid_redemption_status
        CHECK (
            status IN (
                'PENDING',
                'APPROVED',
                'REJECTED',
                'COMPLETED'
            )
        )
);
```

`points_spent` is stored at redemption time so historical records remain correct if the reward's current point cost changes later.

---

# 13. Leaderboard

A separate leaderboard table is **not required** in V1.

The leaderboard can be generated from `user_points`.

Example:

```sql
SELECT
    u.user_id,
    u.name,
    COALESCE(SUM(up.points), 0) AS total_points
FROM users u
LEFT JOIN user_points up
    ON u.user_id = up.user_id
WHERE u.role_id = (
    SELECT role_id
    FROM roles
    WHERE role_name = 'STUDENT'
)
GROUP BY u.user_id, u.name
ORDER BY total_points DESC;
```

This avoids maintaining duplicate leaderboard data.

---

# 14. Entity Relationship Overview

The high-level relationship structure is:

```text
roles
  │
  └──< users
          │
          ├──< disposal_records >── bins >── locations
          │                            │
          │                            └──> waste_types
          │
          ├──< waste_reports >── bins
          │
          ├──< waste_classifications
          │             │
          │             └──> disposal_records
          │
          ├──< user_points >── gamification_actions
          │
          └──< reward_redemptions >── rewards


bins
 │
 ├──< bin_fill_readings
 │
 ├──< collection_records
 │
 └──< fill_predictions


waste_types
 │
 ├──< recycling_records
 │
 └──< composting_records
```

---

# 15. Waste Lifecycle

The V1 data model represents the campus waste lifecycle as:

```text
                    ┌───────────────┐
                    │ Waste Source  │
                    └───────┬───────┘
                            │
                            ▼
                     ┌─────────────┐
                     │     Bin     │
                     │  + QR Code  │
                     └──────┬──────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
        Disposal       Fill Reading     Waste Report
        Records             │
             │              ▼
             │         Prediction
             │
             ▼
        Collection
          Record
             │
             ▼
      Waste Aggregation
             │
       ┌─────┴─────┐
       ▼           ▼
   Recycling   Composting
```

---

# 16. Role-Based Usage

## Student

Can potentially:

- Scan bin QR
- View bin information
- Record disposal
- Report waste issues
- Use AI waste classification
- Earn points
- View leaderboard
- Redeem rewards

## Staff

Can potentially:

- Scan bin QR
- Record disposal
- Report issues
- Provide more detailed operational reports
- View relevant bin information

## Collector

Can potentially:

- Scan bin QR
- View current bin status
- Record fill level
- Record collection
- Record collected quantity
- Update collection information

## Admin

Can potentially:

- Manage users
- Manage locations
- Manage bins
- Manage QR assignments
- Review reports
- View collection/fill history
- View recycling/composting records
- View analytics
- Manage gamification
- Monitor AI/prediction data

**Important:** A foreign key to `users` does not itself guarantee that a referenced user has the correct role. Role authorization must be enforced by the backend/application layer.

---

# 17. Indexing Strategy

Indexes should be added for frequently queried fields after the base schema is created.

Recommended V1 indexes:

```sql
CREATE INDEX idx_bins_location_id
ON bins(location_id);

CREATE INDEX idx_bins_waste_type_id
ON bins(waste_type_id);

CREATE INDEX idx_disposal_records_user_id
ON disposal_records(user_id);

CREATE INDEX idx_disposal_records_bin_id
ON disposal_records(bin_id);

CREATE INDEX idx_disposal_records_recorded_at
ON disposal_records(recorded_at);

CREATE INDEX idx_waste_reports_bin_id
ON waste_reports(bin_id);

CREATE INDEX idx_waste_reports_status
ON waste_reports(status);

CREATE INDEX idx_bin_fill_readings_bin_time
ON bin_fill_readings(bin_id, recorded_at);

CREATE INDEX idx_collection_records_bin_time
ON collection_records(bin_id, collected_at);

CREATE INDEX idx_waste_classifications_created_at
ON waste_classifications(created_at);

CREATE INDEX idx_fill_predictions_bin_time
ON fill_predictions(bin_id, predicted_for);

CREATE INDEX idx_recycling_records_date
ON recycling_records(recycling_date);

CREATE INDEX idx_composting_records_date
ON composting_records(composting_date);

CREATE INDEX idx_user_points_user_time
ON user_points(user_id, earned_at);

CREATE INDEX idx_reward_redemptions_user
ON reward_redemptions(user_id);
```

These indexes should be treated as the initial strategy and adjusted after actual query patterns are known.

---

# 18. Updated Timestamp Trigger

`bins.updated_at` should automatically change whenever the row is updated.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_bins_updated_at
BEFORE UPDATE ON bins
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

# 19. Current V1 Table Count

The current planned schema contains **16 tables**:

| # | Table | Purpose |
|---|---|---|
| 1 | `roles` | User roles |
| 2 | `users` | User accounts |
| 3 | `locations` | Campus waste-generating locations |
| 4 | `waste_types` | Waste categories |
| 5 | `bins` | Physical bins and QR tokens |
| 6 | `disposal_records` | Digital disposal events |
| 7 | `waste_reports` | Reported waste/bin issues |
| 8 | `bin_fill_readings` | Historical fill levels |
| 9 | `collection_records` | Collection history |
| 10 | `waste_classifications` | AI image classifications |
| 11 | `fill_predictions` | AI fill predictions |
| 12 | `recycling_records` | Recycling activities |
| 13 | `composting_records` | Composting activities |
| 14 | `gamification_actions` | Point-earning actions |
| 15 | `user_points` | Point transactions |
| 16 | `rewards` / `reward_redemptions` | Reward catalogue and redemption history |

**Note:** The last row represents two tables, so the actual total is **17 tables** if both `rewards` and `reward_redemptions` are counted separately.

---

# 20. Future Extensions

The following are intentionally not part of the current V1 core schema but can be added later.

## Green Index

Can be implemented later using existing:

- Waste quantities
- Waste types
- Collection records
- Recycling records
- Composting records
- Locations

It should remain an optional analytics module rather than a dependency of the core system.

## IoT Smart Bins

The current `bin_fill_readings.source` field allows:

```text
MANUAL
IOT
ESTIMATED
```

A future IoT implementation can add device-specific tables if needed.

## Advanced AI Prediction

Future versions may add:

- Prediction features
- Model training metadata
- Prediction error metrics
- Multiple prediction targets
- Model experiment tracking

## Campaigns

Gamification can later be extended with dedicated campaign/event tables if DBIT requires structured sustainability campaigns.

---

# 21. V1 Design Philosophy

The database should remain:

- Relational
- Normalized
- Auditable
- History-oriented
- Easy to query
- Suitable for analytics
- Extensible for AI/IoT
- Simple enough for a student major project

Avoid introducing a table merely because a concept exists in the UI. Add a persistent table when the system needs to store a distinct entity, relationship, or historical event.

The central design is:

```text
Users
  ↓
Bins + QR
  ↓
Disposal / Reports / Fill Monitoring
  ↓
Collection
  ↓
Recycling / Composting
  ↓
Analytics + AI
  ↓
Gamification
```

This is the agreed **EcoSense PostgreSQL V1 Schema baseline**.
