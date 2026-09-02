The Architecture Guide organises a forecasting service as a **value chain** flowing from
raw inputs to end users, with the work distributed across three roles. The whole of
SEA-FORWARD sits inside this picture:

- **The system owner** runs the forecast on their own facility — a workstation, a
  server, or a cloud — and is responsible for producing the forecast and for its
  **interoperable output**: output conforming to community standards, so others can use
  it without special knowledge of how it was made.
- **Intermediate users** take that output and build further products on it — indicators,
  derived fields, tailored services.
- **End users** consume the forecast or the derived products to make decisions.

SEA-FORWARD follows the guide's "system owner runs the service" pattern, in which the
value chain runs left to right through three zones: **upstream data**, the **system
owner's facility** where the model runs, and the **downstream** services and users. The
architecture diagram on the overview page is laid out in exactly those zones, and the
next page walks through each component in turn.