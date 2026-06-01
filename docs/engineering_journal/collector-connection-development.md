## 2026-05-30 - 1
### Problem
Trade event logging generated excessive logs and buried important messages.

### Root Cause
Each trade event was logged individually.

### Solution
Replaced per-event logging with aggregated metrics and periodic summaries.

### Lessons Learned
High-frequency systems require metric aggregation rather than event-level logging.

---------------------------------
## 2026-05-30 - 2
### Problem
Logs are only shown in terminal and destoyed when terminal shuts down 

### Root Cause
Using only StreamHandler logger

### Solution
Console Handler  +  Rotating File Handler 

### Lessons Learned
Losing logs leads to not knowing what happened when we need to know

---------------------------------
## 2026-05-30 - 3
### Problem
Generic exceptions 

### Root Cause
not using proper exception handlers 

### Solution
Categorizing exceptions

### Lessons Learned
not handling exceptions in a categorized way creates a debugging hell not knowing exactly what happened

---------------------------------
## 2026-05-30 - 4
### Problem
Infinite retries without signaling critical failures 

### Root Cause
not having proper monitoring 

### Solution
adding critical logs on too many failures


### Lessons Learned
Monitoring is a fundamental part of a good system 
----------------------------------
## 2026-06-01

### problem 
Using file rotator with a new file each flush at storing raw data leads to a complete chaos 

### Root couse 
Storage strategi 

### solution 
Using data flush strategy with date partitioning. 

### lesson learned 
Every decision must consider having huge amout of data effects. 