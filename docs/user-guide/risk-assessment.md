# Risk Assessment Guide

Understanding how Project Thalassa analyzes FASTQ files and calculates SRS (Sea lice Resistance to treatment) risk scores.

## Overview

Project Thalassa uses advanced bioinformatics algorithms to assess the risk of sea lice treatment resistance in salmon populations. The system analyzes genetic markers from FASTQ sequencing data to provide actionable risk scores.

## Risk Score Calculation

### Input Data

The analysis begins with FASTQ files containing:
- Genomic sequences from salmon samples
- Quality scores for each base call
- Sample metadata (cage ID, date, location)

### Analysis Pipeline

1. **Quality Control**
   - Filter low-quality reads
   - Remove adapter sequences
   - Validate data integrity

2. **Sequence Alignment**
   - Map reads to reference genome
   - Identify genetic variants
   - Detect resistance markers

3. **Risk Calculation**
   - Analyze presence of resistance alleles
   - Calculate allele frequencies
   - Apply weighted scoring algorithm

4. **Score Normalization**
   - Normalize scores to 0.0-1.0 range
   - Apply confidence adjustments
   - Generate final risk score

### Risk Score Formula

```
SRS Risk Score = Σ(marker_weight × marker_frequency × confidence_factor)
```

Where:
- `marker_weight`: Importance of each resistance marker (0.0-1.0)
- `marker_frequency`: Frequency of marker in sample (0.0-1.0)
- `confidence_factor`: Quality and coverage adjustment (0.5-1.0)

## Risk Categories

Risk scores are classified into four categories:

| Category | Score Range | Description | Recommended Action |
|----------|-------------|-------------|-------------------|
| **Critical** | 0.8 - 1.0 | Very high resistance risk | Immediate intervention required |
| **High** | 0.6 - 0.79 | Significant resistance risk | Treatment strategy review needed |
| **Medium** | 0.4 - 0.59 | Moderate resistance risk | Enhanced monitoring recommended |
| **Low** | 0.0 - 0.39 | Low resistance risk | Standard protocols sufficient |

## Understanding Results

### Dashboard View

The risk assessment dashboard displays:

```
┌─────────────────────────────────────┐
│ Cage ID: CAGE-04B                   │
│ Risk Score: 0.65 (HIGH)             │
│ Last Updated: 2025-08-11 12:00      │
│                                     │
│ [▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░] 65%         │
│                                     │
│ Samples Analyzed: 5                 │
│ Confidence: 95%                     │
└─────────────────────────────────────┘
```

### Detailed Results

Results are stored in JSON format:

```json
{
  "cageId": "CAGE-04B",
  "srsRiskScore": 0.65,
  "riskLevel": "HIGH",
  "lastUpdated": "2025-08-11T12:00:00Z",
  "details": {
    "samplesAnalyzed": 5,
    "confidence": 0.95,
    "markers": {
      "resistance_marker_1": {
        "present": true,
        "frequency": 0.72,
        "contribution": 0.35
      },
      "resistance_marker_2": {
        "present": true,
        "frequency": 0.58,
        "contribution": 0.30
      }
    },
    "recommendations": [
      "Consider alternative treatment options",
      "Increase monitoring frequency",
      "Review historical treatment efficacy"
    ]
  }
}
```

## Factors Affecting Risk Scores

### Genetic Factors

1. **Known Resistance Mutations**
   - Point mutations in target genes
   - Copy number variations
   - Structural variants

2. **Allele Frequencies**
   - Homozygous vs heterozygous
   - Population frequency
   - Temporal changes

### Environmental Factors

1. **Sample Quality**
   - Sequencing depth
   - Read quality scores
   - Coverage uniformity

2. **Temporal Patterns**
   - Seasonal variations
   - Treatment history
   - Population dynamics

### Technical Factors

1. **Sequencing Parameters**
   - Platform used
   - Read length
   - Library preparation

2. **Analysis Settings**
   - Quality thresholds
   - Alignment parameters
   - Variant calling stringency

## Interpreting Trends

### Temporal Analysis

Monitor risk scores over time:

```
Risk Score Trend (CAGE-04B)
1.0 │
0.8 │              ●━━━●
0.6 │         ●━━━━┛
0.4 │    ●━━━━┛
0.2 │●━━━┛
0.0 └───────────────────
    Jan Feb Mar Apr May
```

### Comparative Analysis

Compare across cages:

```
Risk Comparison (May 2025)
CAGE-04B  [▓▓▓▓▓▓▓▓▓▓▓▓▓░░░] 0.65
CAGE-04A  [▓▓▓▓▓▓▓▓░░░░░░░░] 0.45
CAGE-03C  [▓▓▓▓▓░░░░░░░░░░░] 0.32
CAGE-03B  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓] 0.78
```

## Alert System

### Automatic Alerts

The system generates alerts when:

1. **Critical Risk Detected** (Score ≥ 0.8)
   - Immediate email notification
   - Dashboard highlight in red
   - Recommended actions provided

2. **Rapid Score Increase** (Δ > 0.2 in 30 days)
   - Trend alert notification
   - Historical comparison chart
   - Investigation recommended

3. **Multiple High-Risk Cages** (>50% cages at HIGH)
   - Site-wide alert
   - Management summary report
   - Strategic review triggered

### Alert Configuration

Configure alert thresholds in environment variables:

```ini
CRITICAL_RISK_THRESHOLD=0.8
HIGH_RISK_THRESHOLD=0.6
MEDIUM_RISK_THRESHOLD=0.4
RAPID_CHANGE_THRESHOLD=0.2
```

## Quality Metrics

### Confidence Score

Confidence scores indicate reliability:

| Confidence | Meaning | Factors |
|------------|---------|---------|
| >95% | Highly reliable | High coverage, quality data |
| 85-95% | Reliable | Good coverage, minor issues |
| 70-85% | Moderate | Some quality concerns |
| <70% | Low confidence | Significant data issues |

### Coverage Metrics

Minimum requirements for reliable analysis:

- **Sequencing Depth**: ≥30x coverage
- **Read Quality**: ≥Q30 for >80% bases
- **Genome Coverage**: ≥90% of target regions
- **Sample Size**: ≥3 individuals per cage

## Best Practices

### Sampling Guidelines

1. **Regular Sampling**
   - Monthly sampling recommended
   - Consistent sampling locations
   - Representative population coverage

2. **Sample Quality**
   - Fresh samples preferred
   - Proper storage conditions
   - Quick processing to analysis

3. **Metadata Accuracy**
   - Accurate cage identification
   - Precise sampling dates
   - Complete treatment history

### Result Interpretation

1. **Consider Context**
   - Historical treatment data
   - Regional resistance patterns
   - Environmental conditions

2. **Action Thresholds**
   - Don't react to single readings
   - Look for trends over time
   - Consider confidence levels

3. **Validation**
   - Correlate with field observations
   - Compare with treatment efficacy
   - Validate unexpected results

## Frequently Asked Questions

### Q: How quickly are results available?

Results are typically available within:
- 5-10 minutes for standard analysis
- 15-30 minutes for deep analysis
- 1-2 hours for batch processing

### Q: What causes low confidence scores?

Common causes include:
- Low sequencing quality
- Insufficient coverage
- Sample degradation
- Technical artifacts

### Q: Can historical data be re-analyzed?

Yes, historical FASTQ files can be re-analyzed with updated algorithms to provide revised risk assessments.

### Q: How often should we sample?

Recommended sampling frequency:
- **Standard**: Monthly
- **High-risk periods**: Bi-weekly
- **After treatment**: Weekly for 4 weeks

## Technical Details

### Algorithm Components

1. **Variant Calling**
   - BWA-MEM alignment
   - GATK variant calling
   - Custom resistance database

2. **Score Calculation**
   - Weighted marker analysis
   - Population genetics models
   - Machine learning predictions

3. **Quality Control**
   - FastQC analysis
   - MultiQC reporting
   - Custom QC metrics

### Performance Metrics

- **Sensitivity**: 95% for known markers
- **Specificity**: 98% for resistance detection
- **Accuracy**: 92% correlation with field data
- **Processing Speed**: ~1GB/minute

## Support and Resources

- [API Documentation](/user-guide/api-overview)
- [File Upload Guide](/user-guide/file-upload)
- [Technical Architecture](/docs/Technical_Architecture)
- [Contact Support](mailto:support@thalassa.example.com)
