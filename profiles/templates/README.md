# Introduction to Supercomputing

### Welcome

Welcome to the **Introduction to Supercomputing** course.

This training provides a practical overview of how modern supercomputers operate, how to run applications efficiently, and how to use the {{system.display_name}} system at SURF. The aim is to give you the essential concepts and hands-on experience needed to work productively on HPC systems for your research.

The course is typically divided into three four-hour sessions, each focusing on a different aspect of supercomputing. Throughout the course you will work with hands-on exercises designed to reinforce the concepts and help you build confidence using HPC systems in practice.

We hope you find the training useful, and we welcome any feedback to help us improve future editions.

## Agenda

### **Part I — Fundamentals of HPC**
**Modules:**
- Fundamentals of HPC

### **Part II — Working with the {{system.display_name}} environment**
**Modules:**  
- {{system.display_name}} file systems
- QCG PilotJob

### **Part III — Performance and hybrid jobs**
**Modules:**  
- Performance analysis
- Slurm hybrid jobs

> [!NOTE]
> {{course_cluster.course.cluster_note}}

## Classroom source

Use the audited fork while upstream changes are under review:

```bash
git clone --branch course/maastricht-20261028 --single-branch \
  https://github.com/HaoZeke/introduction-to-supercomputing.git \
  "$HOME/introduction-to-supercomputing-class"
```

Open the course Open OnDemand portal from the welcome note and use Clusters
for a terminal. The [browser setup guide](https://supersurf.rgoswami.me/setup)
explains sign-in, Files, the shell and optional interactive applications.

## Cluster profiles

Render all supported clusters with:

```bash
python3 tools/render_profile.py --all
```

The output is written under `build/<profile>/`. Trainers can follow
[`profiles/README.md`](profiles/README.md) to add and verify another cluster.
