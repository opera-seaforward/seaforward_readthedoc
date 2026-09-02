The Architecture Guide organises a forecasting service as a **value chain** that
flows from raw inputs to end users, and it distributes the work across three
roles. The whole of SEA-FORWARD sits inside this picture:

- **The system owner** runs the forecast on their own facility (a workstation, a
  server, or a cloud) and is responsible for producing the forecast and for its
  **interoperable output** — output that conforms to community standards so that
  others can use it without special knowledge of how it was made.
- **Intermediate users** take that interoperable output and build further products
  on it — indicators, derived fields, tailored services.
- **End users** consume the forecast or the derived products to make decisions.

In the architecture pattern SEA-FORWARD follows — the "system owner runs the
service, output is fully interoperable" pattern — the value chain runs
left-to-right through three zones: **upstream data**, the **system owner's
facility** (where the model runs), and the **downstream** services and users. The
diagram above is laid out in exactly those zones.