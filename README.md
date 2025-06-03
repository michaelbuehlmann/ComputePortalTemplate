# Compute Portal Template

![Flow Diagram](./flow_layout.svg)

This repository contains the folders / packages:
- ``endpoint``: Configuration of the LCF compute endpoints, codes that run on the endpoint, and compute functions. This folder is supposed to be installed and executed at the LCF facilities
- ``entrypoint``: Configuration of the "entrypoint" endpoint as well as entrypoint code and compute function. This endpoint should be set up outside the LCFs (for production, this is running on a CELS VM)
- ``flows``: Globus Flow and FlowAdapter definitions as well as some platform testing codes. This can be run anywhere; for setting up the adapters for the frontend, it makes sense to run it on the webserver system

See the README.md file in each of the subfolders for more information!

In addition, you will need the webserver repository, which you can find
[here](https://github.com/michaelbuehlmann/svelte-compute-portal).


## Development Setup Steps

1. **Create a new Globus Project** with 2 applications:
   - A "thick client" to communicate with the Globus API to setup flows, set
     group permissions, etc
   - A "science portal" under which the webserver will run

2. **Setup the compute endpoints**.
   Follow the instructions under ``endpoint``. You will set this up on
   ALCF/Polaris or NERSC/Perlmutter.

3. **Setup the entrypoint**.
   Follow the instructions under ``entrypoint``. Best to do this on a linux
   development machine, e.g. "astral-armadillo", "relativistic-rhino", ...

4. **Setup the Globus flow and test the setup**.
   Follow the instructions under ``flows``. You can run this anywhere. This
   step will install some test functions which you can run to verify setps 2 and
   3 were all successful. This step will also generate adapter files used in the
   next step

5. **Setup the web application**.
   Follow the installation instructions in the
   [svelte-compute-portal](https://github.com/michaelbuehlmann/svelte-compute-portal)
   repository. You can then add the adapters produced in the previous step with

   ```bash
   npm run addflow <path_to_adapter.json>
   ```

