The reference is not invented for this project. It is the **Ocean Forecasting
Architecture Guide** (OceanPrediction DCC, 2024; doi:10.48670/oofsarchitecture),
published by the **OceanPrediction Decade Collaborative Centre (OceanPrediction
DCC)** — a body hosted by Mercator Ocean International under the **UN Decade of
Ocean Science for Sustainable Development** — and prepared by the **Ocean
Forecasting Co-Design Team (OFCT)**, a group of experts assembled by the DCC to
analyse the state of ocean forecasting worldwide and design a shared architecture.

That guide is one of three that together define how to stand up an ocean-forecast
service — the OceanPrediction DCC calls it a *virtuous loop*:

| guide | question it answers | reference |
|---|---|---|
| **ETOOFS Guide** | the *theory* — how ocean forecasting works | Alvarez-Fanjul et al., 2022 |
| **Architecture Guide** | how to *build* a service — the components and the wiring | OFCT / OceanPrediction DCC, 2024 |
| **Operational Readiness Level (ORL) Guide** | how to *operate* it — best practices, maturity | OceanPrediction DCC |

SEA-FORWARD is a small, complete instance that touches all three: the ETOOFS
theory underlies CROCO and the forcing chain; the Architecture Guide describes the
shape of the system this chapter draws; and the ORL is the ladder SEA-FORWARD
climbs as it moves from a hand-built run toward a scheduled service.

**The problem the guide sets out to solve is worth stating, because SEA-FORWARD is a direct answer to it.** The guide observes that the most common architecture in operational ocean forecasting today is a *non-interoperable system running on the owner institution's own IT environment*, with three consequences: setup and operations are complex and duplicate effort for want of commonly agreed tools and standards; the output is not interoperable; and no shared standards are used acrossthe setup and operations phases. The Architecture Guide proposes an interoperable alternative — commonly agreed tools, shared standards, and interoperable output so that services are more robust, easier to maintain, and, crucially, easier for newcomer institutions to stand up. SEA-FORWARD is built to be exactly that kind of service: a reproducible system whose every stage uses standard tools and produces interoperable output, designed so an institution starting out can build it.

There is one more reason this framing is apt here. The DCC's capacity-development
programme is called **OPERA**, and its pilot focus is the **African marine
community**. SEA-FORWARD's repository is `opera-seaforward`: the system is
deliberately built to be the kind of reproducible, teachable service that OPERA
exists to spread.