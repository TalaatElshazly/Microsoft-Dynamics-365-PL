# Module assessment


## Check your knowledge

1. A developer registers a step that must cancel a Request save whenever an employee has no remaining allowance, and the check needs only data already included in the incoming request. Which event pipeline stage should the developer register the step on to cancel the operation as cheaply as possible?

   - [ ] PreOperation

   - [ ] PreValidation

   - [ ] PostOperation

2. A plug-in class stores the execution context as a private field so that a helper method can read it later in the same class. Why does this design cause problems in production?

   - [ ] The execution context can only be read once per plug-in assembly, so storing it as a field exhausts that single read.

   - [ ] Fields on a plug-in class are only visible to the Organization service, so a helper method in the same class couldn't read it anyway.

   - [ ] Dataverse caches and reuses a single instance of the plug-in class across many invocations, so a stored field can leak data between unrelated requests.

3. A PostOperation plug-in registered on the Update message needs to compare a column's value before the update with the value produced by the main operation. Which approach provides both values?

   - [ ] Register a pre-image and a post-image on the step, and compare the two aliases inside the plug-in.

   - [ ] Read the InputParameters collection twice, once before and once after calling the Organization service.

   - [ ] Increase the step's execution order so it runs after every other step on the same message.

4. A PostOperation plug-in needs to update a different table's row as part of the same transaction that triggered it. Which approach correctly accomplishes this from inside the plug-in?

   - [ ] Call the Dataverse Web API using an HTTP client, since the plug-in is already running with an authenticated context.

   - [ ] Add the other table's columns to the current step's filtering attributes so Dataverse updates them automatically.

   - [ ] Obtain an IOrganizationService instance from the IOrganizationServiceFactory and call its Update method.

5. While registering a plug-in assembly with the Plug-in Registration tool for a Dataverse (online) environment, which isolation mode and location should a developer choose?

   - [ ] None isolation mode with the assembly stored on the server's disk.

   - [ ] Sandbox isolation mode with the assembly stored in the database.

   - [ ] Sandbox isolation mode with the assembly stored in the global assembly cache (GAC).
