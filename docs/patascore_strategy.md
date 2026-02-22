# PataSCORE: Alternative Data Credit Scoring System

## Task 6: Credit Scoring Using Alternative Data Sources for Financial Inclusion

---

## 1. Overview

### 1.1 The Problem

Over 1.7 billion adults worldwide remain unbanked. In Kenya alone, approximately 17 million adults lack access to formal credit -- not because they are uncreditworthy, but because traditional credit bureaus (CRB) have no data on them. These individuals have never held a bank account, never taken a formal loan, and have no credit file.

Yet these same individuals transact daily through M-Pesa, pay for electricity through M-KOPA, buy airtime, and engage in measurable economic activity. Their financial footprint exists -- it is simply invisible to traditional scoring systems.

### 1.2 The PataSCORE Concept

**PataSCORE** (from Swahili *pata* -- "to find/discover") is an alternative credit scoring system that discovers creditworthiness from non-traditional data sources. It is designed for the East African market, with Kenya as the primary deployment target.

**Core thesis:** A borrower's likelihood of repaying a loan can be reliably predicted from their mobile money behavior, utility payment history, device usage patterns, and digital economic activity -- even in the complete absence of traditional credit bureau data.

### 1.3 Design Principles

1. **Inclusion-first:** Score anyone with a mobile phone and 90 days of transaction history
2. **Explainable:** Every score component can be traced to specific data signals
3. **Fair:** Actively monitor and mitigate bias across gender, geography, and socioeconomic segments
4. **Privacy-preserving:** Minimize data collection; process locally where possible; comply with Kenya Data Protection Act 2019
5. **Actionable:** Provide lenders with a score, confidence interval, and recommended loan parameters

---

## 2. Alternative Data Sources

### 2.1 Data Source Overview

[![PataSCORE Data Sources](https://img.shields.io/badge/View_Diagram-Excalidraw-6965db)](https://excalidraw.com/#json=NZK7pCrNK68K5V8wg_o-J,MsYPZ1XpB3PArk9Xwshj4A)

<img width="1520" height="1130" alt="image" src="https://github.com/user-attachments/assets/a606e9b4-fcfb-4c22-84e3-480e658a78de" />


> **[Open interactive diagram](https://excalidraw.com/#json=NZK7pCrNK68K5V8wg_o-J,MsYPZ1XpB3PArk9Xwshj4A)** — 6 data sources: Mobile Money (15 features, 35-40%), Utility Payments (5, 10-15%), Device & Behavioral (7, 15-20%), E-Commerce (5, 5-10%), Social Media (4, 5%), GPS & Location (5, 10-15%) → ~41 total features across 3 scoring tiers

### 2.2 Source 1: Mobile Money Transactions (M-Pesa, Airtel Money)

**Data access:** Safaricom Daraja API, Airtel Money API, or direct M-Pesa statement parsing (as currently implemented in Credit Pulse).

**Raw signals:**
- Transaction timestamps, amounts, counterparties
- Balance history over time
- Transaction types (P2P, merchant, bill pay, cash-in/out)
- M-Shwari, KCB M-Pesa, and Fuliza usage

**Engineered features:**

| Feature                        | Calculation                                              | Credit Signal                          |
|--------------------------------|----------------------------------------------------------|----------------------------------------|
| `income_stability_cv`         | CV of monthly inflows over 6 months                      | Low variance = stable income           |
| `savings_ratio`               | (Inflows - Outflows) / Inflows, monthly average          | Positive = surplus income              |
| `velocity_trend`              | Linear regression slope of weekly transaction count      | Increasing = growing economic activity |
| `inflow_outflow_ratio`        | Total received / Total sent (30-day rolling)             | > 1.0 suggests net positive cash flow  |
| `betting_spend_ratio`         | Betting outflows / Total outflows                        | High ratio = risk indicator            |
| `utility_payment_consistency` | Stddev of days between utility payments                  | Low = consistent bill payer            |
| `fuliza_dependency_ratio`     | Fuliza usage days / Active days                          | High = frequent overdraft usage        |
| `merchant_diversity`          | Count of distinct merchant till numbers                  | High = diverse economic activity       |
| `late_night_txn_ratio`        | Transactions between 11PM-5AM / Total transactions       | High = potential risk signal           |
| `salary_deposit_detected`     | Binary: regular large inflows on consistent dates        | 1 = likely formal employment           |
| `balance_recovery_speed`      | Avg days to return to pre-withdrawal balance             | Fast = strong cash flow resilience     |
| `p2p_network_score`           | PageRank of customer in P2P transaction graph            | High = central economic node           |

### 2.3 Source 2: Utility Payment History

**Data access:** KPLC (Kenya Power) API, Nairobi Water, Safaricom postpaid billing, DSTV/GOtv subscription records.

**Raw signals:**
- Payment amounts and dates
- Account status (active, suspended, disconnected)
- Consumption levels (kWh for electricity, liters for water)
- Prepaid vs postpaid classification

**Engineered features:**

| Feature                        | Calculation                                              | Credit Signal                          |
|--------------------------------|----------------------------------------------------------|----------------------------------------|
| `utility_payment_streak`      | Consecutive months with on-time payment                  | Long streak = reliability              |
| `utility_amount_trend`        | 6-month trend of utility payment amounts                 | Increasing = growing household         |
| `disconnection_count`         | Number of service disconnections in 12 months            | High = payment distress                |
| `prepaid_topup_frequency`     | Electricity/water prepaid top-up frequency               | Regular = disciplined consumption      |
| `utility_to_income_ratio`     | Monthly utility spend / Estimated monthly income         | Reasonable ratio = financial stability |

### 2.4 Source 3: Device and Behavioral Data

**Data access:** With user consent, via Android app permissions or device fingerprinting SDK (e.g., Tala, Branch-style).

**Raw signals:**
- Device make, model, price tier
- Number of installed applications
- App categories (finance, education, gaming)
- Phone contact list size (anonymized count only)
- Call/SMS frequency patterns
- Battery charging patterns
- Screen-on time distribution

**Engineered features:**

| Feature                        | Calculation                                              | Credit Signal                          |
|--------------------------------|----------------------------------------------------------|----------------------------------------|
| `device_value_tier`           | Device retail price mapped to 1-5 tier                   | Higher tier correlates with income     |
| `finance_app_count`           | Count of banking/finance/investment apps                  | High = financially engaged             |
| `contact_list_size_bucket`    | Contacts bucketed: <50, 50-200, 200-500, 500+            | Larger network = social stability      |
| `communication_regularity`    | CV of daily call/SMS counts over 30 days                 | Low CV = routine lifestyle             |
| `gaming_app_ratio`            | Gaming apps / Total apps                                 | Contextual risk signal                 |
| `phone_age_months`            | Months since device activation                           | Older = device retention = stability   |
| `daily_usage_consistency`     | Stddev of daily screen-on hours                          | Consistent = stable routine            |

### 2.5 Source 4: Social Media Signals

**Data access:** OAuth-consented access to public profile data. Privacy-first approach: metadata only, never content analysis.

**Raw signals:**
- Account age and verification status
- Connection/follower count
- Profile completeness score
- Business page or professional profile indicators
- LinkedIn employment verification (where available)

**Engineered features:**

| Feature                        | Calculation                                              | Credit Signal                          |
|--------------------------------|----------------------------------------------------------|----------------------------------------|
| `social_account_age_months`   | Age of oldest social media account                       | Longer = identity stability            |
| `profile_completeness_score`  | % of profile fields filled (photo, bio, location, etc.)  | Higher = identity commitment           |
| `professional_network_flag`   | Has LinkedIn with employment history                     | 1 = verifiable professional identity   |
| `social_verification_count`   | Number of verified accounts (Twitter, Facebook, etc.)    | More = stronger identity               |

**Important constraints:** Social media data is used only for identity verification and stability signals, never for content-based profiling (which would violate privacy regulations and introduce unacceptable bias).

### 2.6 Source 5: E-Commerce and Digital Payments

**Data access:** Jumia, Kilimall, Glovo Kenya purchase history (with user consent), MPESA Lipa Na M-Pesa merchant records.

**Raw signals:**
- Purchase frequency and amounts
- Product categories
- Return/refund rates
- Digital subscription maintenance (Netflix, Spotify, YouTube Premium)
- Buy-now-pay-later usage and repayment

**Engineered features:**

| Feature                        | Calculation                                              | Credit Signal                          |
|--------------------------------|----------------------------------------------------------|----------------------------------------|
| `ecommerce_purchase_freq`    | Average monthly purchases                                | Regular purchasing = economic activity |
| `avg_order_value`            | Mean transaction amount                                  | Spending capacity indicator            |
| `subscription_maintenance`   | Months of continuous digital subscription payments       | Long = consistent discretionary spend  |
| `bnpl_repayment_rate`        | % of BNPL installments paid on time                      | Direct credit behavior signal          |
| `refund_request_ratio`       | Refunds / Total purchases                                | High = potential fraud indicator       |

### 2.7 Source 6: GPS and Location Data

**Data access:** With explicit consent, periodic GPS pings from mobile app (similar to Tala, Branch models).

**Raw signals:**
- Home location (most frequent nighttime location)
- Work location (most frequent daytime location, weekdays)
- Location stability over time
- Proximity to economic centers

**Engineered features:**

| Feature                        | Calculation                                              | Credit Signal                          |
|--------------------------------|----------------------------------------------------------|----------------------------------------|
| `home_location_stability`     | Months at same nighttime location cluster                | Stable = residential permanence        |
| `has_distinct_work_location`  | Binary: consistent daytime location != home              | 1 = likely employed                    |
| `economic_zone_score`         | GDP per capita of home county / National average         | Area-level income proxy                |
| `commute_regularity`          | CV of daily first-movement time                          | Low = regular work schedule            |
| `location_diversity_score`    | Entropy of visited location clusters in 30 days          | Higher = wider economic activity       |

---

## 3. Feature Engineering Pipeline

### 3.1 Feature Processing Architecture

[![Feature Processing Architecture](https://img.shields.io/badge/View_Diagram-Excalidraw-6965db)](https://excalidraw.com/#json=ggVSJ-OyYlPJVrx1wGey6,AmS6WerByiVGxgJfUTxZQg)

<img width="1160" height="1260" alt="image" src="https://github.com/user-attachments/assets/25f9185e-8ca3-480f-a34a-c5b01053f67b" />


> **[Open interactive diagram](https://excalidraw.com/#json=ggVSJ-OyYlPJVrx1wGey6,AmS6WerByiVGxgJfUTxZQg)** — Raw Data Sources → Feature Extraction (per-source ETL) → Feature Store (Redis + DynamoDB, 6 namespaces) → Feature Assembly (join by customer_id, ~41 features) → Training (batch) + Serving (real-time)

### 3.2 Feature Categories and Weights

| Category              | Feature Count | Typical Weight in Model | Data Availability |
|-----------------------|---------------|-------------------------|-------------------|
| Mobile Money          | 15            | 35-40%                  | Very High (90%+)  |
| Utility Payments      | 5             | 10-15%                  | High (70%)        |
| Device & Behavioral   | 7             | 15-20%                  | Medium (50%)      |
| E-Commerce            | 5             | 5-10%                   | Low (30%)         |
| Social Media          | 4             | 5%                      | Medium (40%)      |
| GPS/Location          | 5             | 10-15%                  | Medium (45%)      |
| **Total**             | **~41**       | **100%**                |                   |

### 3.3 Handling Missing Data Sources

Not every applicant will have all six data sources. PataSCORE uses a **tiered scoring approach:**

- **Tier 1 (Mobile Money only):** Minimum viable score. Requires 90+ days of M-Pesa history. Produces a score with wider confidence interval.
- **Tier 2 (Mobile Money + Utility):** Improved accuracy with utility payment signals.
- **Tier 3 (3+ sources):** Full-confidence score with narrow confidence interval.

```python
def determine_score_tier(available_sources: set) -> int:
    """Determine scoring tier based on available data sources."""
    if "mobile_money" not in available_sources:
        raise InsufficientDataError("Mobile money data is required for scoring")

    source_count = len(available_sources)
    if source_count >= 3:
        return 3  # Full confidence
    elif "utility" in available_sources:
        return 2  # Enhanced
    else:
        return 1  # Basic
```

The model is trained separately for each tier, so a Tier 1 score is calibrated against the performance of other Tier 1 borrowers -- not penalized for missing data.

---

## 4. Model Architecture

### 4.1 Ensemble Design

PataSCORE uses a **stacked ensemble** combining gradient boosting and a neural network, each with distinct strengths:

[![Ensemble Model Architecture](https://img.shields.io/badge/View_Diagram-Excalidraw-6965db)](https://excalidraw.com/#json=FGqOHeBuC8QWS9kNjHaVC,3JF0YQOYv8i1VxX9JAhL2A)

<img width="1320" height="1310" alt="image" src="https://github.com/user-attachments/assets/4ade52f9-9075-4656-8bd7-c402ba9eec72" />


> **[Open interactive diagram](https://excalidraw.com/#json=FGqOHeBuC8QWS9kNjHaVC,3JF0YQOYv8i1VxX9JAhL2A)** — Input Features (~41) → LightGBM + Neural Network (dual base models) → Meta-Learner (Logistic Regression with score_tier + data_completeness) → Final P(default) → PataSCORE (300-850)

### 4.2 LightGBM Component

```python
import lightgbm as lgb

gbm_params = {
    "objective": "binary",
    "metric": "auc",
    "boosting_type": "gbdt",
    "num_leaves": 63,
    "learning_rate": 0.05,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "min_child_samples": 50,
    "scale_pos_weight": n_negative / n_positive,  # Handle class imbalance
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "n_estimators": 500,
    "early_stopping_rounds": 50,
    "verbose": -1,
}

# LightGBM natively handles missing values (NaN) by learning
# optimal split directions for missing data -- critical for
# PataSCORE where many features may be absent.
model_gbm = lgb.LGBMClassifier(**gbm_params)
model_gbm.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)],
)
```

### 4.3 Neural Network Component

```python
import torch
import torch.nn as nn

class PataScoreNet(nn.Module):
    """Feed-forward network for alternative credit scoring."""

    def __init__(self, n_numeric: int, n_categorical: int,
                 cat_cardinalities: list, embed_dim: int = 8):
        super().__init__()

        # Categorical embeddings (e.g., device_tier, county, score_tier)
        self.embeddings = nn.ModuleList([
            nn.Embedding(card, embed_dim) for card in cat_cardinalities
        ])
        total_embed = n_categorical * embed_dim

        input_dim = n_numeric + total_embed

        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.1),

            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x_numeric, x_categorical):
        embeds = [emb(x_categorical[:, i]) for i, emb in enumerate(self.embeddings)]
        x = torch.cat([x_numeric] + embeds, dim=1)
        return self.network(x).squeeze()
```

### 4.4 Meta-Learner (Stacking)

```python
from sklearn.linear_model import LogisticRegression
import numpy as np

# Out-of-fold predictions from base models
oof_gbm = cross_val_predict(model_gbm, X, y, cv=5, method="predict_proba")[:, 1]
oof_nn = get_nn_oof_predictions(model_nn, X, y, cv=5)

# Meta-features
meta_features = np.column_stack([
    oof_gbm,
    oof_nn,
    X["score_tier"].values,
    X["data_completeness"].values,  # % of non-null features
])

meta_learner = LogisticRegression(C=1.0)
meta_learner.fit(meta_features, y)
```

---

## 5. Scoring Methodology

### 5.1 Score Scale: 300-850

PataSCORE maps the model's predicted probability of default to a 300-850 scale, designed to be familiar to lenders already using FICO-like systems while calibrated for the Kenyan market.

```python
import numpy as np

def probability_to_patascore(p_default: float, tier: int) -> int:
    """
    Convert default probability to PataSCORE (300-850).

    The transformation uses a log-odds mapping with tier-specific
    calibration to ensure scores are comparable across tiers.
    """
    # Clip to avoid log(0) or log(inf)
    p_default = np.clip(p_default, 0.001, 0.999)

    # Log-odds (higher log-odds of NON-default = higher score)
    log_odds = np.log((1 - p_default) / p_default)

    # Linear mapping: log_odds range [-6.9, 6.9] -> score range [300, 850]
    # Calibrated so that 50% default probability = 575 (midpoint)
    base_score = 575
    pdo = 40  # Points to double the odds

    score = base_score + (pdo / np.log(2)) * log_odds

    # Tier-based confidence adjustment
    tier_adjustment = {1: 0, 2: 0, 3: 0}  # No tier penalty in the score itself
    score += tier_adjustment.get(tier, 0)

    return int(np.clip(round(score), 300, 850))
```

### 5.2 Score Bands and Recommended Actions

| Score Range | Band         | Est. Default Rate | Recommended Action                          |
|-------------|--------------|-------------------|---------------------------------------------|
| 750 - 850   | Excellent    | < 2%              | Approve up to KES 100K, lowest rate         |
| 700 - 749   | Good         | 2% - 5%           | Approve up to KES 50K, standard rate        |
| 650 - 699   | Fair         | 5% - 10%          | Approve up to KES 20K, moderate rate        |
| 550 - 649   | Below Fair   | 10% - 20%         | Approve up to KES 10K, higher rate          |
| 450 - 549   | Poor         | 20% - 35%         | Small loans only (KES 2-5K), highest rate   |
| 300 - 449   | Very Poor    | > 35%             | Decline or require guarantor                |

### 5.3 Score Output Format

```json
{
  "customer_id": "CPK-2024-00847",
  "patascore": 692,
  "score_band": "Fair",
  "score_tier": 2,
  "confidence_interval": [671, 713],
  "default_probability": 0.078,
  "data_sources_used": ["mobile_money", "utility"],
  "data_completeness": 0.62,
  "score_components": {
    "mobile_money_subscore": 71,
    "utility_subscore": 68,
    "device_subscore": null,
    "social_subscore": null,
    "ecommerce_subscore": null,
    "location_subscore": null
  },
  "recommended_loan_limit_kes": 20000,
  "recommended_interest_tier": "moderate",
  "top_positive_factors": [
    "Consistent monthly M-Pesa inflows for 8+ months",
    "Regular KPLC payments with no disconnections",
    "Low betting expenditure ratio (< 2%)"
  ],
  "top_negative_factors": [
    "Below-average savings ratio",
    "Limited transaction history (4 months)"
  ],
  "scored_at": "2026-02-22T14:30:00Z",
  "model_version": "patascore-v1.2"
}
```

### 5.4 Confidence Intervals

The confidence interval narrows as more data sources are available:

| Tier | Data Sources | Typical CI Width | Example              |
|------|-------------|------------------|----------------------|
| 1    | 1 source    | +/- 40 points     | 680 [640, 720]       |
| 2    | 2 sources   | +/- 25 points     | 680 [655, 705]       |
| 3    | 3+ sources  | +/- 15 points     | 680 [665, 695]       |

Confidence intervals are computed using bootstrap resampling during model training, stored as percentile-based lookup tables indexed by predicted probability and tier.

---

## 6. Privacy and Ethical Considerations

### 6.1 Regulatory Compliance

PataSCORE must comply with:

- **Kenya Data Protection Act, 2019 (DPA):** Kenya's primary data protection legislation, modeled after the EU's GDPR. Enforced by the Office of the Data Protection Commissioner (ODPC).
- **Central Bank of Kenya (CBK) Prudential Guidelines:** Regulations on credit information sharing and scoring.
- **Consumer Protection Act, 2012:** Requirements for fair treatment and transparency in financial services.

### 6.2 Data Protection Principles (DPA 2019 Alignment)

| DPA Principle                  | PataSCORE Implementation                                        |
|--------------------------------|-----------------------------------------------------------------|
| **Lawful processing**          | Explicit opt-in consent before any data collection              |
| **Purpose limitation**         | Data used solely for credit scoring; no secondary use           |
| **Data minimization**          | Collect only features needed for scoring, not raw content       |
| **Accuracy**                   | Regular data refresh cycles; dispute resolution mechanism       |
| **Storage limitation**         | Raw data deleted after feature extraction; features retained 24 months max |
| **Integrity & confidentiality**| AES-256 encryption at rest; TLS 1.3 in transit; SOC 2 compliance |
| **Accountability**             | Data Protection Impact Assessment (DPIA) before launch          |

### 6.3 Consent Framework

[![Consent Flow](https://img.shields.io/badge/View_Diagram-Excalidraw-6965db)](https://excalidraw.com/#json=WZ1Ulq5Ok2TfG5SjfK-Bg,S4MgPPbTDDkz73ClMIR4uw)

> **[Open interactive diagram](https://excalidraw.com/#json=WZ1Ulq5Ok2TfG5SjfK-Bg,S4MgPPbTDDkz73ClMIR4uw)** — 5-step DPA 2019 consent flow: Open loan application → Clear disclosure → Granular consent toggles (M-Pesa required, KPLC/Device/Location optional) → Accept/Decline decision → Store consent receipt + timestamp. User can revoke at any time.

### 6.4 Bias Monitoring and Fairness

PataSCORE must not discriminate based on protected characteristics. Active monitoring includes:

**Protected groups:**
- Gender (male vs female)
- Geography (urban vs rural, county-level)
- Age group
- Device tier (as a proxy for socioeconomic status)

**Fairness metrics computed monthly:**

```python
def compute_fairness_metrics(scores_df, protected_col, outcome_col):
    """Compute disparate impact and equalized odds metrics."""
    groups = scores_df[protected_col].unique()

    # Approval rate parity (scores >= 550)
    approval_rates = {}
    for group in groups:
        group_df = scores_df[scores_df[protected_col] == group]
        approval_rates[group] = (group_df["patascore"] >= 550).mean()

    # Disparate impact ratio (4/5ths rule)
    max_rate = max(approval_rates.values())
    min_rate = min(approval_rates.values())
    disparate_impact = min_rate / max_rate if max_rate > 0 else 0

    # Equalized odds: TPR and FPR should be similar across groups
    tpr_by_group = {}
    fpr_by_group = {}
    for group in groups:
        group_df = scores_df[scores_df[protected_col] == group]
        approved = group_df["patascore"] >= 550
        actual_default = group_df[outcome_col] == 1

        tp = ((approved) & (~actual_default)).sum()
        fn = ((~approved) & (~actual_default)).sum()
        fp = ((approved) & (actual_default)).sum()
        tn = ((~approved) & (actual_default)).sum()

        tpr_by_group[group] = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr_by_group[group] = fp / (fp + tn) if (fp + tn) > 0 else 0

    return {
        "approval_rates": approval_rates,
        "disparate_impact_ratio": disparate_impact,  # Must be >= 0.8
        "tpr_by_group": tpr_by_group,
        "fpr_by_group": fpr_by_group,
    }
```

**Remediation actions if bias is detected:**
1. Feature audit: identify which features drive disparate impact
2. Reweighting: adjust training sample weights to equalize outcomes
3. Threshold adjustment: set group-specific approval thresholds to equalize opportunity
4. Feature removal: drop features that are proxies for protected characteristics with no genuine predictive value

### 6.5 Explainability Requirements

Every PataSCORE decision must be explainable to both the lender and the borrower:

- **Lender view:** Full feature importance breakdown, SHAP values, score components by data source
- **Borrower view:** Plain-language top 3 positive and top 3 negative factors (e.g., "Your consistent M-Pesa savings pattern positively impacts your score")
- **Regulatory view:** Full model documentation, training data statistics, fairness reports

```python
import shap

def explain_score(model, features, feature_names):
    """Generate SHAP-based explanation for a single prediction."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(features)

    # Sort by absolute SHAP value
    feature_impacts = sorted(
        zip(feature_names, shap_values[0]),
        key=lambda x: abs(x[1]),
        reverse=True
    )

    positive_factors = [
        (name, val) for name, val in feature_impacts if val < 0  # Lower default prob
    ][:3]

    negative_factors = [
        (name, val) for name, val in feature_impacts if val > 0  # Higher default prob
    ][:3]

    return {
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "full_shap_values": dict(zip(feature_names, shap_values[0].tolist())),
    }
```

### 6.6 Data Retention and Right to Erasure

```
Data Lifecycle:
-------------------------------------------------
Raw data (M-Pesa statements, etc.)
  -> Processed within 24 hours
  -> Raw data deleted after feature extraction
  -> Only aggregated features retained

Feature vectors
  -> Retained for 24 months (regulatory requirement for credit decisions)
  -> Automatically purged after retention period
  -> Customer can request early deletion (right to erasure)

Score history
  -> Retained for 36 months (CBK requirement)
  -> Anonymized after 36 months for model improvement
```

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Months 1-4)

**Objective:** Launch PataSCORE with mobile money data only (Tier 1 scoring).

```
Month 1-2: Data & Infrastructure
---------------------------------------------
- [ ] Integrate with Safaricom Daraja API for M-Pesa data access
- [ ] Build consent management system (DPA 2019 compliant)
- [ ] Deploy feature extraction pipeline for mobile money
- [ ] Set up secure data storage (encrypted DynamoDB + Redis)
- [ ] Conduct Data Protection Impact Assessment (DPIA)

Month 3: Model Development
---------------------------------------------
- [ ] Engineer 15 mobile money features (from Section 2.2)
- [ ] Train LightGBM model on historical loan performance data
- [ ] Calibrate 300-850 score scale
- [ ] Validate on holdout set: target AUC > 0.72
- [ ] Implement SHAP-based explainability

Month 4: Launch & Validation
---------------------------------------------
- [ ] Deploy scoring API (FastAPI + ONNX)
- [ ] Shadow-score 10,000 applicants alongside existing process
- [ ] Measure concordance with traditional scoring where overlap exists
- [ ] Launch Tier 1 scoring for partner lenders in pilot
- [ ] Initial fairness audit (gender, geography)
```

**Phase 1 success criteria:**
- AUC > 0.72 on out-of-sample test set
- Disparate impact ratio > 0.8 across gender and urban/rural
- P99 scoring latency < 200ms
- 10,000+ borrowers scored in pilot

### Phase 2: Enrichment (Months 5-8)

**Objective:** Add utility and device data sources; launch Tier 2 and Tier 3 scoring.

```
Month 5-6: Data Source Integration
---------------------------------------------
- [ ] Integrate KPLC API for electricity payment history
- [ ] Build device fingerprinting SDK (Android)
- [ ] Implement granular consent UI for additional data sources
- [ ] Deploy feature extraction pipelines for utility + device data

Month 7: Model Enhancement
---------------------------------------------
- [ ] Engineer utility (5) and device (7) features
- [ ] Train ensemble model (LightGBM + Neural Network)
- [ ] Implement stacking meta-learner with tier-aware calibration
- [ ] Retrain on expanded dataset: target AUC > 0.78
- [ ] Add confidence intervals per tier

Month 8: Production Rollout
---------------------------------------------
- [ ] A/B test Tier 2/3 scores against Tier 1 for same borrowers
- [ ] Measure incremental lift from additional data sources
- [ ] Scale to 50,000+ monthly scorings
- [ ] Automated fairness monitoring pipeline
- [ ] Monthly model performance reports for CBK compliance
```

**Phase 2 success criteria:**
- AUC > 0.78 for Tier 2/3 borrowers
- Measurable reduction in default rates for lender partners
- 50% of scored borrowers have Tier 2+ scores
- Automated monthly fairness reports

### Phase 3: Scale and Intelligence (Months 9-12)

**Objective:** Add remaining data sources, real-time scoring, and adaptive models.

```
Month 9-10: Full Data Integration
---------------------------------------------
- [ ] Integrate e-commerce purchase data (Jumia, digital payments)
- [ ] Add GPS/location features with privacy-preserving aggregation
- [ ] Social media verification signals (OAuth-based)
- [ ] Implement real-time streaming pipeline (Kafka + PySpark)
- [ ] Deploy to Kubernetes with auto-scaling

Month 11-12: Advanced Capabilities
---------------------------------------------
- [ ] Implement automated model retraining triggered by drift detection
- [ ] Launch score simulator: "How would my score change if I..."
- [ ] Build lender dashboard with portfolio-level analytics
- [ ] Implement P2P network graph scoring (PageRank on transaction graph)
- [ ] Sequence model (LSTM) for transaction pattern analysis
- [ ] Publish PataSCORE methodology whitepaper for transparency
- [ ] Apply for CBK approval as a registered credit scoring provider
```

**Phase 3 success criteria:**
- AUC > 0.82 for Tier 3 borrowers
- Real-time scoring with P99 < 50ms
- 200,000+ monthly scorings
- Measurable impact on financial inclusion (new-to-credit borrowers approved)
- CBK registration application submitted

---

## 8. Expected Impact on Financial Inclusion

### 8.1 The Inclusion Gap

Traditional credit scoring in Kenya relies on Credit Reference Bureau (CRB) data, which covers only individuals who have previously accessed formal credit. This creates a catch-22: you cannot get credit without a credit history, and you cannot build a credit history without credit.

**Current state in Kenya:**
- ~21 million CRB-listed individuals (out of ~33 million adults)
- ~12 million adults with no CRB record whatsoever
- Rural populations, women, and youth disproportionately excluded
- Informal sector workers (60%+ of workforce) largely invisible to traditional scoring

### 8.2 PataSCORE's Addressable Population

| Segment                          | Population (Est.) | Traditional Score? | PataSCORE Coverage |
|----------------------------------|-------------------|--------------------|---------------------|
| Banked with CRB history          | 14M               | Yes                | Yes (enhanced)      |
| Banked without CRB history       | 7M                | Partial            | Yes                 |
| M-Pesa only (no bank account)    | 8M                | No                 | Yes                 |
| Feature phone M-Pesa users       | 4M                | No                 | Tier 1 only         |
| **Total addressable**            | **33M**            | **14M (42%)**      | **29M (88%)**       |

### 8.3 Projected Impact (Year 1)

| Metric                                    | Estimate          |
|-------------------------------------------|-------------------|
| New-to-credit borrowers scored            | 500,000+          |
| Previously declined borrowers now approved | 15-25% of scored  |
| Average loan size for new-to-credit       | KES 5,000 - 15,000|
| Estimated default rate (Tier 1 borrowers) | 8-12%             |
| Estimated default rate (Tier 3 borrowers) | 4-7%              |
| Reduction in lender default rate vs no-score | 30-40%          |

### 8.4 Social and Economic Benefits

1. **Entrepreneurship:** Small traders and jua kali (informal sector) workers can access working capital loans based on their M-Pesa cash flow, enabling business growth without collateral.

2. **Gender equity:** Women in Kenya are more likely to use M-Pesa for savings and utility payments but less likely to have formal credit histories. PataSCORE's mobile money and utility features can help close the gender credit gap.

3. **Rural access:** Rural borrowers who transact primarily through M-Pesa agents gain access to credit scoring without needing to visit a bank branch or have formal employment documentation.

4. **Youth inclusion:** Young adults (18-25) who have grown up on mobile money but have no credit history can begin building a PataSCORE from day one of their economic activity.

5. **Poverty reduction:** Access to affordable micro-credit -- rather than predatory informal lending -- enables productive investment and consumption smoothing during income shocks.

### 8.5 Responsible Lending Safeguards

PataSCORE is a tool for inclusion, not predation. Safeguards include:

- **Loan amount caps** tied to demonstrated cash flow (not just score)
- **Cooling-off periods** for borrowers who show signs of over-indebtedness
- **Mandatory affordability checks** that prevent lending beyond 30% of estimated monthly income
- **Transparent score factors** so borrowers understand and can improve their scores
- **Score improvement pathways** communicated to declined applicants (e.g., "Pay your KPLC bill on time for 3 months to improve your score")

---

## 9. Technical Architecture Summary

[![PataSCORE System Architecture](https://img.shields.io/badge/View_Diagram-Excalidraw-6965db)](https://excalidraw.com/#json=NTl0Wc0x1kbfa6CwkzZWj,rF-k_Opq-mL8k88bqx6CHA)

> **[Open interactive diagram](https://excalidraw.com/#json=NTl0Wc0x1kbfa6CwkzZWj,rF-k_Opq-mL8k88bqx6CHA)** — 5-layer architecture: Data Layer (Daraja API, KPLC, Device SDK, OAuth, E-Commerce) → Processing (Feature Extraction, Consent Manager, Data Quality) → Storage (Feature Store, Score History) → Model (LightGBM + Neural Network + Meta-Learner) → Serving (Scoring API, SHAP Explainability, Fairness Monitor) → Lender APIs

---

## 10. Conclusion

PataSCORE represents a paradigm shift from "credit history required" to "economic activity sufficient." By harnessing the rich digital footprint that Kenyans already generate through mobile money, utility payments, and smartphone usage, PataSCORE can extend creditworthiness assessment to the 12+ million Kenyan adults currently invisible to traditional credit bureaus.

The system is designed to be:

- **Technically sound:** Ensemble models achieving AUC > 0.78, with ONNX serving at sub-50ms latency
- **Ethically responsible:** SHAP explainability, automated fairness monitoring, DPA 2019 compliance
- **Commercially viable:** Incremental data sources improve accuracy while the base Tier 1 score requires only M-Pesa data
- **Socially impactful:** Projected 500,000+ new-to-credit borrowers scored in Year 1

Financial inclusion is not just about giving people access to credit -- it is about giving lenders the confidence to say yes to people they previously could not evaluate. PataSCORE provides that confidence.
