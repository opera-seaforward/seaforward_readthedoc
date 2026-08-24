<!-- BANNER IMAGE GOES HERE -->
<!-- e.g. ![SEA-FORWARD](assets/banner.png) -->

# SEA-FORWARD

SEA-FORWARD (**S**imple **E**ducational **A**ccess for **For**ecast and **War**ning **D**evelopers) is a free, open-source toolkit that teaches you to build and run a
complete ocean forecasting system on your own computer — from raw input data
through to a validated 5-day forecast you can plot and interpret. SEA-FORWARD is based on the OPERA OCeanPrediction-A Architecture as described by the figure below.

<figure style="text-align: center; margin: 20px 0;">
  <img src="./img/SEA-FORWARD_Architecture.png" alt="Architecture" style="max-width: 100%; height: auto;">
  <figcaption style="font-size: 0.9em; color: #555; margin-top: 8px; font-style: italic;">
    Implementation of the OceanPrediction-A architecture for the SEA-FORWARD system. The system consists of two main components (UNIX/LINUX based system and Jupyter Notebooks) accessible via a GitHub Repository.
  </figcaption>
</figure>

The OceanPrediction-A architecture is functionally implemented within a downloadable workflow, hence locally accessible by the users. The SEA-FORWARD architecture diagram illustrates a system which consists of two main components:

* **UNIX/LINUX system**: Hosts the model and forecast systems elements, the test configurations along with storage capabilities.
* **Jupyter Notebooks**: Provide interface for output data analysis and visualization, the downstream tools, sensitivity tests and exercises.

The **GitHub repository** serves as version control and download interface for the tools listed above.

Users interact locally with the UNIX/LINUX system to set-up/compile/execute models and run forecasts; and then with the Jupyter Notebook to analyze simulation outputs, create visualizations and downstream services.

SEA-FORWARD is aimed at practitioners who understand oceanography but have not yet built
or operated a forecasting system. Every step is explicit and manual by design:
there is no automated installer, because the goal is not just to produce a
forecast — it is to understand each link in the chain that produces it.

No supercomputer is required. SEA-FORWARD runs on commodity hardware.

## What you will build

A complete forecasting chain following the **OceanPrediction-A**
blueprint of the OceanPrediction DCC Architecture:

**Upstream data → Ocean model → Validation → Visualization**

| Layer                       | Process            | In SEA-FORWARD                                                                                                       |
| --------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------- |
| Upstream Data (U)           | U2, U3, U4, U5, U7 | GFS atmospheric forcing, Dai river discharge, CMEMS ocean boundary conditions, ETOPO2 bathymetry, TPXO tidal forcing |
| Core Forecasting Engine (C) | C1                 | The CROCO v2.0 ocean model, compiled from source                                                                     |
| Verification & Analysis (V) | V1                 | Automated validation against a canonical reference run (RMSE, bias, spatial correlation)                             |
| Downstream Applications (D) | D1                 | Jupyter notebooks for SST, SSH, currents, MLD and salinity, with guided exercises                                    |

The forecasting strategy follows [Tchonang et al. (2024)](https://journals.ametsoc.org/view/journals/atot/41/6/JTECH-D-23-0112.1.xml): each cycle is initialized from the global 1/12° GLORYS12v1 reanalysis, integrated through a 2-day spin-up for dynamical adjustment, then run forward as a 5-day forecast — repeated every 2 days in a rolling cycle for continuous coverage.
![forecasting_scheme](./img/forecasting_scheme.png)

Every component in the documentation is cross-referenced to the
OceanPrediction DCC Architecture process it implements, so what you learn here
maps directly onto real operational systems.

## Regions

SEA-FORWARD ships with three contrasting African test configurations, chosen
because each poses a different forecasting challenge:

- **Canary Upwelling System** — one of the four major Eastern Boundary Upwelling
  Systems, driven by trade winds along Northwest Africa. Highly variable
  wind-driven coastal upwelling, mesoscale eddies and offshore filaments.
- **Inner Gulf of Guinea** — equatorial seasonal upwelling, sensitive to remote
  forcing from the Atlantic Niño and to coupled atmosphere-ocean feedbacks.
- **Agulhas Current System** — the strongest western boundary current in the
  Southern Hemisphere, with large-amplitude meanders, retroflection and ring
  shedding.

See the [region gallery](phase7/) for what is available today.
![sea_forward_test_cases](./img/SEA-FORWARD_test_cases.png)


|              | **Component Access**                                                                                                    |
| ------------ | ----------------------------------------------------------------------------------------------------------------------- |
| What you get | The full SEA-FORWARD repository: tools to fetch the model and data, prepare inputs, run forecasts, validate and analyse |
| Best for     | Learning how the system is actually built; running at full speed                                                        |

## Requirements at a glance

- **Minimum:** 4-core CPU, 8 GB RAM, 50 GB free disk
- **Comfortable:** 8-core CPU, 16 GB RAM — canonical run completes in under 30 minutes
- **OS:** Ubuntu 20.04+ (primary), CentOS 7+, macOS 12+; Windows via WSL2
- **You should know:** basic Linux and Python, and have a physical oceanography background
- **Time:** a user with that background should complete installation and a first run within one working day

Grids up to roughly 128×128 run comfortably on a standard laptop or desktop. Higher resolutions need a multicore machine.

## Where to start

!!! tip "New here?"
    Read this page, then go to **[Quickstart](quickstart/)** to get a forecast
    running with the least friction. Come back to Phase 1 when you want to build the full stack yourself.

| If you want to…                      | Go to                                            |
| ------------------------------------ | ------------------------------------------------ |
| Set up a machine from scratch        | [Phase 1 — Setup](phase1/01_setup.md)            |
| Configure a forecast                 | [Phase 2](phase2/02_forecast_config.md)          |
| Run forecasts, manually or automated | [Phase 3](phase3/03_forecast.md)                 |
| Build and run a hindcast             | [Phase 4](phase4/04_hindcast.md)                 |
| Post-process and validate results    | [Phase 5](phase5/05_postprocessing.md)           |
| Increase resolution with nesting     | [Phase 6](phase6/06_nesting.md)                  |
| Start from a ready-made region       | [Phase 7 — Region gallery](phase7/07_regions.md) |

## Context: the OPERA Capacity Development Activities

SEA-FORWARD is delivered under the **OPERA (Ocean Prediction Enhancement in Regions of Africa) Capacity Development Activities** — a 38-month initiative led by the **ICMPA-UNESCO Chair** (Université d'Abomey-Calavi, Benin) and the **Gulf of Guinea Ocean Sciences Summer School (GGOSSS)**.

OPERA is a five-year project implemented by **Mercator Ocean International**,
funded by the **European Union** as part of the **Arc X programme**, and framed
within the **OceanPrediction Decade Collaborative Centre (DCC)**. Its purpose is
to strengthen regional, pan-African and international cooperation for the
development of ocean forecasting systems, services and applications.

OPERA serves three audiences — the general public, intermediate-level
practitioners, and advanced-level developers — structured around the
OceanPrediction DCC _virtuous loop_, which moves through four thematic periods:

1. Fundamentals of Ocean Forecasting
2. Building an Ocean Forecasting System
3. Operating an Ocean Forecasting Service
4. Applications and Digital Twins

**SEA-FORWARD is the advanced-level entry point into that loop.** It deliberately
implements OceanPrediction-A — a single deterministic run without data
assimilation — because that exposes the full value chain without the added
complexity of observational ingestion or ensemble methods. The architecture
keeps clear hook points for future progression to OceanPrediction-B (data
assimilation) and for CROCO-AGRIF nesting.

## Partners

|                                 |                                                                                                                                      |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Project owner / implementer** | Mercator Ocean International                                                                                                         |
| **Funder**                      | European Union — Arc X programme                                                                                                     |
| **Lead institutions**           | ICMPA-UNESCO Chair, Université d'Abomey-Calavi (Benin); Gulf of Guinea Ocean Sciences Summer School (GGOSSS)                         |
| **Framework**                   | OceanPrediction Decade Collaborative Centre (DCC)                                                                                    |
| **Ocean model**                 | CROCO — Coastal and Regional Ocean COmmunity model                                                                                   |
| **Data sources**                | CMEMS, Copernicus Climate Data Store; Global Forecasting System (GFS); ETOPO2; TPXO Tides Atlas; Dai and Trenberth River Climatology |

## Learn more

- [OceanPrediction DCC Architecture Guide](https://doi.org/10.48670/oofsarchitecture) — Alvarez Fanjul et al. (2024).
- [ETOOFS Guide](https://www.unoceanprediction.org/en/resources/etoofs-guide)
- [Ocean Rating List (ORL) Guide](https://www.unoceanprediction.org/en/resources/orl)
- [CROCO Ocean Engine](https://www.croco-ocean.org/)
- [CF Conventions v1.8](https://cfconventions.org)

## Citing and licence

SEA-FORWARD is released under an open-source licence, with input data and reference results archived on Zenodo with permanent DOIs. See [LICENSE](https://github.com/) and the citation guidance in the repository.

<!-- TODO: replace with the real repository URL, licence name and DOI once issued -->
