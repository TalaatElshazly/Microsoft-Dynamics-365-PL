# Develop a plug-in that uses the execution context


Unit 2 establishes that Contoso's allowance check belongs in PreValidation and explains why that stage beats PreOperation for a check that only needs to say no early. This unit turns that stage decision into a working plug-in class, and shows how that class reads the Request record's data through the execution context.

## Implement IPlugin to run your logic in the pipeline

Every plug-in class you register with Dataverse implements the **`IPlugin`** interface. That interface defines a single method, `Execute(IServiceProvider serviceProvider)`, and Dataverse calls this method whenever a registered step for your class fires. Everything your plug-in does happens inside this one method.

Here's a minimal class that matches the allowance check from unit 2, registered as a PreValidation step on the Request table's Create message:

```csharp
public class ValidateRequestAllowance : IPlugin
{
    public void Execute(IServiceProvider serviceProvider)
    {
        IPluginExecutionContext context = (IPluginExecutionContext)
            serviceProvider.GetService(typeof(IPluginExecutionContext));

        Entity request = (Entity)context.InputParameters["Target"];

        if (request.Contains("cont_remainingallowance") &&
            request.GetAttributeValue<Money>("cont_remainingallowance").Value <= 0)
        {
            throw new InvalidPluginExecutionException(
                "This employee has no remaining allowance for a new request.");
        }
    }
}
```

The `serviceProvider` parameter is how `Execute` reaches everything it needs: the execution context, a tracing service, and the Organization service you explore in the next unit. Casting the Request entity out of `InputParameters["Target"]` gives the plug-in direct access to the exact row the employee is trying to save, before that save ever reaches the database.

## Keep your plug-in class stateless

Dataverse caches a single instance of your plug-in class and reuses it across many invocations, for many different users and requests, since creating a new instance every time would cost performance. That caching behavior is also why a plug-in class has to stay stateless: anything you store as a class-level field or property persists across every invocation that reuses the same cached instance.

As a result, one employee's Request data could leak into another employee's execution, or get overwritten mid-flight by a concurrent call. In practice, that means:

- **Keep request-specific objects inside `Execute`.** The context, the Organization service reference, the tracing service, and any request-specific row data belong there, never as fields on the class.
- **Class-level constants and stateless helpers are safe.** Anything that doesn't hold request-specific state is fine to keep at the class level, since it doesn't change between invocations.
- **Don't cache context, service, tracing, or row data in fields.** Treating `Execute` as the only place state lives keeps Contoso's plug-in safe to reuse under real production load.

## Choose IPlugin directly or build on PluginBase

Writing a class against `IPlugin` directly, as the example above does, works for any plug-in. Dataverse also offers an abstract **`PluginBase`** class, generated for you by the Power Platform Tools extension for Visual Studio or the `pac plugin init` Power Platform CLI command. `PluginBase` implements `IPlugin` and pre-wires the context and common services, so your `Execute` override starts with the context and services already resolved instead of you resolving them yourself.

`PluginBase` is a convenience, not a requirement. It's worth considering while you're writing your first few plug-ins, since it removes some repetitive setup code, but a class that implements `IPlugin` directly behaves identically once registered. Contoso's developers can mix both approaches across their solution without any conflict.

## Read the data your plug-in needs from the context

The execution context carries everything your plug-in needs to know about the operation it's running inside. The properties you reach for most often are:

| Property | What it holds | How Contoso's plug-in uses it |
| --- | --- | --- |
| `InputParameters` / `OutputParameters` | The request and response data for the operation, as key/value pairs | Reads the Request entity from `InputParameters["Target"]` before the save completes |
| `SharedVariables` | Data one plug-in step passes to a later step in the same pipeline execution; for a value set in PreValidation on Create, Update, or Delete, the later step reads it from `ParentContext.SharedVariables` | Lets a PreValidation step flag something a PostOperation step on the same Request retrieves through `ParentContext.SharedVariables` and acts on |
| `PreEntityImages` / `PostEntityImages` | Snapshots of the row before and after the operation | Carries the data unit 4 uses to compare a Request's values before and after an update |
| `Stage`, `MessageName`, `PrimaryEntityName` | What stage is running and what triggered it | Lets one class registered against several steps tell them apart |
| `Depth` | The current depth of execution in the call stack | Helps you spot potential re-entry when a plug-in update triggers more processing |
| `ParentContext` | Details about an outer operation, if another plug-in or workflow triggered this one | Shows whether a Request change ran because of something another plug-in already did |

All of these properties are read-only on the context object itself, but `InputParameters`, `OutputParameters`, and `SharedVariables` are mutable collections. Modifying what's inside them, rather than reassigning the property, is how a plug-in changes what the operation does next. `PreEntityImages` and `PostEntityImages` carry real data as soon as you register them, but how you register and work with images is a topic the next unit covers in depth.

> 
> **Reflect:** Based on what you've read, why shouldn't Contoso's plug-in class cache the Organization service reference in a class-level field? Which context property would you check first to confirm a Request's current status value before continuing?

## Guard against infinite loops with Depth

`Depth` exists because a plug-in can trigger another operation that, directly or indirectly, fires the same plug-in again. Dataverse increments `Depth` each time this happens and halts execution once it crosses an internal limit, which stops a runaway loop from consuming resources indefinitely. You should treat `Depth` as a safety net the platform manages, rather than a value your business logic reads or depends on. The exact number can change for reasons outside your plug-in's control.

## Reuse logic across steps with configuration data

A separate mechanism solves a different real-world problem: reusing the same compiled plug-in class across steps that need slightly different settings. A plug-in class can declare `unsecure` and `secure` string constructor parameters, and you supply values for each at registration time:

- **Unsecure configuration data** is visible to anyone who can view the step's registration.
- **Secure configuration data** is accessible only to administrators.

Contoso can use this to register the same allowance-checking class against multiple steps, each with a different allowance threshold passed in as configuration data, which avoids writing a near-duplicate class for every threshold.

With the class written and the context properties mapped to what Contoso's plug-in needs, the next unit builds on this foundation. It shows how pre-images and post-images carry a row's before-and-after values, and how the Organization service lets your plug-in perform additional operations as part of the same transaction.

Learn more about [writing a plug-in](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/write-plug-in) and [understanding the execution context](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/understand-the-data-context).
