# Feature Specification

## Chronic Health Risk Prediction

### Input Features

| Feature | Description | Input Type |
|---|---|---|
| HighBP | High blood pressure indicator | Yes/No |
| HighChol | High cholesterol indicator | Yes/No |
| BMI | Body Mass Index | Numeric |
| Smoker | Smoking indicator | Yes/No |
| PhysActivity | Physical activity indicator | Yes/No |
| GenHlth | Self-rated general health (1–5) | Numeric |
| Age | Age category | Numeric |
| Sex | Sex | Categorical |

### Target

`Diabetes_012`

Target classes:

- `0` = No diabetes
- `1` = Prediabetes
- `2` = Diabetes

---

## Mental Health Risk Prediction

### Input Features

All 21 DASS-21 question responses:

- Q3_1_S1
- Q3_2_S2
- Q3_3_S3
- Q3_4_S4
- Q3_5_S5
- Q3_6_S6
- Q3_7_S7
- Q3_8_A1
- Q3_9_A2
- Q3_10_A3
- Q3_11_A4
- Q3_12_A5
- Q3_13_A6
- Q3_14_A7
- Q3_15_D1
- Q3_16_D2
- Q3_17_D3
- Q3_18_D4
- Q3_19_D5
- Q3_20_D6
- Q3_21_D7

Additional inputs:

- Age
- Gender

### Target

`mental_risk_category`

Target classes:

- `Low`
- `Moderate`
- `High`

### Important

The following computed scores are NOT used as model input features:

- `stress_score`
- `anxiety_score`
- `depression_score`

These scores are calculated from the DASS-21 responses and are used to create the target category.